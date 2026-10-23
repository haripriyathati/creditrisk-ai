"""
Unit and Integration Tests for CreditRisk AI
Validates synthetic generation, preprocessor leakage-prevention, model inference,
threshold optimization, and SHAP explainability.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add root project path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.utils import (
    generate_synthetic_credit_data,
    validate_credit_dataframe,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)
from models.preprocessor import CreditRiskPreprocessor
from models.pipeline import load_artifacts, _compute_threshold_metrics
from models.inference import predict_single_applicant, predict_batch_portfolio
from models.explainability import CreditRiskExplainer

class TestCreditRiskAI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load or verify artifacts once for test suite."""
        cls.artifacts = load_artifacts()
        cls.demo_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "data", "cs_training_demo.csv"))

    def test_synthetic_data_generation(self):
        """Verify synthetic data adheres to Kaggle Give Me Some Credit schema."""
        df = generate_synthetic_credit_data(n_samples=500, random_state=123)
        self.assertEqual(len(df), 500)
        self.assertIn(TARGET_COLUMN, df.columns)
        for col in FEATURE_COLUMNS:
            self.assertIn(col, df.columns)
            
        # Check target values are purely binary 0 or 1
        unique_targets = set(df[TARGET_COLUMN].unique())
        self.assertTrue(unique_targets.issubset({0, 1}))
        
        # Check missing values exist in expected columns
        self.assertTrue(df["MonthlyIncome"].isna().sum() > 0)
        self.assertTrue(df["NumberOfDependents"].isna().sum() > 0)

    def test_schema_validation(self):
        """Ensure schema validation detects invalid columns or missing target."""
        valid, msg, meta = validate_credit_dataframe(self.demo_df)
        self.assertTrue(valid)
        self.assertTrue(meta["has_target"])
        
        # Test broken df
        broken_df = self.demo_df.drop(columns=[TARGET_COLUMN])
        valid_b, msg_b, _ = validate_credit_dataframe(broken_df)
        self.assertFalse(valid_b)
        self.assertIn("Missing target column", msg_b)

    def test_preprocessor_no_data_leakage(self):
        """Test that preprocessor learns statistics only during fit."""
        train_df = self.demo_df.iloc[:200].copy()
        test_df = self.demo_df.iloc[200:250].copy()
        
        preprocessor = CreditRiskPreprocessor()
        preprocessor.fit(train_df)
        
        # Verify learned attributes
        self.assertTrue(hasattr(preprocessor, "monthly_income_median_"))
        self.assertTrue(hasattr(preprocessor, "number_of_dependents_median_"))
        
        # Transform test data
        X_test_trans = preprocessor.transform(test_df)
        self.assertFalse(X_test_trans.isna().any().any(), "Transformed output must have zero NaNs")
        self.assertIn("TotalDelinquencyEvents", X_test_trans.columns)
        self.assertIn("IsOverUtilized", X_test_trans.columns)

    def test_models_loaded(self):
        """Verify all three models exist in artifacts."""
        self.assertIsNotNone(self.artifacts, "Artifacts should be loaded.")
        models = self.artifacts["models"]
        self.assertIn("Logistic Regression", models)
        self.assertIn("Random Forest", models)
        self.assertIn("XGBoost", models)

    def test_single_applicant_inference(self):
        """Verify inference function returns correct schema and bounded score."""
        applicant = {
            "RevolvingUtilizationOfUnsecuredLines": 0.35,
            "age": 42,
            "NumberOfTime30-59DaysPastDueNotWorse": 0,
            "DebtRatio": 0.30,
            "MonthlyIncome": 6500.0,
            "NumberOfOpenCreditLinesAndLoans": 8,
            "NumberOfTimes90DaysLate": 0,
            "NumberRealEstateLoansOrLines": 1,
            "NumberOfTime60-89DaysPastDueNotWorse": 0,
            "NumberOfDependents": 2.0
        }
        model = self.artifacts["models"]["XGBoost"]
        preprocessor = self.artifacts["preprocessor"]
        
        res = predict_single_applicant(applicant, model, preprocessor)
        self.assertGreaterEqual(res["probability"], 0.0)
        self.assertLessEqual(res["probability"], 1.0)
        self.assertGreaterEqual(res["simulated_credit_score"], 300)
        self.assertLessEqual(res["simulated_credit_score"], 850)
        self.assertIn("Risk", res["risk_tier"])

    def test_threshold_metrics_calculation(self):
        """Verify threshold metrics math."""
        y_true = np.array([0, 0, 0, 1, 1])
        y_prob = np.array([0.1, 0.2, 0.4, 0.6, 0.9])
        
        metrics = _compute_threshold_metrics(y_true, y_prob, threshold=0.5)
        self.assertEqual(metrics["confusion_matrix"]["tp"], 2)
        self.assertEqual(metrics["confusion_matrix"]["tn"], 3)
        self.assertEqual(metrics["confusion_matrix"]["fp"], 0)
        self.assertEqual(metrics["confusion_matrix"]["fn"], 0)
        self.assertEqual(metrics["accuracy"], 1.0)

    def test_shap_explainer(self):
        """Verify SHAP explanation runs and yields contributions."""
        model = self.artifacts["models"]["XGBoost"]
        preprocessor = self.artifacts["preprocessor"]
        test_sample = self.artifacts["test_sample"]
        
        X_trans = preprocessor.transform(test_sample.head(20))
        explainer = CreditRiskExplainer(model, "XGBoost", X_trans)
        
        # Test global
        exp_glob = explainer.explain_global(X_trans, max_samples=20)
        self.assertTrue(len(exp_glob["features"]) > 0)
        
        # Test local
        exp_inst = explainer.explain_instance(X_trans.iloc[[0]])
        self.assertTrue(len(exp_inst["contributions"]) > 0)

if __name__ == "__main__":
    unittest.main()
