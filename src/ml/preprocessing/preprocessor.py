# src/ml/preprocessing/preprocessor.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from imblearn.over_sampling import SMOTE
import joblib
import os
import time
from typing import Tuple, Dict
import logging

# Add logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDataPreprocessor:
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        self.amount_scaler = RobustScaler()
        self.feature_scaler = StandardScaler()
        os.makedirs(model_dir, exist_ok=True)
        logger.info(f"Initialized FraudDataPreprocessor with model_dir: {model_dir}")

    def _check_data_distribution(self, y):
        """Check and log class distribution"""
        unique, counts = np.unique(y, return_counts=True)
        dist = dict(zip(unique, counts))
        total = len(y)
        logger.info("Class distribution:")
        for class_label, count in dist.items():
            percentage = (count/total) * 100
            logger.info(f"Class {class_label}: {count} ({percentage:.2f}%)")
        return dist
        
    def prepare_training_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training"""
        logger.info("Loading and preprocessing training data...")
        
        # Load data
        df = pd.read_csv(data_path)
        logger.info(f"Loaded dataset with shape: {df.shape}")
        self._check_data_distribution(df['Class'].values)
        
        # Process features
        X = self._preprocess_features(df)
        y = df['Class'].values
        
        # Handle class imbalance
        logger.info("Applying SMOTE for class imbalance...")
        smote = SMOTE(random_state=42, sampling_strategy=0.1)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        logger.info(f"After SMOTE - X shape: {X_resampled.shape}, y shape: {y_resampled.shape}")
        
        # Save preprocessors
        self._save_preprocessors()
        
        return X_resampled, y_resampled
    
    def prepare_prediction_data(self, transaction_data: Dict) -> np.ndarray:
        """Prepare single transaction data for prediction"""
        # Load preprocessors
        self._load_preprocessors()
        
        # Convert transaction data to features
        features = self._convert_transaction_to_features(transaction_data)
        
        return features
    
    def _preprocess_features(self, df: pd.DataFrame) -> np.ndarray:
        """Preprocess features for model"""
        logger.info("Preprocessing features...")
        
        # Scale amount
        amount_scaled = self.amount_scaler.fit_transform(
            df['Amount'].values.reshape(-1, 1)
        )
        
        # Process time feature
        time_features = self._process_time_feature(df['Time'])
        
        # Scale V1-V28 features
        v_features = self.feature_scaler.fit_transform(
            df[['V%d' % i for i in range(1,29)]]
        )
        
        return np.hstack([v_features, amount_scaled, time_features])
    
    def _process_time_feature(self, time_series: pd.Series) -> np.ndarray:
        """Process time feature into meaningful components"""
        # Convert to seconds of day
        seconds_in_day = time_series % 86400
        
        # Create cyclical time features
        time_sin = np.sin(2 * np.pi * seconds_in_day / 86400)
        time_cos = np.cos(2 * np.pi * seconds_in_day / 86400)
        
        return np.column_stack([time_sin, time_cos])
    
    def _save_preprocessors(self):
        """Save preprocessors for later use"""
        logger.info("Saving preprocessors...")
        joblib.dump(self.amount_scaler, 
                   os.path.join(self.model_dir, 'amount_scaler.pkl'))
        joblib.dump(self.feature_scaler, 
                   os.path.join(self.model_dir, 'feature_scaler.pkl'))
        logger.info("Preprocessors saved successfully")
    
    def _load_preprocessors(self):
        """Load saved preprocessors"""
        logger.info("Loading preprocessors...")
        self.amount_scaler = joblib.load(
            os.path.join(self.model_dir, 'amount_scaler.pkl')
        )
        self.feature_scaler = joblib.load(
            os.path.join(self.model_dir, 'feature_scaler.pkl')
        )
        logger.info("Preprocessors loaded successfully")

    def transform_transaction_data(self, transaction: Dict) -> np.ndarray:
        """Transform a raw transaction into model features"""
        try:
            logger.info("Transforming transaction data...")
            
            # Load preprocessors if not already loaded
            self._load_preprocessors()
            
            # Initialize feature arrays
            pattern_features = np.zeros(10)    # V1-V10
            behavior_features = np.zeros(10)   # V11-V20
            location_features = np.zeros(8)    # V21-V28
            
            # 1. Pattern Risk (V1-V10)
            card_hash = hash(transaction.get('card_id', '')) % 100
            pattern_features[0] = card_hash
            pattern_features[1] = float(hash(transaction.get('device_id', '')) % 100)
            pattern_features[2] = float(hash(transaction.get('ip_address', '')) % 100)
            # Remaining pattern features can be derived from other transaction patterns
            
            # 2. User Behavior (V11-V20)
            behavior_features[0] = card_hash  # Reuse card hash for user behavior
            behavior_features[1] = float(transaction.get('location_id', 0))
            # Additional behavior features can be added here
            
            # 3. Location/Merchant Risk (V21-V28)
            merchant_hash = hash(transaction.get('merchant_id', '')) % 100
            location_features[0] = merchant_hash
            location_features[1] = float(transaction.get('location_id', 0))
            # Additional location/merchant features can be added here
            
            # Combine and reshape all V features
            v_features = np.concatenate([
                pattern_features,
                behavior_features,
                location_features
            ]).reshape(1, -1)
            
            # Scale V features
            v_features_scaled = self.feature_scaler.transform(v_features)
            
            # Scale amount
            amount = float(transaction.get('amount', 0.0))
            amount_scaled = self.amount_scaler.transform([[amount]])
            
            # Add time features
            current_time = int(time.time() % 86400)  # Current time in seconds since midnight
            time_features = self._process_time_feature(pd.Series([current_time]))
            
            # Combine all features
            features = np.hstack([v_features_scaled, amount_scaled, time_features])
            
            logger.info(f"Transaction transformed successfully. Feature shape: {features.shape}")
            return features
            
        except Exception as e:
            logger.error(f"Error transforming transaction: {str(e)}")
            raise ValueError(f"Error transforming transaction data: {str(e)}")
    def feature_names(self) -> list:
        """Return list of feature names"""
        return ([f'V{i}' for i in range(1, 29)] + 
                ['Amount', 'Time_sin', 'Time_cos'])
