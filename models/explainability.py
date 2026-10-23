"""
CreditRisk AI - Explainable AI (XAI) and Model Interpretability
Provides SHAP (SHapley Additive exPlanations) for global and local borrower risk profiling,
with reliable fallbacks and financial domain governance notes.
"""

import os
import tempfile
# Ensure Matplotlib uses writable temp directory on Windows sandbox
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_creditrisk"))

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import shap

class CreditRiskExplainer:
    """
    Manages global and local explainability for credit delinquency models.
    Supports TreeExplainer for XGBoost/Random Forest and LinearExplainer for Logistic Regression,
    with robust fallbacks.
    """
    
    def __init__(self, model, model_name: str, background_data: pd.DataFrame):
        self.model = model
        self.model_name = model_name
        self.feature_names = list(background_data.columns)
        self.background_data = background_data
        
        # Sub-sample background data for low-latency SHAP initialization (100 samples)
        if len(background_data) > 100:
            self.bg_sample = background_data.sample(n=100, random_state=42)
        else:
            self.bg_sample = background_data
            
        self.explainer = None
        self._init_explainer()
        
    def _init_explainer(self):
        """Initializes appropriate SHAP explainer based on model architecture."""
        try:
            if self.model_name == "XGBoost":
                self.explainer = shap.TreeExplainer(self.model)
            elif self.model_name == "Random Forest":
                # For RF, use TreeExplainer with model output 'probability' or raw
                self.explainer = shap.TreeExplainer(self.model)
            elif self.model_name == "Logistic Regression":
                # LinearExplainer on the classifier step with scaled background
                scaler = self.model.named_steps["scaler"]
                classifier = self.model.named_steps["classifier"]
                scaled_bg = scaler.transform(self.bg_sample)
                self.explainer = shap.LinearExplainer(classifier, scaled_bg)
        except Exception as e:
            # Explainer fallback flag
            self.explainer = None
            
    def explain_global(self, sample_data: pd.DataFrame, max_samples: int = 300) -> Dict[str, Any]:
        """
        Computes global mean |SHAP| values across a representative cohort.
        Falls back to tree importance or coefficients if SHAP is bypassed.
        """
        if len(sample_data) > max_samples:
            sample_eval = sample_data.sample(n=max_samples, random_state=42)
        else:
            sample_eval = sample_data
            
        if self.explainer is not None:
            try:
                if self.model_name == "Logistic Regression":
                    scaler = self.model.named_steps["scaler"]
                    eval_matrix = scaler.transform(sample_eval)
                    shap_values = self.explainer.shap_values(eval_matrix)
                else:
                    # Tree models
                    shap_values = self.explainer.shap_values(sample_eval)
                    
                # Handle binary classification shapes
                if isinstance(shap_values, list):
                    # Usually index 1 is class 1 (default)
                    sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
                elif hasattr(shap_values, "values"):
                    # SHAP Explanation object
                    sv = shap_values.values
                    if len(sv.shape) == 3:
                        sv = sv[:, :, 1]
                else:
                    sv = shap_values
                    if len(sv.shape) == 3:
                        sv = sv[:, :, 1]
                        
                mean_abs_shap = np.mean(np.abs(sv), axis=0)
                sorted_indices = np.argsort(mean_abs_shap)[::-1]
                
                importance_list = [
                    {
                        "feature": self.feature_names[i],
                        "importance": float(mean_abs_shap[i]),
                        "mean_val": float(np.mean(sample_eval.iloc[:, i]))
                    }
                    for i in sorted_indices
                ]
                return {
                    "method": "SHAP (Kernel/Tree)",
                    "importance_ranking": importance_list,
                    "features": [self.feature_names[i] for i in sorted_indices],
                    "values": [float(mean_abs_shap[i]) for i in sorted_indices]
                }
            except Exception as e:
                pass
                
        # Lightweight Fallback: Feature Importance or Normalized Coefficients
        return self._fallback_global_importance()
        
    def _fallback_global_importance(self) -> Dict[str, Any]:
        """Reliable fallback if SHAP computation is interrupted."""
        if hasattr(self.model, "feature_importances_"):
            raw_imp = self.model.feature_importances_
        elif hasattr(self.model, "named_steps") and "classifier" in self.model.named_steps:
            raw_imp = np.abs(self.model.named_steps["classifier"].coef_[0])
        else:
            raw_imp = np.ones(len(self.feature_names))
            
        sorted_indices = np.argsort(raw_imp)[::-1]
        importance_list = [
            {
                "feature": self.feature_names[i],
                "importance": float(raw_imp[i]),
                "mean_val": 0.0
            }
            for i in sorted_indices
        ]
        return {
            "method": "Gini/Magnitude Fallback",
            "importance_ranking": importance_list,
            "features": [self.feature_names[i] for i in sorted_indices],
            "values": [float(raw_imp[i]) for i in sorted_indices]
        }
        
    def explain_instance(self, instance_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes local feature attribution for an individual borrower.
        Decomposes the prediction into positive pushes (risk increasing)
        and negative pushes (risk mitigating).
        """
        if not isinstance(instance_df, pd.DataFrame):
            instance_df = pd.DataFrame([instance_df], columns=self.feature_names)
            
        instance_row = instance_df.iloc[[0]]
        
        if self.explainer is not None:
            try:
                if self.model_name == "Logistic Regression":
                    scaler = self.model.named_steps["scaler"]
                    instance_matrix = scaler.transform(instance_row)
                    shap_vals = self.explainer.shap_values(instance_matrix)
                    expected_value = self.explainer.expected_value
                else:
                    shap_vals = self.explainer.shap_values(instance_row)
                    expected_value = self.explainer.expected_value
                    
                # Standardize shape
                if isinstance(shap_vals, list):
                    vals = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
                    base_val = expected_value[1] if isinstance(expected_value, (list, np.ndarray)) else expected_value
                elif hasattr(shap_vals, "values"):
                    sv = shap_vals.values[0]
                    vals = sv[:, 1] if len(sv.shape) > 1 else sv
                    base_val = shap_vals.base_values[0]
                    if isinstance(base_val, (list, np.ndarray)):
                        base_val = base_val[1]
                else:
                    if len(shap_vals.shape) == 3:
                        vals = shap_vals[0, :, 1]
                        base_val = expected_value[1] if isinstance(expected_value, (list, np.ndarray)) else expected_value
                    elif len(shap_vals.shape) == 2:
                        vals = shap_vals[0]
                        base_val = float(expected_value)
                    else:
                        vals = shap_vals
                        base_val = float(expected_value)
                        
                # Create contribution decomposition
                contributions = []
                for feat, val, shap_val in zip(self.feature_names, instance_row.values[0], vals):
                    contributions.append({
                        "feature": feat,
                        "value": float(val),
                        "attribution": float(shap_val),
                        "impact": "Increases Risk" if shap_val > 0 else "Lowers Risk"
                    })
                    
                # Sort by absolute attribution
                contributions.sort(key=lambda x: abs(x["attribution"]), reverse=True)
                
                return {
                    "method": "SHAP Local Explanation",
                    "base_value": float(base_val),
                    "contributions": contributions,
                    "top_risk_factors": [c for c in contributions if c["attribution"] > 0][:5],
                    "top_protective_factors": [c for c in contributions if c["attribution"] < 0][:5]
                }
            except Exception as e:
                pass
                
        # Fallback local attribution via normalized deviations
        return self._fallback_local_explanation(instance_row)
        
    def _fallback_local_explanation(self, instance_row: pd.DataFrame) -> Dict[str, Any]:
        """Provides heuristic local risk attribution if SHAP is unavailable."""
        contributions = []
        bg_means = self.bg_sample.mean()
        bg_stds = self.bg_sample.std().replace(0, 1.0)
        
        for feat in self.feature_names:
            val = float(instance_row[feat].values[0])
            mean_val = float(bg_means[feat])
            std_val = float(bg_stds[feat])
            z_score = (val - mean_val) / std_val
            
            # Risk weights
            risk_increasing_features = [
                "RevolvingUtilizationOfUnsecuredLines",
                "NumberOfTime30-59DaysPastDueNotWorse",
                "NumberOfTime60-89DaysPastDueNotWorse",
                "NumberOfTimes90DaysLate",
                "DebtRatio",
                "TotalDelinquencyEvents",
                "HasSevereDelinquency",
                "IsOverUtilized"
            ]
            
            if feat in risk_increasing_features:
                attribution = z_score * 0.25
            elif feat in ["age", "MonthlyIncome"]:
                attribution = -z_score * 0.20
            else:
                attribution = z_score * 0.05
                
            contributions.append({
                "feature": feat,
                "value": val,
                "attribution": float(attribution),
                "impact": "Increases Risk" if attribution > 0 else "Lowers Risk"
            })
            
        contributions.sort(key=lambda x: abs(x["attribution"]), reverse=True)
        return {
            "method": "Standardized Deviation Proxy",
            "base_value": 0.0,
            "contributions": contributions,
            "top_risk_factors": [c for c in contributions if c["attribution"] > 0][:5],
            "top_protective_factors": [c for c in contributions if c["attribution"] < 0][:5]
        }
