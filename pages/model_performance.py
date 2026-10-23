"""
CreditRisk AI - Page C: Model Performance & Discrimination Analysis
Provides exhaustive model benchmarking (Logistic Regression vs Random Forest vs XGBoost),
ROC/PR trade-off curves, decision threshold optimization, and class imbalance education.
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Dict, Any

from components.theme import render_header, render_metric_card
from components.charts import (
    create_roc_curves_chart,
    create_pr_curves_chart,
    create_confusion_matrix_heatmap,
    create_threshold_tuning_chart,
    FIN_PALETTE
)
from models.pipeline import _compute_threshold_metrics

def render_model_performance(artifacts: Dict[str, Any], is_demo: bool):
    """Renders Page C: Model Performance Evaluation & Comparison."""
    render_header(
        title="Model Performance & Validation",
        subtitle="Rigorous empirical evaluation on stratified hold-out validation splits, metric trade-offs, and threshold optimization.",
        tag="Model Governance & Validation",
        is_demo=is_demo
    )
    
    results = artifacts["results"]
    models_dict = results["models"]
    meta = results["metadata"]
    comparison_table = results["comparison_table"]
    
    # 1. Benchmarking Summary Table
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Model Architecture Comparison Benchmark</div>', unsafe_allow_html=True)
    
    comp_df = pd.DataFrame(comparison_table)
    st.dataframe(
        comp_df.style.highlight_max(
            subset=["ROC-AUC", "PR-AUC", "Recall @ Opt.", "F1-Score @ Opt."],
            color="#DCFCE7"
        ).highlight_min(
            subset=["Brier Score"],
            color="#E0F2FE"
        ),
        use_container_width=True
    )
    st.caption("Stratified hold-out split: 80% Training, 20% Evaluation. Preprocessor fitted strictly on training data to prevent leakage.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. In-Depth Class Imbalance BFSI Discussion
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">⚠️ The Class Imbalance Imperative: Why Accuracy is Misleading in Banking</div>', unsafe_allow_html=True)
    
    default_rate = meta["test_default_rate"] * 100
    st.markdown(f"""
    In the benchmark *Give Me Some Credit* cohort, serious credit delinquency occurs in only **{default_rate:.2f}%** of borrowers. 
    This severe class imbalance creates critical evaluation pitfalls for standard machine learning workflows:
    
    1. **The 'Trivial Reject-All-Defaults' Fallacy**: A naive model that classifies every single applicant as non-delinquent achieves **{100 - default_rate:.2f}% Accuracy**, yet it catches **0% of financial defaults**, generating catastrophic credit losses for the lending institution.
    2. **ROC-AUC vs PR-AUC**: While ROC-AUC evaluates the rank-ordering capability across all false-positive rates, **PR-AUC (Precision-Recall Area)** is substantially more informative under extreme imbalance. It directly penalizes false alarms when looking for the rare high-risk default cases.
    3. **Threshold Calibration**: The default classification threshold of `0.50` is calibrated for 50/50 balanced problems. In credit risk, predicting with a cutoff of `0.50` misses the vast majority of defaulting borrowers. The decision threshold must be calibrated using economic cost matrices or Youden's J statistic.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. Discrimination Visualizations (ROC & PR Curves)
    col_roc, col_pr = st.columns(2)
    with col_roc:
        st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
        roc_fig = create_roc_curves_chart(models_dict)
        st.plotly_chart(roc_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_pr:
        st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
        pr_fig = create_pr_curves_chart(models_dict, base_rate=meta["test_default_rate"])
        st.plotly_chart(pr_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 4. Interactive Threshold Optimization Simulator
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Interactive Decision Threshold Tuning & Confusion Matrix</div>', unsafe_allow_html=True)
    
    model_sel_col, thresh_slider_col = st.columns([1, 2])
    with model_sel_col:
        sel_model = st.selectbox(
            "Select Model Architecture for Inspection",
            list(models_dict.keys()),
            index=2 if "XGBoost" in models_dict else 0
        )
        
    chosen_m = models_dict[sel_model]
    y_test_arr = np.array(chosen_m["y_test"])
    y_prob_arr = np.array(chosen_m["y_prob"])
    opt_youden = chosen_m["optimal_threshold_youden"]
    opt_f1 = chosen_m["optimal_threshold_f1"]
    
    with thresh_slider_col:
        selected_thresh = st.slider(
            f"Decision Threshold Cutoff (Youden Opt: {opt_youden:.2f} | Max F1: {opt_f1:.2f})",
            min_value=0.05,
            max_value=0.95,
            value=float(opt_youden),
            step=0.01
        )
        
    # Recompute metrics dynamically at selected threshold
    active_metrics = _compute_threshold_metrics(y_test_arr, y_prob_arr, selected_thresh)
    
    # Threshold Simulator KPI Row
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        render_metric_card(
            title="Recall (Catch Rate)",
            value=f"{active_metrics['recall']*100:.1f}%",
            subtext="Actual Defaults Detected",
            accent="rose",
            pill_text="Sensitivity",
            pill_color="rose"
        )
    with m_col2:
        render_metric_card(
            title="Precision",
            value=f"{active_metrics['precision']*100:.1f}%",
            subtext="Predicted Defaults True",
            accent="blue",
            pill_text="Positive Pred",
            pill_color="blue"
        )
    with m_col3:
        render_metric_card(
            title="F1-Score",
            value=f"{active_metrics['f1']:.3f}",
            subtext="Harmonic Precision/Recall",
            accent="emerald",
            pill_text="Balanced",
            pill_color="emerald"
        )
    with m_col4:
        render_metric_card(
            title="Specificity",
            value=f"{active_metrics['specificity']*100:.1f}%",
            subtext="True Non-Delinquents Kept",
            accent="teal",
            pill_text="Clean Approvals",
            pill_color="emerald"
        )
    with m_col5:
        render_metric_card(
            title="Overall Accuracy",
            value=f"{active_metrics['accuracy']*100:.1f}%",
            subtext=f"Total Correct at {selected_thresh:.2f}",
            accent="amber",
            pill_text="Observed Acc",
            pill_color="amber"
        )
        
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    col_cm, col_curve = st.columns([1, 1.2])
    with col_cm:
        cm_fig = create_confusion_matrix_heatmap(
            active_metrics["confusion_matrix"],
            title=f"{sel_model} Confusion Matrix (@ Cutoff {selected_thresh:.2f})"
        )
        st.plotly_chart(cm_fig, use_container_width=True)
        
    with col_curve:
        tune_fig = create_threshold_tuning_chart(y_test_arr, y_prob_arr)
        st.plotly_chart(tune_fig, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
