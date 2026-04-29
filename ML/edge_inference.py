import json
from pathlib import Path


MODEL_PATH = Path(__file__).with_name("model_config.json")


def load_model():
    with MODEL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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

        if value > 10**15:
            return None

        return value

    return None


def z_score(value, mean, std_dev):
    safe_std = std_dev if std_dev > 0 else 1.0
    return abs(value - mean) / safe_std


def infer_anomaly(model, temp, hum):
    stats = model["stats"]
    thresholds = model["thresholds"]

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
        "model_profile": model["profile"],
    }


def model_diagnostics(model):
    config_bytes = MODEL_PATH.stat().st_size
    memory_limit_bytes = get_memory_limit_bytes()
    estimated_model_bytes = len(json.dumps(model).encode("utf-8"))

    return {
        "memoryLimitBytes": memory_limit_bytes,
        "configBytes": config_bytes,
        "estimatedModelBytes": estimated_model_bytes,
        "pythonImplementation": "statistical-thresholding",
        "esp32SimulationNote": (
            "Runtime uses only a tiny JSON config and simple arithmetic so the inference path "
            "stays compatible with an ESP32-style memory budget."
        ),
    }


def run_self_test(model):
    normal_case = infer_anomaly(model, 27.5, 49.5)
    anomaly_case = infer_anomaly(model, 42.0, 60.0)

    return {
        "status": "ok",
        "normalCase": normal_case,
        "anomalyCase": anomaly_case,
        "passed": (not normal_case["anomaly"]) and anomaly_case["anomaly"],
    }
