import pandas as pd
from ML.standalone_model.setup import DATA_PATH

class DataLoader:
    def __init__(self, filepath=DATA_PATH):
        self.filepath = filepath
        self.data = None

    def load_data(self):
        """Loads the dataset from the specified path."""
        print(f"Loading data from {self.filepath}...")
        try:
            self.data = pd.read_csv(self.filepath)
            print("Data loaded successfully.")
            return self.data
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def describe_data(self):
        """Prints a brief summary of the dataset."""
        if self.data is not None:
            print("Dataset Shape:", self.data.shape)
            print("\nClass Distribution:")
            print(self.data['label'].value_counts(normalize=True))
        else:
            print("No data loaded. Call load_data() first.")

if __name__ == "__main__":
    loader = DataLoader()
    df = loader.load_data()
    loader.describe_data()
