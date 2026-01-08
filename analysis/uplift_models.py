import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklift.models import SoloModel, ClassTransformation
from sklift.metrics import qini_auc_score, uplift_at_k
from catboost import CatBoostClassifier
# Note: CatBoost is heavy, usually fine, but if we want lighter we can use RandomForest
from sklearn.ensemble import RandomForestClassifier

def train_uplift_model(df: pd.DataFrame, feature_cols: list, treatment_col='treatment', outcome_col='outcome_conversion', method='class_transform'):
    """
    Trains an uplift model.
    """
    X = df[feature_cols]
    y = df[outcome_col]
    treat = df[treatment_col]
    
    # Split for valid evaluation
    X_train, X_val, y_train, y_val, treat_train, treat_val = train_test_split(
        X, y, treat, test_size=0.3, random_state=42, stratify=treat
    )
    
    # Base estimator
    estimator = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    
    if method == 'class_transform':
        uplift_model = ClassTransformation(estimator=estimator)
    else:
        uplift_model = SoloModel(estimator=estimator)
        
    uplift_model.fit(X_train, y_train, treat_train)
    
    # Predictions
    uplift_scores = uplift_model.predict(X_val)
    
    # Evaluate
    qini_auc = qini_auc_score(y_val, uplift_scores, treat_val)
    lift_at_30 = uplift_at_k(y_val, uplift_scores, treat_val, strategy='overall', k=0.3)
    
    return {
        'model_name': method,
        'qini_auc': float(qini_auc),
        'uplift_at_30': float(lift_at_30),
        'targeting_fraction': 0.3, # For the metric above
        'expected_value_lift': float(lift_at_30) # Proxy for now
    }
