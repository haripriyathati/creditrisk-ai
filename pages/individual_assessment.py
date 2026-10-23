"""
CreditRisk AI - Page B: Individual Risk Assessment
Enables underwriters and risk analysts to score individual loan applicants,
inspect real-time delinquency probabilities, explore score gauge meters,
and review local factor attributions with regulatory disclaimers.
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Dict, Any

from components.theme import render_header, render_metric_card, render_regulatory_disclaimer
from components.charts import create_score_gauge, create_local_attribution_chart
from models.inference import predict_single_applicant
from models.explainability import CreditRiskExplainer

# Predefined borrower archetypes for seamless interactive testing
BORROWER_PRESETS = {
    "Prime Borrower (Low Risk)": {
        "RevolvingUtilizationOfUnsecuredLines": 0.12,
        "age": 48,
        "NumberOfTime30-59DaysPastDueNotWorse": 0,
        "DebtRatio": 0.28,
        "MonthlyIncome": 9200.0,
        "NumberOfOpenCreditLinesAndLoans": 9,
        "NumberOfTimes90DaysLate": 0,
        "NumberRealEstateLoansOrLines": 1,
        "NumberOfTime60-89DaysPastDueNotWorse": 0,
        "NumberOfDependents": 2.0
    },
    "Near-Prime / Stretched Borrower (Moderate Risk)": {
        "RevolvingUtilizationOfUnsecuredLines": 0.68,
        "age": 34,
        "NumberOfTime30-59DaysPastDueNotWorse": 1,
        "DebtRatio": 0.46,
        "MonthlyIncome": 4800.0,
        "NumberOfOpenCreditLinesAndLoans": 12,
        "NumberOfTimes90DaysLate": 0,
        "NumberRealEstateLoansOrLines": 1,
        "NumberOfTime60-89DaysPastDueNotWorse": 0,
        "NumberOfDependents": 1.0
    },
    "Distressed Borrower (High Delinquency Exposure)": {
        "RevolvingUtilizationOfUnsecuredLines": 1.15,
        "age": 29,
        "NumberOfTime30-59DaysPastDueNotWorse": 3,
        "DebtRatio": 0.72,
        "MonthlyIncome": 2900.0,
        "NumberOfOpenCreditLinesAndLoans": 6,
        "NumberOfTimes90DaysLate": 2,
        "NumberRealEstateLoansOrLines": 0,
        "NumberOfTime60-89DaysPastDueNotWorse": 1,
        "NumberOfDependents": 3.0
    }
}

def render_individual_assessment(artifacts: Dict[str, Any], is_demo: bool):
    """Renders Page B: Single Applicant Credit Risk Profiling."""
    render_header(
        title="Individual Risk Assessment",
        subtitle="Real-time underwriting evaluation, credit delinquency risk probability, and local factor decomposition.",
        tag="Underwriting Workbench",
        is_demo=is_demo
    )
    
    active_model_name = st.session_state.get("active_model", "XGBoost")
    model = artifacts["models"].get(active_model_name)
    preprocessor = artifacts["preprocessor"]
    test_sample = artifacts.get("test_sample")
    
    # Archetype Preset Selector
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Borrower Profile Quick-Load Archetypes</div>', unsafe_allow_html=True)
    
    preset_col, reset_col = st.columns([3, 1])
    with preset_col:
        selected_preset = st.selectbox(
            "Select Borrower Scenario",
            ["Custom Input"] + list(BORROWER_PRESETS.keys())
        )
    with reset_col:
        st.write("")
        st.write("")
        if st.button("Reset Form"):
            st.session_state["form_preset"] = "Custom Input"
            st.rerun()
            
    # Set default values based on preset
    preset_vals = BORROWER_PRESETS.get(selected_preset, {
        "RevolvingUtilizationOfUnsecuredLines": 0.25,
        "age": 45,
        "NumberOfTime30-59DaysPastDueNotWorse": 0,
        "DebtRatio": 0.35,
        "MonthlyIncome": 6000.0,
        "NumberOfOpenCreditLinesAndLoans": 8,
        "NumberOfTimes90DaysLate": 0,
        "NumberRealEstateLoansOrLines": 1,
        "NumberOfTime60-89DaysPastDueNotWorse": 0,
        "NumberOfDependents": 1.0
    })
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Application Form
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Borrower Financial & Bureau Predictors</div>', unsafe_allow_html=True)
    
    with st.form("applicant_scoring_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 💳 Credit Utilization & Debt")
            revolving_util = st.number_input(
                "Revolving Utilization (0.0 to 1.0+)",
                min_value=0.0,
                max_value=15.0,
                value=float(preset_vals["RevolvingUtilizationOfUnsecuredLines"]),
                step=0.05,
                help="Total balance on credit cards divided by total credit limits. Values > 1.0 denote over-limit balances."
            )
            debt_ratio = st.number_input(
                "Debt-to-Income Ratio (DTI)",
                min_value=0.0,
                max_value=500.0,
                value=float(preset_vals["DebtRatio"]),
                step=0.05,
                help="Monthly debt obligations and living costs divided by monthly gross income."
            )
            monthly_income = st.number_input(
                "Monthly Gross Income (USD)",
                min_value=0.0,
                max_value=1000000.0,
                value=float(preset_vals["MonthlyIncome"]) if preset_vals["MonthlyIncome"] is not None else 5400.0,
                step=250.0,
                help="Applicant's monthly gross income in USD. If unknown, leave blank/zero."
            )
            income_is_unreported = st.checkbox("Income Unreported / Thin-File", value=False)
            if income_is_unreported:
                monthly_income = np.nan
                
        with col2:
            st.markdown("##### 📅 Delinquency History (Last 2 Years)")
            late_30 = st.number_input(
                "30-59 Days Past Due Count",
                min_value=0,
                max_value=15,
                value=int(preset_vals["NumberOfTime30-59DaysPastDueNotWorse"]),
                step=1,
                help="Times borrower has been 30-59 days past due but no worse in the last 2 years."
            )
            late_60 = st.number_input(
                "60-89 Days Past Due Count",
                min_value=0,
                max_value=15,
                value=int(preset_vals["NumberOfTime60-89DaysPastDueNotWorse"]),
                step=1,
                help="Times borrower has been 60-89 days past due but no worse in the last 2 years."
            )
            late_90 = st.number_input(
                "90+ Days Late Derogatory Count",
                min_value=0,
                max_value=15,
                value=int(preset_vals["NumberOfTimes90DaysLate"]),
                step=1,
                help="Times borrower has been 90 days or more past due. Primary leading indicator of severe delinquency."
            )
            
        with col3:
            st.markdown("##### 👤 Demographics & Facilities")
            age = st.number_input(
                "Borrower Age (Years)",
                min_value=18,
                max_value=105,
                value=int(preset_vals["age"]),
                step=1
            )
            open_lines = st.number_input(
                "Number of Open Credit Lines & Loans",
                min_value=0,
                max_value=60,
                value=int(preset_vals["NumberOfOpenCreditLinesAndLoans"]),
                step=1,
                help="Count of active installment loans and revolving credit lines."
            )
            real_estate = st.number_input(
                "Number of Real Estate Loans / Mortgages",
                min_value=0,
                max_value=25,
                value=int(preset_vals["NumberRealEstateLoansOrLines"]),
                step=1
            )
            dependents = st.number_input(
                "Number of Dependents",
                min_value=0,
                max_value=15,
                value=int(preset_vals["NumberOfDependents"]),
                step=1
            )
            
        submit_btn = st.form_submit_button("⚡ Evaluate Applicant Risk Score", use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process Assessment
    applicant_dict = {
        "RevolvingUtilizationOfUnsecuredLines": revolving_util,
        "age": age,
        "NumberOfTime30-59DaysPastDueNotWorse": late_30,
        "DebtRatio": debt_ratio,
        "MonthlyIncome": monthly_income,
        "NumberOfOpenCreditLinesAndLoans": open_lines,
        "NumberOfTimes90DaysLate": late_90,
        "NumberRealEstateLoansOrLines": real_estate,
        "NumberOfTime60-89DaysPastDueNotWorse": late_60,
        "NumberOfDependents": dependents
    }
    
    low_thresh = st.session_state.get("low_risk_threshold", 0.10)
    high_thresh = st.session_state.get("high_risk_threshold", 0.25)
    
    scoring_result = predict_single_applicant(
        applicant_data=applicant_dict,
        model=model,
        preprocessor=preprocessor,
        low_risk_threshold=low_thresh,
        high_risk_threshold=high_thresh
    )
    
    prob = scoring_result["probability"]
    score = scoring_result["simulated_credit_score"]
    risk_tier = scoring_result["risk_tier"]
    status = scoring_result["status"]
    
    # Results Banner
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="fin-panel-title">Assessment Summary: <span style="color:{scoring_result["color"]};">{risk_tier}</span></div>', unsafe_allow_html=True)
    
    col_res1, col_res2, col_res3 = st.columns([1, 1.2, 1])
    with col_res1:
        render_metric_card(
            title="Delinquency Probability",
            value=f"{prob*100:.1f}%",
            subtext=f"Classified by {active_model_name}",
            accent="rose" if prob >= high_thresh else ("amber" if prob >= low_thresh else "teal"),
            pill_text=status,
            pill_color="rose" if prob >= high_thresh else ("amber" if prob >= low_thresh else "emerald")
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        render_metric_card(
            title="Estimated Credit Score",
            value=f"{score}",
            subtext="Mapped Range: 300 to 850",
            accent="blue",
            pill_text="FICO Proxy",
            pill_color="blue"
        )
        
    with col_res2:
        gauge_fig = create_score_gauge(prob, score)
        st.plotly_chart(gauge_fig, use_container_width=True)
        
    with col_res3:
        st.markdown("##### 📋 Underwriting Recommendation")
        if prob < low_thresh:
            st.success("✅ **ELIGIBLE FOR AUTO-APPROVAL**: Applicant demonstrates exceptional repayment history, low revolving utilization, and balanced debt-to-income.")
        elif prob < high_thresh:
            st.warning("⚠️ **MANUAL UNDERWRITING REQUIRED**: Applicant exhibits moderate debt service strain or minor historical delinquency. Verification of income and secondary collateral suggested.")
        else:
            st.error("🛑 **ELEVATED DEFAULT RISK**: Probability of 90+ day delinquency exceeds tolerance limit. Adverse action or credit enhancement required.")
            
        st.caption(f"Configured Thresholds: Low Risk < {low_thresh*100:.0f}% | High Risk ≥ {high_thresh*100:.0f}%")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Local Explainability Factor Breakdown
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Explainable AI: Key Factors Influencing This Prediction</div>', unsafe_allow_html=True)
    
    # Transform row
    transformed_row = pd.DataFrame([scoring_result["transformed_features"]])
    
    # Background for XAI
    bg_df = preprocessor.transform(test_sample) if test_sample is not None else transformed_row
    explainer = CreditRiskExplainer(model, active_model_name, bg_df)
    local_explanation = explainer.explain_instance(transformed_row)
    
    col_xai1, col_xai2 = st.columns([1.3, 1])
    with col_xai1:
        local_fig = create_local_attribution_chart(local_explanation["contributions"])
        st.plotly_chart(local_fig, use_container_width=True)
        
    with col_xai2:
        st.markdown("##### 🔍 Top Risk Escalation Drivers")
        if local_explanation["top_risk_factors"]:
            for item in local_explanation["top_risk_factors"][:3]:
                st.markdown(f"- 🔴 **{item['feature']}**: Observed value `{item['value']:.2f}` pushes estimated risk **UP** (Attribution: `+{item['attribution']:.3f}`).")
        else:
            st.markdown("*No dominant risk-escalating factors identified.*")
            
        st.markdown("##### 🛡️ Top Risk Mitigating Drivers")
        if local_explanation["top_protective_factors"]:
            for item in local_explanation["top_protective_factors"][:3]:
                st.markdown(f"- 🟢 **{item['feature']}**: Observed value `{item['value']:.2f}` pulls estimated risk **DOWN** (Attribution: `{item['attribution']:.3f}`).")
        else:
            st.markdown("*No strong protective factors identified.*")
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Legal & Compliance Disclaimer
    render_regulatory_disclaimer()
