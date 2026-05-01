from ML.standalone_model.setup import MODEL_DIR
from ML.standalone_model.data_loader import DataLoader
from ML.standalone_model.preprocessor import Preprocessor
from ML.standalone_model.trainer import ModelTrainer

def run_pipeline():
    print("--- Starting Standalone ML Pipeline ---")
    
    # 1. Load Data
    loader = DataLoader()
    data = loader.load_data()
    loader.describe_data()
    
    # 2. Preprocess
    print("\n--- Preprocessing ---")
    preprocessor = Preprocessor()
    X_train, X_test, y_train, y_test = preprocessor.process(data)
    print(f"Train samples: {X_train.shape[0]}")
    print(f"Test samples: {X_test.shape[0]}")
    
    # 3. Train
    print("\n--- Training ---")
    trainer = ModelTrainer(n_estimators=100)
    trainer.train(X_train, y_train)
    
    # 4. Evaluate
    print("\n--- Evaluation ---")
    trainer.evaluate(X_test, y_test)
    
    # 5. Save Model
    print("\n--- Saving ---")
    model_path = MODEL_DIR / 'rf_model.pkl'
    trainer.save_model(model_path)
    
    print("\n--- Pipeline Completed Successfully ---")


if __name__ == "__main__":
    run_pipeline()
