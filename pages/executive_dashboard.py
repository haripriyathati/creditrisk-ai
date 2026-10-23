"""
CreditRisk AI - Page A: Executive Dashboard
Provides senior risk executives with an institutional overview of portfolio health,
observed historical default rates, AI-predicted delinquency exposure, and segment stress.
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Dict, Any

from components.theme import render_header, render_metric_card
from components.charts import (
    create_risk_distribution_donut,
    create_segmentation_chart,
    FIN_PALETTE
)
import plotly.express as px
import plotly.graph_objects as go

def render_executive_dashboard(df: pd.DataFrame, artifacts: Dict[str, Any], is_demo: bool):
    """Renders Page A: Executive Risk Management Dashboard."""
    render_header(
        title="Executive Risk Dashboard",
        subtitle="Portfolio-level credit delinquency surveillance, borrower segment stress, and delinquency forecasts.",
        tag="Executive Overview",
        is_demo=is_demo
    )
    
    # Check if model predictions are available
    active_model_name = st.session_state.get("active_model", "XGBoost")
    model = artifacts["models"].get(active_model_name)
    preprocessor = artifacts["preprocessor"]
    
    # Clean dataframe for scoring
    clean_df = df.copy()
    if "Unnamed: 0" in clean_df.columns:
        clean_df = clean_df.drop(columns=["Unnamed: 0"])
        
    has_target = "SeriousDlqin2yrs" in clean_df.columns
    total_applicants = len(clean_df)
    
    # Interactive Sidebar / Top Filters for drill-down
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Portfolio Surveillance Filters</div>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        min_age, max_age = int(clean_df["age"].min()), int(clean_df["age"].max())
        selected_age = st.slider("Borrower Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
        
    with col_f2:
        income_avail = clean_df["MonthlyIncome"].dropna()
        p99_income = int(np.percentile(income_avail, 99)) if len(income_avail) > 0 else 25000
        selected_income = st.slider("Monthly Gross Income (USD)", min_value=0, max_value=p99_income, value=(0, p99_income), step=500)
        
    with col_f3:
        util_options = ["All Borrowers", "Over-Utilized (> 80%)", "Healthy (< 30%)"]
        selected_util = st.selectbox("Revolving Utilization Cohort", util_options)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter dataset
    filtered_df = clean_df[
        (clean_df["age"] >= selected_age[0]) &
        (clean_df["age"] <= selected_age[1])
    ]
    
    # Apply income filter (keeping NaNs if range includes typical income)
    filtered_df = filtered_df[
        (filtered_df["MonthlyIncome"].isna()) |
        ((filtered_df["MonthlyIncome"] >= selected_income[0]) & (filtered_df["MonthlyIncome"] <= selected_income[1]))
    ]
    
    if selected_util == "Over-Utilized (> 80%)":
        filtered_df = filtered_df[filtered_df["RevolvingUtilizationOfUnsecuredLines"] > 0.8]
    elif selected_util == "Healthy (< 30%)":
        filtered_df = filtered_df[filtered_df["RevolvingUtilizationOfUnsecuredLines"] < 0.3]
        
    if len(filtered_df) == 0:
        st.warning("No applicants match the current filter selection. Resetting to full portfolio view.")
        filtered_df = clean_df
        
    # Model predictions on filtered dataset
    from components.utils import FEATURE_COLUMNS
    X_filt_raw = filtered_df[[c for c in FEATURE_COLUMNS if c in filtered_df.columns]]
    X_filt_trans = preprocessor.transform(X_filt_raw)
    predicted_probs = model.predict_proba(X_filt_trans)[:, 1]
    
    low_thresh = st.session_state.get("low_risk_threshold", 0.10)
    high_thresh = st.session_state.get("high_risk_threshold", 0.25)
    
    high_risk_count = int(np.sum(predicted_probs >= high_thresh))
    avg_pred_prob = float(np.mean(predicted_probs))
    
    # Observed historical delinquency rate
    observed_rate_str = f"{filtered_df['SeriousDlqin2yrs'].mean() * 100:.2f}%" if has_target else "N/A (Unlabelled)"
    observed_count = int(filtered_df['SeriousDlqin2yrs'].sum()) if has_target else 0
    
    # Executive KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            title="Portfolio Volume",
            value=f"{len(filtered_df):,}",
            subtext=f"Total Analyzed ({len(clean_df):,} baseline)",
            accent="blue",
            pill_text="Sample Cohort",
            pill_color="blue"
        )
    with col2:
        render_metric_card(
            title="Observed Delinquency",
            value=observed_rate_str,
            subtext=f"{observed_count:,} Historical Defaults (Ground Truth)",
            accent="amber",
            pill_text="Historical Fact",
            pill_color="amber"
        )
    with col3:
        render_metric_card(
            title="High-Risk Exposure",
            value=f"{high_risk_count:,}",
            subtext=f"{(high_risk_count / len(filtered_df)) * 100:.1f}% Above Cutoff (>{int(high_thresh*100)}%)",
            accent="rose",
            pill_text="Model Forecast",
            pill_color="rose"
        )
    with col4:
        render_metric_card(
            title="Avg Predicted Probability",
            value=f"{avg_pred_prob * 100:.2f}%",
            subtext=f"Calibrated Score ({active_model_name})",
            accent="teal",
            pill_text="Model Estimate",
            pill_color="emerald"
        )
        
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    
    # Visual Analytics Row
    col_chart1, col_chart2 = st.columns([1, 1])
    with col_chart1:
        st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
        donut_fig = create_risk_distribution_donut(predicted_probs, low_thresh, high_thresh)
        st.plotly_chart(donut_fig, use_container_width=True)
        st.caption(f"Risk Tier Cutoffs: Low < {low_thresh*100:.0f}%, Medium {low_thresh*100:.0f}%–{high_thresh*100:.0f}%, High > {high_thresh*100:.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_chart2:
        st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
        seg_fig = create_segmentation_chart(filtered_df)
        st.plotly_chart(seg_fig, use_container_width=True)
        st.caption("Displays empirical default rates across borrower demographic age brackets.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Delinquency Stress by Past-Due Frequency
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Derogatory Event Sensitivity & Historical Loss Frequency</div>', unsafe_allow_html=True)
    
    # Bucket historical 30-59 days past due
    df_chart = filtered_df.copy()
    df_chart["PastDue_30_59_Bucket"] = df_chart["NumberOfTime30-59DaysPastDueNotWorse"].apply(
        lambda x: "0 Events" if x == 0 else ("1 Event" if x == 1 else ("2 Events" if x == 2 else "3+ Events"))
    )
    
    summary_past_due = df_chart.groupby("PastDue_30_59_Bucket", observed=True)["SeriousDlqin2yrs"].agg(["mean", "count"]).reset_index()
    # Sort logically
    order_map = {"0 Events": 0, "1 Event": 1, "2 Events": 2, "3+ Events": 3}
    summary_past_due["sort_order"] = summary_past_due["PastDue_30_59_Bucket"].map(order_map)
    summary_past_due = summary_past_due.sort_values("sort_order")
    summary_past_due["Delinq_Rate_Pct"] = summary_past_due["mean"] * 100
    
    bar_fig = go.Figure(go.Bar(
        x=summary_past_due["PastDue_30_59_Bucket"],
        y=summary_past_due["Delinq_Rate_Pct"],
        text=[f"{v:.1f}%<br>(n={c:,})" for v, c in zip(summary_past_due["Delinq_Rate_Pct"], summary_past_due["count"])],
        textposition="outside",
        marker=dict(
            color=summary_past_due["Delinq_Rate_Pct"],
            colorscale=[[0, "#E0F2FE"], [0.5, "#38BDF8"], [1.0, "#E11D48"]],
            line=dict(color="#0F172A", width=1)
        )
    ))
    bar_fig.update_layout(
        title="Impact of 30-59 Day Derogatory Events on Serious Delinquency Incidence",
        xaxis_title="Number of 30-59 Day Delinquency Occurrences in Last 2 Years",
        yaxis_title="Observed Delinquency Probability (%)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(summary_past_due["Delinq_Rate_Pct"].max() * 1.25, 15)]),
        margin=dict(l=40, r=40, t=50, b=40),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    st.plotly_chart(bar_fig, use_container_width=True)
    st.caption("Demonstrates the non-linear inflection in delinquency risk once a borrower misses a single credit cycle payment.")
    st.markdown('</div>', unsafe_allow_html=True)
