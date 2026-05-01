import joblib
import pandas as pd
from ML.standalone_model.setup import MODEL_DIR

class StandalonePredictor:
    def __init__(self, model_path=MODEL_DIR / 'rf_model.pkl'):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """Loads a pre-trained model from disk."""
        try:
            self.model = joblib.load(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise

    def predict(self, feature_array):
        """
        Runs inference on given data.
        :param feature_array: pandas DataFrame or 2D NumPy array of preprocessed features.
        :return: Array of predictions.
        """
        if self.model is None:
            raise ValueError("Model is not loaded. Call load_model() first.")
        
        predictions = self.model.predict(feature_array)
        return predictions


if __name__ == "__main__":
    import numpy as np
    
    # Just a mock prediction to test the script
    print("Testing predictor logic...")
    predictor = StandalonePredictor()
    # Assume model is not saved yet, this will fail if ran independently without training first
    try:
        predictor.load_model()
        dummy_input = np.random.rand(1, 16)  # Mock 16 features
        result = predictor.predict(dummy_input)
        print("Prediction result:", result)
    except Exception as e:
        print("Expected error if model not trained yet:", e)
