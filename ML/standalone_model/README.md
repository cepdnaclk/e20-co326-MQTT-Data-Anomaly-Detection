# Standalone ML Model

This is a standalone, disconnected Random Forest machine learning pipeline for the 'embedded_system_network_security_dataset.csv'.
It is decoupled from external Docker containers.

## Structure
- `requirements-standalone.txt`: Standalone pip requirements.
- `setup.py`: Configuration and base paths.
- `data_loader.py`: Simple utility to ingest the dataset.
- `preprocessor.py`: Implements features scaling and train/test splits.
- `trainer.py`: Random Forest implementation with performance evaluation.
- `inference.py`: Exposes a predictor API to use the trained `.pkl` model.
- `main.py`: Ties everything together to train, evaluate, and save the model.

## Usage
Simply run:
```bash
pip install -r requirements-standalone.txt
python main.py
```
This will train the model on the CSV and save `rf_model.pkl` in this directory.
