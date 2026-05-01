from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import pandas as pd

class ModelTrainer:
    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )

    def train(self, X_train, y_train):
        """Fits the model on the training data."""
        print("Training Random Forest Classifier...")
        self.model.fit(X_train, y_train)
        print("Training complete.")

    def evaluate(self, X_test, y_test):
        """Evaluates the model on test data and prints metrics."""
        print("Evaluating the model...")
        y_pred = self.model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        print(f"\nAccuracy: {acc * 100:.2f}%")
        
        print("\nConfusion Matrix:")
        print(pd.DataFrame(confusion_matrix(y_test, y_pred)))
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return y_pred, acc

    def save_model(self, filepath):
        """Saves the trained model to disk."""
        joblib.dump(self.model, filepath)
        print(f"Model saved to {filepath}")


if __name__ == "__main__":
    from ML.standalone_model.data_loader import DataLoader
    from ML.standalone_model.preprocessor import Preprocessor
    
    loader = DataLoader()
    data = loader.load_data()
    
    preprocessor = Preprocessor()
    X_train, X_test, y_train, y_test = preprocessor.process(data)
    
    trainer = ModelTrainer(n_estimators=50)
    trainer.train(X_train, y_train)
    trainer.evaluate(X_test, y_test)
