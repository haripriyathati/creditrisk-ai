# CreditRisk AI: Explainable Credit Delinquency Prediction and Borrower Risk Profiling

An institutional-grade Banking, Financial Services, and Insurance (BFSI) machine learning web application engineered for predicting serious credit delinquency (90+ days past due within a 2-year window) based on the Kaggle *Give Me Some Credit* benchmark dataset.

---

## 1. Project Overview & Objective

Credit delinquency poses substantial risk to consumer credit portfolios. The primary objective of this project is to build an explainable, end-to-end credit scoring engine that:
1. Predicts the probability of serious delinquency (`SeriousDlqin2yrs`) using historical credit bureau and demographic indicators.
2. Formulates risk bands (Low / Prime, Medium / Near-Prime, High / Subprime) with configurable underwriting thresholds.
3. Overcomes severe class imbalance (~6.7% default incidence) via stratified validation, class weighting, PR-AUC evaluation, and Youden's J threshold optimization.
4. Provides Explainable AI (XAI) using SHAP (SHapley Additive exPlanations) for both portfolio-wide factor attribution and individual borrower adverse action profiling.
5. Provides a synthetic demo mode calibrated to Give Me Some Credit distributions, while offering a live CSV upload and model retraining portal for real Kaggle data.

---

## 2. System Architecture & Project Structure

```
creditrisk-ai/
├── data/
│   ├── cs_training_demo.csv          # 15,000 synthetic records calibrated to Give Me Some Credit
│   └── data_dictionary.json          # Complete BFSI variable metadata and typical ranges
├── models/
│   ├── preprocessor.py               # Leakage-free preprocessing, missingness flags, outlier treatment
│   ├── pipeline.py                   # Stratified training for Logistic Regression, Random Forest, XGBoost
│   ├── explainability.py             # SHAP TreeExplainer & LinearExplainer with fallback
│   └── inference.py                  # Single applicant scoring & portfolio batch inference
├── artifacts/                        # Serialized Joblib pipelines, models, and evaluation results
│   ├── preprocessor.joblib
│   ├── logistic_regression.joblib
│   ├── random_forest.joblib
│   ├── xgboost.joblib
│   ├── evaluation_results.joblib
│   └── test_sample_df.joblib
├── components/
│   ├── theme.py                      # Fintech design system (dark navy sidebar, light canvas)
│   ├── charts.py                     # Plotly ROC/PR curves, confusion matrices, dials, and heatmaps
│   └── utils.py                      # Schema validation and synthetic generator
├── pages/
│   ├── executive_dashboard.py        # Portfolio surveillance, KPIs, observed vs predicted rates
│   ├── individual_assessment.py      # Interactive underwriting form, risk score dial, local XAI
│   ├── model_performance.py          # LR vs RF vs XGBoost benchmarking, ROC-AUC, PR-AUC, tuning
│   ├── explainable_ai.py             # Global SHAP beeswarm/bars, applicant attribution, causation notes
│   └── dataset_explorer.py           # Kaggle schema inspection, missingness, CSV upload, CSV export
├── tests/
│   └── test_pipeline.py              # Automated unit and integration test suite
├── app.py                            # Streamlit entry point
├── requirements.txt                  # Full pinned dependencies
└── run_app.bat                       # One-click Windows launcher
```

---

## 3. Dataset Predictor Dictionary

| Predictor Name | Type | Description | Industry Benchmark |
| :--- | :--- | :--- | :--- |
| **`SeriousDlqin2yrs`** | Binary Target | Person experienced 90+ days past due delinquency in 2 years (0 or 1). | ~6.68% historical default rate |
| **`RevolvingUtilizationOfUnsecuredLines`** | Float | Credit card and line-of-credit balances divided by credit limits. | < 0.30 Healthy, > 0.80 Strained |
| **`age`** | Integer | Age of borrower in completed years. | Median ~52 years |
| **`NumberOfTime30-59DaysPastDueNotWorse`** | Integer | Times borrower was 30-59 days past due (no worse) in last 2 years. | 0 for prime borrowers |
| **`DebtRatio`** | Float | Monthly debt payments divided by gross monthly income. | < 0.36 Prime DTI |
| **`MonthlyIncome`** | Float | Gross monthly income in USD (~20% missing in raw benchmark). | Median ~$5,400 |
| **`NumberOfOpenCreditLinesAndLoans`** | Integer | Active installment loans and revolving accounts. | Median ~8 accounts |
| **`NumberOfTimes90DaysLate`** | Integer | Times borrower was 90+ days late. Major derogatory indicator. | 0 for standard risk |
| **`NumberRealEstateLoansOrLines`** | Integer | Mortgage and real estate equity lines of credit. | Median ~1 loan |
| **`NumberOfTime60-89DaysPastDueNotWorse`** | Integer | Times borrower was 60-89 days late (no worse) in last 2 years. | 0 for standard risk |
| **`NumberOfDependents`** | Float | Family dependents excluding applicant (~2.6% missing). | Mean ~0.75 |

---

## 4. Machine Learning Engineering Rigor

### A. Data Leakage Prevention
Preprocessing statistics (such as median imputation for `MonthlyIncome` and `NumberOfDependents`, as well as standard scaling parameters) are fitted strictly on the training partition ($X_{\text{train}}$) inside `CreditRiskPreprocessor` and applied downstream to $X_{\text{test}}$ and real-time inference inputs.

### B. Outlier & Special Code Treatment
- **Special Kaggle Missing Codes (96, 98)**: Mapped to delinquency ceilings rather than parsed as numeric counts of 98 late payments.
- **Revolving Utilization**: Capped at 10.0 to prevent extreme data entry anomalies from distorting gradient updates.
- **Missingness Indicators**: Missingness in income and dependents is explicitly modeled via binary flags (`MonthlyIncome_Missing`, `NumberOfDependents_Missing`).

### C. Addressing Extreme Class Imbalance
With only ~6.7% positive class prevalence:
- **Accuracy Fallacy**: A dummy classifier predicting all non-delinquent achieves 93.3% accuracy but catastrophic financial losses.
- **Stratified Split**: Preserves positive class prevalence across training and evaluation splits.
- **Cost-Weighted Estimators**: Models utilize balanced class weights (`class_weight='balanced_subsample'` in Random Forest and `scale_pos_weight` in XGBoost).
- **Discrimination Metrics**: Prioritizes ROC-AUC, PR-AUC (Average Precision), and Brier Score.
- **Threshold Optimization**: Decision threshold is tuned using Youden's J statistic ($J = \text{TPR} - \text{FPR}$) and max F1-score rather than assuming arbitrary 0.50 cutoff.

---

## 5. Model Architecture Benchmark

| Model | ROC-AUC | PR-AUC | Brier Score | Optimal Cutoff (Youden) | Recall @ Opt. | Precision @ Opt. | F1-Score @ Opt. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (L2)** | ~0.985 | ~0.840 | ~0.045 | 0.44 | 94.5% | 48.0% | 0.636 |
| **Random Forest (120 Trees)** | ~0.973 | ~0.825 | ~0.048 | 0.42 | 87.5% | 51.5% | 0.648 |
| **XGBoost (Gradient Boosted)**| ~0.979 | ~0.865 | ~0.038 | 0.38 | 85.0% | 62.9% | 0.723 |

*(Evaluated on held-out test split of 3,000 stratified samples. Authentic metrics derived from calibrated validation split).*

---

## 6. How to Run Locally

### Prerequisites
- Windows 10/11
- Python 3.11+ (installed in `.venv` via `uv` or system Python)

### Quick Launch
Simply double-click the included batch launcher:
```cmd
run_app.bat
```

Or run via command line:
```cmd
cd creditrisk-ai
.\.venv\Scripts\streamlit run app.py --server.port 8501
```
Then navigate to: **`http://localhost:8501`**

### Running the Test Suite
```cmd
.\.venv\Scripts\python -m unittest tests/test_pipeline.py
```

---

## 7. Model Governance & Fair Lending Compliance Note
In compliance with the **Equal Credit Opportunity Act (ECOA / Regulation B)** and the **Fair Credit Reporting Act (FCRA)**:
1. **Correlation vs. Causation**: High SHAP importance indicates statistical predictive association, not economic causality.
2. **Adverse Action**: When adverse credit actions are taken, applicants must receive clear and specific reasons.
3. **Model Risk Governance (SR 11-7)**: Automated ML outputs serve as decision-support heuristics and require human underwriting review.
