import os

from flask import Flask, jsonify, request

from edge_inference import (
    infer_anomaly,
    load_model,
    model_diagnostics,
    run_self_test,
)


app = Flask(__name__)
MODEL = load_model()


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}

    try:
        temp = float(payload["temp"])
        hum = float(payload["hum"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "temp and hum must be numeric"}), 400

    return jsonify(infer_anomaly(MODEL, temp, hum))


@app.get("/health")
def health():
    diagnostics = model_diagnostics(MODEL)
    return jsonify(
        {
            "status": "ok",
            "model": MODEL["profile"]["name"],
            "memoryLimitBytes": diagnostics["memoryLimitBytes"],
            "configBytes": diagnostics["configBytes"],
            "estimatedModelBytes": diagnostics["estimatedModelBytes"],
        }
    )


@app.get("/model-info")
def model_info():
    diagnostics = model_diagnostics(MODEL)
    diagnostics["profile"] = MODEL["profile"]
    diagnostics["thresholds"] = MODEL["thresholds"]
    return jsonify(diagnostics)


@app.get("/self-test")
def self_test():
    return jsonify(run_self_test(MODEL))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
