# scripts/train_fraud_model.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.ml.preprocessing.preprocessor import FraudDataPreprocessor
from src.ml.training.trainer import FraudModelTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_fraud_model(data_path: str):
    try:
        # Initialize components
        preprocessor = FraudDataPreprocessor()
        trainer = FraudModelTrainer()
        
        # Prepare data
        logger.info("Preparing training data...")
        X, y = preprocessor.prepare_training_data(data_path)
        
        # Train model
        logger.info("Training model...")
        model = trainer.train_model(X, y)
        
        logger.info("Training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    data_path = "data/creditcard.csv"
    train_fraud_model(data_path)
