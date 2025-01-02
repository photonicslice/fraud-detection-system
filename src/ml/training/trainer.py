# src/ml/training/trainer.py

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_curve, auc, average_precision_score
import xgboost as xgb
import optuna
import joblib
import os
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudModelTrainer:
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        self.cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        os.makedirs(model_dir, exist_ok=True)
        
    def _objective(self, trial, X, y):
        param = {
            'max_depth': trial.suggest_int('max_depth', 2, 4),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
            'min_child_weight': trial.suggest_int('min_child_weight', 5, 10),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.1, 10.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 0.1, 10.0),
            'subsample': trial.suggest_float('subsample', 0.5, 0.7),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.7),
            'objective': 'binary:logistic',
            'eval_metric': 'aucpr',
            'tree_method': 'hist',
            'scale_pos_weight': 50
        }
        
        boost_rounds = trial.suggest_int('boost_rounds', 50, 200)
        
        scores = []
        for fold, (train_idx, val_idx) in enumerate(self.cv.split(X, y)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            dtrain = xgb.DMatrix(X_train, label=y_train)
            dval = xgb.DMatrix(X_val, label=y_val)
            
            model = xgb.train(
                params=param,
                dtrain=dtrain,
                num_boost_round=boost_rounds,
                evals=[(dval, 'eval')],
                early_stopping_rounds=10,
                verbose_eval=False
            )
            
            y_pred = model.predict(dval)
            precision, recall, _ = precision_recall_curve(y_val, y_pred)
            auprc = auc(recall, precision)
            scores.append(auprc)
            
            logger.info(f"Fold {fold + 1} AUPRC: {auprc:.4f}")
        
        mean_score = np.mean(scores)
        logger.info(f"Mean AUPRC: {mean_score:.4f} (std: {np.std(scores):.4f})")
        return mean_score

    def train_model(self, X, y):
        """Train the final model with the best parameters"""
        logger.info("Starting model training process...")
        
        study = optuna.create_study(direction='maximize')
        study.optimize(
            lambda trial: self._objective(trial, X, y),
            n_trials=20,
            show_progress_bar=True
        )
        
        best_params = study.best_params
        boost_rounds = best_params.pop('boost_rounds')  # Remove and store boost_rounds
        logger.info(f"Best parameters: {best_params}")
        logger.info(f"Best boost rounds: {boost_rounds}")
        
        final_params = {
            **best_params,
            'objective': 'binary:logistic',
            'eval_metric': 'aucpr',
            'tree_method': 'hist'
        }
        
        dtrain = xgb.DMatrix(X, label=y)
        
        final_model = xgb.train(
            params=final_params,
            dtrain=dtrain,
            num_boost_round=boost_rounds,
            verbose_eval=True
        )
        
        self._save_model(final_model, best_params, study.best_value)
        
        return final_model
    
    def _save_model(self, model, params, best_score):
        """Save model and its metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_path = os.path.join(self.model_dir, f'fraud_model_{timestamp}.json')
        model.save_model(model_path)
        
        metadata = {
            'timestamp': timestamp,
            'parameters': params,
            'best_score': float(best_score),
            'feature_importance': {
                f'f{i}': float(score) 
                for i, score in enumerate(model.get_score(importance_type='gain').values())
            }
        }
        
        metadata_path = os.path.join(self.model_dir, f'model_metadata_{timestamp}.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"Model saved: {model_path}")
        logger.info(f"Metadata saved: {metadata_path}")