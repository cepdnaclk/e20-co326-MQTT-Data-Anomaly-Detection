import json
import os
from pathlib import Path

from flask import Flask, jsonify, request


app = Flask(__name__)

MODEL_PATH = Path(__file__).with_name("model_config.json")


def load_model():
    with MODEL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


MODEL = load_model()


def get_memory_limit_bytes():
    cgroup_candidates = [
        "/sys/fs/cgroup/memory.max",
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",
    ]

    for candidate in cgroup_candidates:
        try:
            raw_value = Path(candidate).read_text(encoding="utf-8").strip()
        except OSError:
            continue

        if raw_value == "max":
            return None

        try:
            value = int(raw_value)
        except ValueError:
            continue

        # Ignore obviously unbounded fallback values.
        if value > 10**15:
            return None

        return value

    return None


def z_score(value, mean, std_dev):
    safe_std = std_dev if std_dev > 0 else 1.0
    return abs(value - mean) / safe_std


def infer_anomaly(temp, hum):
    stats = MODEL["stats"]
    thresholds = MODEL["thresholds"]

    temp_z = z_score(temp, stats["temperature"]["mean"], stats["temperature"]["std"])
    hum_z = z_score(hum, stats["humidity"]["mean"], stats["humidity"]["std"])

    outside_hard_range = (
        temp < thresholds["temperature_min"]
        or temp > thresholds["temperature_max"]
        or hum < thresholds["humidity_min"]
        or hum > thresholds["humidity_max"]
    )

    anomaly_score = max(
        4.0 if outside_hard_range else 0.0,
        temp_z,
        hum_z,
        (temp_z + hum_z) / 2,
    )
    anomaly = outside_hard_range or anomaly_score >= thresholds["score_threshold"]

    return {
        "anomaly": anomaly,
        "anomaly_score": round(anomaly_score, 4),
        "features": {
            "temperature_z": round(temp_z, 4),
            "humidity_z": round(hum_z, 4),
        },
        "model_profile": MODEL["profile"],
    }


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}

    try:
        temp = float(payload["temp"])
        hum = float(payload["hum"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "temp and hum must be numeric"}), 400

    result = infer_anomaly(temp, hum)
    return jsonify(result)


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model": MODEL["profile"]["name"],
            "memoryLimitBytes": get_memory_limit_bytes(),
            "configBytes": MODEL_PATH.stat().st_size,
        }
    )


@app.get("/model-info")
def model_info():
    return jsonify(
        {
            "profile": MODEL["profile"],
            "thresholds": MODEL["thresholds"],
            "memoryLimitBytes": get_memory_limit_bytes(),
            "pythonImplementation": "statistical-thresholding",
            "esp32SimulationNote": (
                "This container uses a very small config-only model and a low memory cap "
                "to approximate an ESP32-friendly inference profile."
            ),
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
