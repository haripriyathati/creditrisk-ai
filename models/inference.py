"""
CreditRisk AI - Real-time Inference Engine and Scoring Service
Applies consistent schema validation, preprocessing, and probability calibration
for single-applicant scoring and batch portfolio assessment.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Union, Optional
from components.utils import FEATURE_COLUMNS

def predict_single_applicant(
    applicant_data: Dict[str, Any],
    model,
    preprocessor,
    low_risk_threshold: float = 0.10,
    high_risk_threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Evaluates a single loan applicant:
    1. Validates and casts input dictionary to DataFrame.
    2. Runs feature preprocessing and feature engineering.
    3. Infers delinquency probability.
    4. Categorizes into configurable risk bands (Low, Medium, High).
    5. Maps probability to a simulated credit score (300 - 850).
    """
    # Create input DataFrame with expected columns
    row = {}
    for col in FEATURE_COLUMNS:
        val = applicant_data.get(col, None)
        if val is None or val == "" or (isinstance(val, float) and np.isnan(val)):
            row[col] = np.nan
        else:
            try:
                row[col] = float(val)
            except (ValueError, TypeError):
                row[col] = np.nan
                
    df_raw = pd.DataFrame([row])
    
    # Preprocess
    df_transformed = preprocessor.transform(df_raw)
    
    # Predict probability of delinquency (class 1)
    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(df_transformed)[0, 1])
    else:
        prob = float(model.predict(df_transformed)[0])
        
    prob = max(0.0001, min(0.9999, prob))
    
    # Risk Tier assignment based on configurable thresholds
    if prob < low_risk_threshold:
        tier = "Low Risk (Prime)"
        status = "ACCEPTABLE"
        color = "#10B981"  # Emerald green
    elif prob < high_risk_threshold:
        tier = "Medium Risk (Near-Prime)"
        status = "MANUAL REVIEW"
        color = "#F59E0B"  # Amber
    else:
        tier = "High Risk (Subprime / Distressed)"
        status = "ELEVATED RISK"
        color = "#EF4444"  # Crimson
        
    # Standard FICO-like scale mapping (300 to 850)
    # Log-odds inverted to standard credit score
    # Score 850 when prob near 0; Score 300 when prob near 1
    simulated_score = int(np.round(850 - (prob * 550)))
    simulated_score = max(300, min(850, simulated_score))
    
    return {
        "probability": prob,
        "probability_pct": round(prob * 100, 2),
        "simulated_credit_score": simulated_score,
        "risk_tier": tier,
        "status": status,
        "color": color,
        "transformed_features": df_transformed.iloc[0].to_dict(),
        "input_features": row
    }

def predict_batch_portfolio(
    df: pd.DataFrame,
    model,
    preprocessor,
    low_risk_threshold: float = 0.10,
    high_risk_threshold: float = 0.25
) -> pd.DataFrame:
    """
    Applies batch scoring over an entire portfolio DataFrame.
    Appends probability, risk tier, and simulated score.
    """
    df_clean = df.copy()
    if "Unnamed: 0" in df_clean.columns:
        df_clean = df_clean.drop(columns=["Unnamed: 0"])
        
    # Extract only feature columns
    features = [c for c in FEATURE_COLUMNS if c in df_clean.columns]
    X_raw = df_clean[features].copy()
    
    X_transformed = preprocessor.transform(X_raw)
    probabilities = model.predict_proba(X_transformed)[:, 1]
    
    results_df = df_clean.copy()
    results_df["Predicted_Delinquency_Prob"] = probabilities
    results_df["Simulated_Credit_Score"] = (850 - (probabilities * 550)).round().astype(int).clip(300, 850)
    
    conditions = [
        results_df["Predicted_Delinquency_Prob"] < low_risk_threshold,
        results_df["Predicted_Delinquency_Prob"] < high_risk_threshold
    ]
    choices = ["Low Risk", "Medium Risk"]
    results_df["Risk_Category"] = np.select(conditions, choices, default="High Risk")
    
    return results_df
