from flask import Flask, jsonify, request


app = Flask(__name__)


def is_anomaly(temp, hum):
    return temp < 19 or temp > 36 or hum < 29 or hum > 71


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}

    try:
        temp = float(payload["temp"])
        hum = float(payload["hum"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "temp and hum must be numeric"}), 400

    return jsonify({"anomaly": is_anomaly(temp, hum)})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
