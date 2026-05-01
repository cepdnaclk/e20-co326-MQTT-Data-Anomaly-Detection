import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class Preprocessor:
    def __init__(self, target_column='label'):
        self.target_column = target_column
        self.scaler = StandardScaler()

    def process(self, df):
        """Preprocesses the DataFrame by splitting features/target, scaling, and train-test splits."""
        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in DataFrame.")

        # Drop NaNs
        df = df.dropna()

        # Separate Features and Target
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]

        # Convert booleans to ints if they exist
        X = X.astype(float)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test

if __name__ == "__main__":
    from ML.standalone_model.data_loader import DataLoader
    
    loader = DataLoader()
    data = loader.load_data()
    
    preprocessor = Preprocessor()
    X_train, X_test, y_train, y_test = preprocessor.process(data)
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
