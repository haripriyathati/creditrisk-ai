"""
CreditRisk AI - Page D: Explainable AI & Model Governance
Provides model transparency via SHAP global importance, local factor attribution,
fair lending compliance insights, and non-causality advisories.
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Dict, Any

from components.theme import render_header, render_metric_card, render_regulatory_disclaimer
from components.charts import (
    create_feature_importance_bar,
    create_local_attribution_chart,
    FIN_PALETTE
)
from models.explainability import CreditRiskExplainer

def render_explainable_ai(artifacts: Dict[str, Any], is_demo: bool):
    """Renders Page D: Explainable AI & Ethical Governance."""
    render_header(
        title="Explainable AI (XAI) & Interpretability",
        subtitle="Unraveling black-box credit scoring models via game-theoretic SHAP values, feature importance, and regulatory governance.",
        tag="Model Governance & XAI",
        is_demo=is_demo
    )
    
    active_model_name = st.session_state.get("active_model", "XGBoost")
    model = artifacts["models"].get(active_model_name)
    preprocessor = artifacts["preprocessor"]
    test_sample = artifacts.get("test_sample")
    
    if test_sample is None:
        st.error("No validation cohort sample found for explainability calculation.")
        return
        
    X_test_trans = preprocessor.transform(test_sample)
    
    # Explainer instance
    explainer = CreditRiskExplainer(model, active_model_name, X_test_trans)
    
    # 1. Global Feature Importance Section
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Global Feature Importance Architecture</div>', unsafe_allow_html=True)
    
    tab_global_shap, tab_gini = st.tabs(["SHAP Mean Absolute Attribution", "Model Native Importance / Weights"])
    
    with tab_global_shap:
        global_shap = explainer.explain_global(X_test_trans, max_samples=200)
        col_fig, col_txt = st.columns([1.4, 1])
        with col_fig:
            fig_shap = create_feature_importance_bar(
                global_shap["importance_ranking"],
                title=f"Global SHAP Importance: {active_model_name}"
            )
            st.plotly_chart(fig_shap, use_container_width=True)
            
        with col_txt:
            st.markdown(f"##### 🎯 Interpretation Summary ({global_shap['method']})")
            st.markdown("""
            SHAP (SHapley Additive exPlanations) computes the average marginal contribution of each financial predictor across all possible feature coalitions.
            
            - **Derogatory History (`TotalDelinquencyEvents`, `NumberOfTimes90DaysLate`)**: Exhibits the highest global attribution. Past delinquency is the strongest historical behavioral predictor of near-future failure.
            - **Revolving Utilization**: High utilization indicates credit stretching and liquidity depletion.
            - **Borrower Age**: Younger borrowers statistically experience higher delinquency rates, while mature borrowers exhibit asset stability.
            """)
            
    with tab_gini:
        results = artifacts["results"]
        native_imp = results["models"][active_model_name].get("feature_importance", {})
        imp_list = [{"feature": k, "importance": v} for k, v in native_imp.items()]
        fig_native = create_feature_importance_bar(
            imp_list,
            title=f"Native Architecture Importance / Coefficients: {active_model_name}"
        )
        st.plotly_chart(fig_native, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Local Applicant Explainability Workbench
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Interactive Local Case Profiler: Applicant Attribution Breakdown</div>', unsafe_allow_html=True)
    
    st.write("Inspect how the model reaches a decision for individual borrowers from the hold-out test set:")
    
    sample_options = [
        f"Borrower #{i+1} | Age: {int(test_sample.iloc[i]['age'])} | Util: {test_sample.iloc[i]['RevolvingUtilizationOfUnsecuredLines']:.2f} | 90d Late: {int(test_sample.iloc[i]['NumberOfTimes90DaysLate'])} | Truth: {'Delinquent' if test_sample.iloc[i]['SeriousDlqin2yrs'] == 1 else 'Non-Delinquent'}"
        for i in range(min(15, len(test_sample)))
    ]
    
    selected_idx_str = st.selectbox("Select Test Applicant for Deep XAI Audit", sample_options)
    selected_row_idx = sample_options.index(selected_idx_str)
    
    selected_raw = test_sample.iloc[[selected_row_idx]]
    selected_trans = X_test_trans.iloc[[selected_row_idx]]
    
    local_exp = explainer.explain_instance(selected_trans)
    pred_p = float(model.predict_proba(selected_trans)[0, 1])
    
    col_l1, col_l2 = st.columns([1.3, 1])
    with col_l1:
        local_fig = create_local_attribution_chart(
            local_exp["contributions"],
            title=f"Local Risk Factor Attribution (Predicted Risk: {pred_p*100:.1f}%)"
        )
        st.plotly_chart(local_fig, use_container_width=True)
        
    with col_l2:
        st.markdown("##### 📄 Applicant Data Snapshot")
        snapshot_df = selected_raw.T.reset_index()
        snapshot_df.columns = ["Predictor", "Recorded Value"]
        st.dataframe(snapshot_df, use_container_width=True, height=270)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. Critical Legal & Scientific Advisory: Correlation vs. Causation
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">⚖️ Causality vs. Correlation: Fair Lending and Model Risk Governance</div>', unsafe_allow_html=True)
    
    st.markdown("""
    > **Fundamental Econometric Principle:** Feature importance scores and high machine learning correlations **do NOT establish causation**.
    
    In banking and retail credit analytics:
    1. **Proxy Discrimination Risk**: High predictive weights on features such as age, revolving debt, or dependents may correlate with socioeconomic or geographic factors. Under the US Equal Credit Opportunity Act (ECOA) and Regulation B, disparate impact must be rigorously monitored.
    2. **Endogeneity & Confounding**: For example, an applicant with a high number of open credit lines may have a higher delinquency rate not *because* opening lines causes default, but because lenders aggressively market credit lines to consumers already in credit distress.
    3. **Adverse Action Requirements**: When an application is declined or priced unfavorably, underwriters must provide specific, actionable reasons (e.g., 'Excessive balance-to-limit ratio') that are economically causal, rather than relying on non-causal statistical artifacts.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_regulatory_disclaimer()
