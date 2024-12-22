# scripts/train_model.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.ml.model import FraudDetectionModel

def train_initial_model():
    print("Initializing fraud detection model...")
    model = FraudDetectionModel()
    
    print("Generating dummy training data...")
    X, y = model.generate_dummy_data(n_samples=1000)
    
    print("Training model...")
    model.train(X, y)
    
    print("Model training complete!")

if __name__ == "__main__":
    train_initial_model()
