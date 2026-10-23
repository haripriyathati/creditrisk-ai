"""
CreditRisk AI - Utility Functions and Synthetic Dataset Generation
Provides data synthesis, schema validation, and formatting tools calibrated
to the Kaggle "Give Me Some Credit" competition benchmark.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional

FEATURE_COLUMNS = [
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfTime30-59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60-89DaysPastDueNotWorse",
    "NumberOfDependents"
]

TARGET_COLUMN = "SeriousDlqin2yrs"

def generate_synthetic_credit_data(
    n_samples: int = 15000,
    random_state: int = 42,
    target_default_rate: float = 0.0668
) -> pd.DataFrame:
    """
    Generates a realistic, statistically calibrated synthetic credit delinquency dataset
    matching the Give Me Some Credit schema, empirical distributions, and risk correlations.
    """
    rng = np.random.default_rng(random_state)
    
    # 1. Age: Truncated normal distribution around 52 years (range 21 - 92)
    age = np.clip(rng.normal(loc=52.3, scale=14.5, size=n_samples).astype(int), 21, 95)
    
    # 2. Revolving Utilization: Beta / Log-normal mixture
    # Majority under 0.6, long right tail representing over-leveraged cards
    u_base = rng.beta(a=1.2, b=4.5, size=n_samples) * 1.15
    u_tail = rng.exponential(scale=0.4, size=n_samples) * (rng.random(size=n_samples) < 0.12)
    revolving_util = np.round(u_base + u_tail, 4)
    # A few extreme outliers matching raw Kaggle data
    outlier_idx = rng.choice(n_samples, size=int(n_samples * 0.005), replace=False)
    revolving_util[outlier_idx] = rng.uniform(2.0, 15.0, size=len(outlier_idx))
    
    # 3. Monthly Income: Log-normal distribution with median ~5400
    log_income = rng.normal(loc=8.6, scale=0.75, size=n_samples)
    monthly_income = np.round(np.exp(log_income), -1)
    monthly_income = np.clip(monthly_income, 500, 75000)
    
    # 4. Open credit lines & loans: Poisson distribution
    open_lines = rng.poisson(lam=8.4, size=n_samples)
    open_lines = np.clip(open_lines, 0, 45)
    
    # 5. Real estate loans: Poisson distribution
    real_estate = rng.poisson(lam=1.05, size=n_samples)
    real_estate = np.clip(real_estate, 0, 15)
    
    # 6. Debt Ratio: Dependent on income and real estate
    # Standard DTI around 0.32, but if high real estate loans or low income, higher
    dti_base = rng.gamma(shape=2.5, scale=0.14, size=n_samples)
    dti_real_estate_boost = (real_estate * 0.06)
    debt_ratio = np.round(dti_base + dti_real_estate_boost, 4)
    # Give Me Some Credit has cases where DebtRatio is high (unreported income)
    high_dti_idx = rng.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    debt_ratio[high_dti_idx] = rng.uniform(1.5, 450.0, size=len(high_dti_idx))
    
    # 7. Delinquency history (30-59, 60-89, 90+ days late)
    # Zero-inflated Poisson distributions
    late30_prob = 0.22
    late30 = (rng.random(size=n_samples) < late30_prob) * rng.poisson(lam=0.8, size=n_samples)
    
    late60_prob = 0.10
    late60 = (rng.random(size=n_samples) < late60_prob) * rng.poisson(lam=0.5, size=n_samples)
    
    late90_prob = 0.08
    late90 = (rng.random(size=n_samples) < late90_prob) * rng.poisson(lam=0.4, size=n_samples)
    
    # Cap special Kaggle codes (96, 98) in a tiny fraction of records
    special_code_idx = rng.choice(n_samples, size=int(n_samples * 0.003), replace=False)
    late30[special_code_idx] = 98
    late60[special_code_idx] = 98
    late90[special_code_idx] = 98
    
    # 8. Number of dependents
    dependents = rng.poisson(lam=0.76, size=n_samples)
    dependents = np.clip(dependents, 0, 10).astype(float)
    
    # 9. Realistic Target (SeriousDlqin2yrs) generation using true BFSI credit risk logit
    # Log-odds calculation:
    clean_late30 = np.where(late30 >= 96, 2.5, late30)
    clean_late60 = np.where(late60 >= 96, 3.0, late60)
    clean_late90 = np.where(late90 >= 96, 4.0, late90)
    clean_util = np.clip(revolving_util, 0, 3.0)
    clean_dti = np.clip(debt_ratio, 0, 3.0)
    
    z = (
        -3.85
        + 1.65 * clean_util
        + 1.35 * clean_late90
        + 0.85 * clean_late60
        + 0.55 * clean_late30
        + 0.40 * clean_dti
        - 0.022 * (age - 50)
        - 0.000045 * (monthly_income - 5000)
        + 0.12 * (dependents - 0.7)
        - 0.03 * (open_lines - 8)
        + rng.normal(0, 0.45, size=n_samples)  # Unobserved risk component
    )
    
    p = 1.0 / (1.0 + np.exp(-z))
    # Calibrate probability threshold to obtain target default rate (~6.68%)
    cutoff = np.percentile(p, (1.0 - target_default_rate) * 100)
    serious_dlq = (p >= cutoff).astype(int)
    
    # 10. Introduce realistic Missing Values matching Give Me Some Credit
    # MonthlyIncome: ~19.8% missing
    income_missing_mask = rng.random(size=n_samples) < 0.198
    monthly_income[income_missing_mask] = np.nan
    
    # NumberOfDependents: ~2.6% missing
    dep_missing_mask = rng.random(size=n_samples) < 0.026
    dependents[dep_missing_mask] = np.nan
    
    df = pd.DataFrame({
        "Unnamed: 0": np.arange(1, n_samples + 1),
        TARGET_COLUMN: serious_dlq,
        "RevolvingUtilizationOfUnsecuredLines": revolving_util,
        "age": age,
        "NumberOfTime30-59DaysPastDueNotWorse": late30,
        "DebtRatio": debt_ratio,
        "MonthlyIncome": monthly_income,
        "NumberOfOpenCreditLinesAndLoans": open_lines,
        "NumberOfTimes90DaysLate": late90,
        "NumberRealEstateLoansOrLines": real_estate,
        "NumberOfTime60-89DaysPastDueNotWorse": late60,
        "NumberOfDependents": dependents
    })
    
    return df

def validate_credit_dataframe(df: pd.DataFrame) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates uploaded or loaded DataFrame against the expected Kaggle schema.
    Returns (is_valid, message, metadata).
    """
    cols = list(df.columns)
    
    # Clean possible unnamed index column
    cleaned_df = df.copy()
    if "Unnamed: 0" in cleaned_df.columns:
        cleaned_df = cleaned_df.drop(columns=["Unnamed: 0"])
    
    has_target = TARGET_COLUMN in cleaned_df.columns
    missing_features = [f for f in FEATURE_COLUMNS if f not in cleaned_df.columns]
    
    metadata = {
        "total_rows": len(cleaned_df),
        "total_columns": len(cleaned_df.columns),
        "has_target": has_target,
        "missing_features": missing_features,
        "feature_count": len([f for f in FEATURE_COLUMNS if f in cleaned_df.columns])
    }
    
    if missing_features:
        return False, f"Missing required feature columns: {', '.join(missing_features)}", metadata
    
    if not has_target:
        return False, f"Missing target column '{TARGET_COLUMN}'. Uploaded file must contain training labels.", metadata
        
    return True, "Valid Give Me Some Credit schema detected.", metadata

def load_data_dictionary() -> Dict[str, Any]:
    """Loads feature definitions and descriptions."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "data_dictionary.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}
