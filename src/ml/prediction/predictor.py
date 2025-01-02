# src/ml/prediction/predictor.py

import numpy as np
import xgboost as xgb
import os
import logging
from typing import Dict, List
from datetime import datetime
from src.ml.preprocessing.preprocessor import FraudDataPreprocessor

logger = logging.getLogger(__name__)

class FraudPredictor:
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.preprocessor = FraudDataPreprocessor()
        self._load_model()

    def _validate_features(self, features: Dict) -> None:
        """Validate that all required features are present"""
        required_fields = ['amount', 'location_id']
        missing_fields = [field for field in required_fields if field not in features]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
            
        # Validate numeric values
        try:
            float(features['amount'])
            int(features['location_id'])
        except (ValueError, TypeError):
            raise ValueError("Amount must be numeric and location_id must be an integer")

    def predict(self, features: Dict) -> Dict:
        """Make fraud prediction for a transaction"""
        try:
            # Validate input features
            self._validate_features(features)
            
            # Transform data
            features_array = self.preprocessor.transform_transaction_data(features)
            
            # Convert to DMatrix for XGBoost
            dmatrix = xgb.DMatrix(features_array)
            
            # Get raw prediction score and convert to probability using sigmoid
            raw_pred = self.model.predict(dmatrix)[0]
            fraud_prob = float(1 / (1 + np.exp(-raw_pred)))
            
            # Adjust probability based on risk scores
            risk_components = self._calculate_risk_components(features_array[0], list(self.get_feature_importances().values()))
            
            # Count high risk indicators
            high_risks = sum(1 for score in risk_components.values() if score > 0.8)
            
            # Boost fraud probability if multiple high risks are detected
            if high_risks >= 2:
                fraud_prob = max(fraud_prob, 0.7)  # At least HIGH risk if multiple high risk indicators
            elif high_risks == 1:
                fraud_prob = max(fraud_prob, 0.4)  # At least MEDIUM risk if one high risk indicator
                
            # Determine risk level
            risk_level = self._get_risk_level(fraud_prob)
            
            return {
                'fraud_probability': fraud_prob,
                'risk_components': risk_components,
                'risk_level': risk_level,
                'merchant_risk_score': risk_components['location_merchant_risk'],
                'location_risk_score': risk_components['location_merchant_risk'],
                'amount_risk_score': risk_components['amount_risk'],
                'pattern_risk_score': risk_components['pattern_risk'],
                'user_behavior_risk_score': risk_components['user_behavior_risk']
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

    def _calculate_risk_components(self, features: np.ndarray, importance_values: List[float]) -> Dict:
        """Calculate risk components based on feature groups"""
        try:
            # Convert importance_values list to numpy array for element-wise multiplication
            importance_array = np.array(importance_values)
            
            # Calculate weighted means for each component
            pattern_risk = np.mean(features[0:10] * importance_array[0:10])
            user_behavior_risk = np.mean(features[10:20] * importance_array[10:20])
            location_merchant_risk = np.mean(features[20:28] * importance_array[20:28])
            amount_risk = features[28] * importance_array[28]
            time_risk = np.mean(features[29:] * importance_array[29:])

            def normalize_score(score: float) -> float:
                return float(1 / (1 + np.exp(-score/100)))  # Dividing by 100 to adjust the scale

            components = {
                'pattern_risk': normalize_score(pattern_risk),
                'user_behavior_risk': normalize_score(user_behavior_risk),
                'location_merchant_risk': normalize_score(location_merchant_risk),
                'amount_risk': normalize_score(amount_risk),
                'time_risk': normalize_score(time_risk)
            }
            
            # Ensure all values are finite
            for key, value in components.items():
                if not np.isfinite(value):
                    components[key] = 0.0
            
                    
            return components
            
        except Exception as e:
            logger.error(f"Error calculating risk components: {str(e)}")
            # Return default risk components if there's an error
            return {
                'pattern_risk': 0.0,
                'user_behavior_risk': 0.0,
                'location_merchant_risk': 0.0,
                'amount_risk': 0.0,
                'time_risk': 0.0
            }

    def _get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability < 0.3:
            return 'LOW'
        elif probability < 0.7:
            return 'MEDIUM'
        return 'HIGH'

    def _load_model(self):
        """Load the latest model"""
        try:
            logger.info(f"Checking for model files in directory: {self.model_dir}")
            
            model_files = sorted(
                [f for f in os.listdir(self.model_dir) 
                 if f.startswith('fraud_model_') and f.endswith('.json')]
            )
            logger.info(f"Found model files: {model_files}")
            
            if not model_files:
                raise FileNotFoundError("No model files found in models directory")
                
            latest_model = model_files[-1]
            model_path = os.path.join(self.model_dir, latest_model)
            logger.info(f"Attempting to load model from path: {model_path}")
            
            # Create a new XGBoost Booster and load the model
            self.model = xgb.Booster()
            self.model.load_model(model_path)
            logger.info(f"Successfully loaded model: {latest_model}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def get_feature_importances(self) -> Dict[str, float]:
        """Get importance of each feature"""
        try:
            # Get raw importance scores
            importance_scores = self.model.get_score(importance_type='gain')
            feature_names = self.preprocessor.feature_names()
            
            # Initialize importances with zeros
            importances = np.zeros(len(feature_names))
            
            # Fill in available importance scores
            for f_idx in importance_scores:
                idx = int(f_idx.replace('f', ''))  # Convert 'f0', 'f1' etc to index
                importances[idx] = importance_scores[f_idx]
                
            return dict(zip(feature_names, importances))
            
        except Exception as e:
            logger.error(f"Error getting feature importances: {str(e)}")
            # Return default importances if there's an error
            return {name: 1.0 for name in self.preprocessor.feature_names()}

    def health_check(self) -> bool:
        """Check if model is loaded and functional"""
        try:
            # Create dummy features for health check
            dummy_features = {
                'amount': 0,
                'location_id': 0,
                'card_id': 'test',
                'merchant_id': 'test',
                'device_id': 'test',
                'ip_address': 'test'
            }
            
            # Try to make a prediction
            self.predict(dummy_features)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False