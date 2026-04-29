import json
import random
from pathlib import Path
from statistics import mean, pstdev


OUTPUT_PATH = Path(__file__).with_name("model_config.json")
TRAINING_SAMPLES = 1500


def generate_normal_sample():
    temperature = random.uniform(20.0, 35.0)
    humidity = random.uniform(30.0, 70.0)

    temperature = random.uniform(temperature - 0.5, temperature + 0.5)
    humidity = random.uniform(humidity - 0.5, humidity + 0.5)

    return round(temperature, 2), round(humidity, 2)


def build_model():
    temperatures = []
    humidities = []

    random.seed(326)

    for _ in range(TRAINING_SAMPLES):
        temp, hum = generate_normal_sample()
        temperatures.append(temp)
        humidities.append(hum)

    return {
        "profile": {
            "name": "esp32-s3-sim-stat-v1",
            "algorithm": "statistical-thresholding",
            "training_samples": TRAINING_SAMPLES,
            "features": ["temperature", "humidity"],
            "target_device": "ESP32-S3 simulation",
        },
        "stats": {
            "temperature": {
                "mean": round(mean(temperatures), 4),
                "std": round(pstdev(temperatures), 4),
            },
            "humidity": {
                "mean": round(mean(humidities), 4),
                "std": round(pstdev(humidities), 4),
            },
        },
        "thresholds": {
            "temperature_min": 19.0,
            "temperature_max": 36.0,
            "humidity_min": 29.0,
            "humidity_max": 71.0,
            "score_threshold": 2.6,
        },
    }


if __name__ == "__main__":
    model = build_model()
    OUTPUT_PATH.write_text(json.dumps(model, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
