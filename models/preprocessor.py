"""
CreditRisk AI - Preprocessor and Feature Engineering Pipeline
Handles data cleaning, missing-value imputation, extreme outlier treatment,
and banking domain feature engineering without data leakage.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Optional

class CreditRiskPreprocessor(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compliant preprocessor designed for credit delinquency prediction.
    Strictly fits statistics on the training set to prevent data leakage.
    """
    
    def __init__(
        self,
        cap_utilization: float = 10.0,
        cap_debt_ratio: float = 20.0,
        cap_delinquencies: int = 15,
        create_missing_indicators: bool = True,
        engineer_domain_features: bool = True
    ):
        self.cap_utilization = cap_utilization
        self.cap_debt_ratio = cap_debt_ratio
        self.cap_delinquencies = cap_delinquencies
        self.create_missing_indicators = create_missing_indicators
        self.engineer_domain_features = engineer_domain_features
        
        # State learned during fit
        self.monthly_income_median_: float = 5400.0
        self.number_of_dependents_median_: float = 0.0
        self.feature_names_out_: List[str] = []
        
    def fit(self, X: pd.DataFrame, y=None):
        """Fit imputation statistics strictly on X_train."""
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
            
        # Learn medians for missing values
        if "MonthlyIncome" in X.columns:
            self.monthly_income_median_ = float(X["MonthlyIncome"].median(skipna=True))
            if np.isnan(self.monthly_income_median_):
                self.monthly_income_median_ = 5400.0
                
        if "NumberOfDependents" in X.columns:
            self.number_of_dependents_median_ = float(X["NumberOfDependents"].median(skipna=True))
            if np.isnan(self.number_of_dependents_median_):
                self.number_of_dependents_median_ = 0.0

        # Transform a dummy sample to record output feature names
        dummy_transformed = self._transform_internal(X.head(5).copy())
        self.feature_names_out_ = list(dummy_transformed.columns)
        return self
        
    def _transform_internal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Core transformation logic applied to any dataset."""
        df = df.copy()
        
        # Drop Kaggle index or target column if present in input
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])
        if "SeriousDlqin2yrs" in df.columns:
            df = df.drop(columns=["SeriousDlqin2yrs"])
            
        # 1. Missing value flags & imputation
        if self.create_missing_indicators:
            if "MonthlyIncome" in df.columns:
                df["MonthlyIncome_Missing"] = df["MonthlyIncome"].isna().astype(float)
            if "NumberOfDependents" in df.columns:
                df["NumberOfDependents_Missing"] = df["NumberOfDependents"].isna().astype(float)
                
        if "MonthlyIncome" in df.columns:
            df["MonthlyIncome"] = df["MonthlyIncome"].fillna(self.monthly_income_median_)
            
        if "NumberOfDependents" in df.columns:
            df["NumberOfDependents"] = df["NumberOfDependents"].fillna(self.number_of_dependents_median_)
            
        # 2. Outlier treatment & Special Kaggle Codes (96, 98)
        # 96 and 98 represent missing/unrecorded in Give Me Some Credit
        delinq_cols = [
            "NumberOfTime30-59DaysPastDueNotWorse",
            "NumberOfTime60-89DaysPastDueNotWorse",
            "NumberOfTimes90DaysLate"
        ]
        for col in delinq_cols:
            if col in df.columns:
                # Replace special codes with high-risk ceiling
                df[col] = df[col].replace({96: 5, 98: 5})
                df[col] = df[col].clip(lower=0, upper=self.cap_delinquencies)
                
        if "RevolvingUtilizationOfUnsecuredLines" in df.columns:
            df["RevolvingUtilizationOfUnsecuredLines"] = df["RevolvingUtilizationOfUnsecuredLines"].clip(
                lower=0.0, upper=self.cap_utilization
            )
            
        if "DebtRatio" in df.columns:
            df["DebtRatio"] = df["DebtRatio"].clip(lower=0.0, upper=self.cap_debt_ratio)
            
        if "age" in df.columns:
            # Handle anomalous age <= 0 or extreme
            df["age"] = df["age"].clip(lower=18, upper=100)
            
        # 3. Domain Feature Engineering (BFSI Best Practices)
        if self.engineer_domain_features:
            # Total delinquency count across all buckets
            total_delinq = (
                df.get("NumberOfTime30-59DaysPastDueNotWorse", 0) +
                df.get("NumberOfTime60-89DaysPastDueNotWorse", 0) +
                df.get("NumberOfTimes90DaysLate", 0)
            )
            df["TotalDelinquencyEvents"] = total_delinq
            
            # Severe delinquency indicator (90+ days is a major derogatory event)
            if "NumberOfTimes90DaysLate" in df.columns:
                df["HasSevereDelinquency"] = (df["NumberOfTimes90DaysLate"] > 0).astype(float)
                
            # Over-utilization alert flag (utilization > 0.8 is standard credit warning)
            if "RevolvingUtilizationOfUnsecuredLines" in df.columns:
                df["IsOverUtilized"] = (df["RevolvingUtilizationOfUnsecuredLines"] > 0.8).astype(float)
                
            # Log transformed utilization and debt ratio for linear sensitivity
            if "RevolvingUtilizationOfUnsecuredLines" in df.columns:
                df["Log_RevolvingUtilization"] = np.log1p(df["RevolvingUtilizationOfUnsecuredLines"])
                
            if "DebtRatio" in df.columns:
                df["Log_DebtRatio"] = np.log1p(df["DebtRatio"])
                
        return df

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform input features using fitted statistics."""
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        return self._transform_internal(X)

    def get_feature_names_out(self, input_features=None) -> List[str]:
        return self.feature_names_out_
