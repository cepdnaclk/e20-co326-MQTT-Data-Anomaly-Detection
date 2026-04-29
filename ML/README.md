# ML Runtime Notes

This folder now contains two different ML paths:

## 1. Edge-style runtime path

Files:

- `app.py`
- `edge_inference.py`
- `model_config.json`
- `train_model.py`
- `requirements.txt`

Purpose:

- Simulate an `ESP32-S3` friendly inference flow
- Keep runtime memory small
- Avoid heavy ML libraries inside the running container
- Use simple arithmetic and a tiny JSON configuration instead of a large pickled model

Runtime behavior:

- `POST /predict` returns `anomaly`, `anomaly_score`, feature z-scores, and model profile
- `GET /health` reports model bytes and container memory limit
- `GET /model-info` reports thresholds and edge-simulation details
- `GET /self-test` validates one normal case and one anomaly case

## 2. Offline cloud experimentation path

Files:

- `brain.py`
- `data_preprocessing.py`
- `model_train.py`
- `full_model.pkl`
- `embedded_system_network_security_dataset.csv`
- `requirements-train.txt`

Purpose:

- Preserve the heavier experimentation work already done in this repo
- Keep XGBoost / Isolation Forest training available without forcing those dependencies into the runtime image

## Recommendation

For the assignment demo, use the lightweight runtime container as the simulated edge model and describe the heavier files as offline experimentation, not as the deployed ESP32 path.
