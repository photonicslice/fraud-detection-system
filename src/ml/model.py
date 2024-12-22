# src/ml/model.py

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
import joblib
import os
from datetime import datetime, timedelta
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class FeatureEngineering(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.amount_mean = None
        self.amount_std = None
        self.location_risk_map = {}
        self.merchant_risk_map = {}
        logger.info("FeatureEngineering initialized")

    def fit(self, X, y=None):
        try:
            # Convert dictionary to DataFrame if needed
            if isinstance(X, dict):
                X = pd.DataFrame([X])
            
            self.amount_mean = X['amount'].mean()
            self.amount_std = X['amount'].std()
            self.location_risk_map = X.groupby('location_id')['amount'].mean().to_dict()
            self.merchant_risk_map = X.groupby('merchant_id')['amount'].mean().to_dict()
            
            logger.info("Feature engineering fitted successfully")
            return self
        except Exception as e:
            logger.error(f"Error in feature engineering fit: {str(e)}")
            raise

    def transform(self, X):
        try:
            # Convert dictionary to DataFrame if needed
            if isinstance(X, dict):
                X = pd.DataFrame([X])
            
            features = np.column_stack([
                self._standardize_amount(X['amount']),
                self._extract_time_features(X['timestamp']),
                self._calculate_location_risk(X['location_id']),
                self._get_merchant_risk(X['merchant_id'])
            ])
            
            logger.debug(f"Transformed features shape: {features.shape}")
            return features
        except Exception as e:
            logger.error(f"Error in feature transformation: {str(e)}")
            raise

    def _standardize_amount(self, amount):
        return (amount - self.amount_mean) / (self.amount_std if self.amount_std != 0 else 1)

    def _extract_time_features(self, timestamp):
        hour = pd.to_datetime(timestamp).dt.hour
        is_weekend = pd.to_datetime(timestamp).dt.dayofweek >= 5
        return np.column_stack([hour, is_weekend])

    def _calculate_location_risk(self, location_id):
        return np.array([
            self.location_risk_map.get(loc, self.amount_mean) 
            for loc in location_id
        ])

    def _get_merchant_risk(self, merchant_id):
        return np.array([
            self.merchant_risk_map.get(merch, self.amount_mean) 
            for merch in merchant_id
        ])

class FraudDetectionModel:
    def __init__(self, model_path=None):
        self.model_path = model_path or 'models/fraud_detection_model.pkl'
        self.model = self._build_model()
        logger.info("FraudDetectionModel initialized")

    def _build_model(self):
        return Pipeline([
            ('feature_engineering', FeatureEngineering()),
            ('classifier', XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                objective='binary:logistic'
            ))
        ])

    def train(self, X, y):
        try:
            logger.info("Starting model training")
            self.model.fit(X, y)
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model trained and saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            raise

    def predict(self, X):
        try:
            # Ensure model is loaded
            if not hasattr(self.model, 'predict_proba'):
                self.load_model()
            
            # Handle single transaction case
            if isinstance(X, dict):
                X = pd.DataFrame([X])
            
            predictions = self.model.predict_proba(X)[:, 1]
            logger.debug(f"Generated predictions: {predictions}")
            return predictions
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            raise

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info("Model loaded successfully")
            else:
                logger.warning("No existing model found, will need training")
                raise FileNotFoundError(f"Model file not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    @staticmethod
    def generate_dummy_data(n_samples=1000):
        """Generate dummy data for testing and initial training."""
        try:
            logger.info(f"Generating {n_samples} dummy transactions")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            timestamps = [
                start_date + timedelta(seconds=np.random.randint(0, 30*24*60*60))
                for _ in range(n_samples)
            ]
            
            data = {
                'timestamp': timestamps,
                'amount': np.random.lognormal(mean=4, sigma=1, size=n_samples),
                'location_id': np.random.randint(1, 51, size=n_samples),
                'merchant_id': np.random.randint(1, 101, size=n_samples)
            }
            
            # Generate labels (fraud is rare - about 1% of transactions)
            fraud_prob = np.zeros(n_samples)
            fraud_prob += np.random.normal(0, 1, n_samples) * 0.1
            fraud_prob += (data['amount'] > np.percentile(data['amount'], 95)) * 0.3
            fraud_prob = 1 / (1 + np.exp(-fraud_prob))
            labels = (fraud_prob > 0.9).astype(int)
            
            logger.info(f"Generated {sum(labels)} fraudulent transactions")
            return pd.DataFrame(data), labels
        except Exception as e:
            logger.error(f"Error generating dummy data: {str(e)}")
            raise