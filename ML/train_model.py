import json
import random
from pathlib import Path
from statistics import mean, pstdev


OUTPUT_PATH = Path(__file__).with_name("model_config.json")
TRAINING_SAMPLES = 1800
NORMAL_RANGE = {
    "temperature_min": 19.0,
    "temperature_max": 36.0,
    "humidity_min": 29.0,
    "humidity_max": 71.0,
}


def generate_normal_sample():
    temperature = random.uniform(20.0, 35.0)
    humidity = random.uniform(30.0, 70.0)

    temperature = random.uniform(temperature - 0.5, temperature + 0.5)
    humidity = random.uniform(humidity - 0.5, humidity + 0.5)

    return round(temperature, 2), round(humidity, 2)


def generate_anomaly_sample():
    temperature, humidity = generate_normal_sample()

    if random.random() < 0.5:
        temperature += random.uniform(10.0, 18.0)
    else:
        humidity += random.uniform(10.0, 18.0)

    return round(temperature, 2), round(humidity, 2)


def percentile(values, ratio):
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(ratio * (len(ordered) - 1))))
    return ordered[index]


def build_model():
    temperatures = []
    humidities = []
    normal_scores = []

    random.seed(326)

    for _ in range(TRAINING_SAMPLES):
        temp, hum = generate_normal_sample()
        temperatures.append(temp)
        humidities.append(hum)

    temp_mean = mean(temperatures)
    hum_mean = mean(humidities)
    temp_std = pstdev(temperatures) or 1.0
    hum_std = pstdev(humidities) or 1.0

    for temp, hum in zip(temperatures, humidities):
        temp_z = abs(temp - temp_mean) / temp_std
        hum_z = abs(hum - hum_mean) / hum_std
        normal_scores.append(max(temp_z, hum_z, (temp_z + hum_z) / 2))

    score_threshold = round(percentile(normal_scores, 0.98), 4)

    # Ensure the threshold does not become too permissive for obvious spikes.
    score_threshold = min(max(score_threshold, 2.4), 3.1)

    validation_examples = {
        "normal": list(generate_normal_sample()),
        "anomaly": list(generate_anomaly_sample()),
    }

    return {
        "profile": {
            "name": "esp32-s3-sim-stat-v2",
            "algorithm": "statistical-thresholding",
            "training_samples": TRAINING_SAMPLES,
            "features": ["temperature", "humidity"],
            "target_device": "ESP32-S3 simulation",
            "runtime_class": "tiny-config",
        },
        "stats": {
            "temperature": {
                "mean": round(temp_mean, 4),
                "std": round(temp_std, 4),
            },
            "humidity": {
                "mean": round(hum_mean, 4),
                "std": round(hum_std, 4),
            },
        },
        "thresholds": {
            **NORMAL_RANGE,
            "score_threshold": score_threshold,
        },
        "validation_examples": validation_examples,
    }


if __name__ == "__main__":
    model = build_model()
    OUTPUT_PATH.write_text(json.dumps(model, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
