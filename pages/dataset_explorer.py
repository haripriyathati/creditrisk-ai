"""
CreditRisk AI - Page E: Dataset Explorer & Schema Management
Provides deep exploratory data analysis (EDA), Kaggle Give Me Some Credit schema inspection,
missingness profiling, file uploader for real cs-training.csv, and scored CSV export.
"""

import streamlit as st
import numpy as np
import pandas as pd
import io
from typing import Dict, Any

from components.theme import render_header, render_metric_card
from components.utils import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    validate_credit_dataframe,
    load_data_dictionary
)
from models.pipeline import train_and_evaluate_all_models
from models.inference import predict_batch_portfolio
import plotly.express as px
import plotly.graph_objects as go

def render_dataset_explorer(df: pd.DataFrame, artifacts: Dict[str, Any], is_demo: bool):
    """Renders Page E: Dataset Explorer & Management."""
    render_header(
        title="Dataset Explorer & Data Management",
        subtitle="Kaggle Give Me Some Credit schema analysis, missing value auditing, CSV upload portal, and scored analytical export.",
        tag="Data Governance & EDA",
        is_demo=is_demo
    )
    
    clean_df = df.copy()
    if "Unnamed: 0" in clean_df.columns:
        clean_df = clean_df.drop(columns=["Unnamed: 0"])
        
    data_dict = load_data_dictionary()
    has_target = TARGET_COLUMN in clean_df.columns
    
    # 1. Dataset Dimensions & Quick Stats
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Cohort Overview & Dimension Metrics</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Total Records",
            value=f"{len(clean_df):,}",
            subtext="Borrower Observations",
            accent="blue",
            pill_text="Rows",
            pill_color="blue"
        )
    with c2:
        render_metric_card(
            title="Feature Dimensions",
            value=f"{len(clean_df.columns)}",
            subtext=f"{len(FEATURE_COLUMNS)} Predictors + 1 Target",
            accent="teal",
            pill_text="Columns",
            pill_color="emerald"
        )
    with c3:
        target_rate = (clean_df[TARGET_COLUMN].mean() * 100) if has_target else 0.0
        render_metric_card(
            title="Delinquency Incidence",
            value=f"{target_rate:.2f}%" if has_target else "Unlabelled",
            subtext="Target (SeriousDlqin2yrs = 1)",
            accent="rose",
            pill_text="Class Prevalence",
            pill_color="rose"
        )
    with c4:
        total_missing = clean_df.isna().sum().sum()
        render_metric_card(
            title="Missing Cells",
            value=f"{total_missing:,}",
            subtext=f"{(total_missing / (len(clean_df)*len(clean_df.columns)))*100:.2f}% of Dataset Matrix",
            accent="amber",
            pill_text="Missingness",
            pill_color="amber"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Upload Custom Real Dataset (cs-training.csv)
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">📂 Upload Real Kaggle Training Data (`cs-training.csv`)</div>', unsafe_allow_html=True)
    
    st.write("Upload the official Kaggle *Give Me Some Credit* training file to retrain all models and run live validation:")
    
    uploaded_file = st.file_uploader(
        "Upload Give Me Some Credit CSV File",
        type=["csv"],
        help="Upload cs-training.csv or an equivalent file containing SeriousDlqin2yrs."
    )
    
    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file)
            is_valid, msg, meta = validate_credit_dataframe(user_df)
            
            if is_valid:
                st.success(f"✅ Schema validation passed! Loaded {meta['total_rows']:,} rows and {meta['total_columns']} columns.")
                if st.button("🚀 Train Pipeline on Uploaded Dataset", type="primary"):
                    with st.spinner("Executing end-to-end training and evaluation (Logistic Regression, Random Forest, XGBoost)..."):
                        # Save uploaded file
                        user_df.to_csv("data/cs_training_uploaded.csv", index=False)
                        new_results = train_and_evaluate_all_models(user_df)
                        st.session_state["active_dataset_path"] = "data/cs_training_uploaded.csv"
                        st.session_state["is_demo"] = False
                        st.success("🎉 Models successfully trained and serialized on your uploaded dataset!")
                        st.rerun()
            else:
                st.error(f"❌ Schema Validation Failed: {msg}")
        except Exception as e:
            st.error(f"Error parsing uploaded file: {str(e)}")
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. Missing Value Analysis & Target Balance
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Data Health & Missing Value Profiling</div>', unsafe_allow_html=True)
    
    col_miss, col_target = st.columns([1.3, 1])
    with col_miss:
        missing_counts = clean_df.isna().sum()
        missing_df = pd.DataFrame({
            "Feature": missing_counts.index,
            "Missing Count": missing_counts.values,
            "Missing Pct": (missing_counts.values / len(clean_df)) * 100
        }).sort_values("Missing Pct", ascending=False)
        
        fig_miss = go.Figure(go.Bar(
            x=missing_df["Missing Pct"],
            y=missing_df["Feature"],
            orientation="h",
            text=[f"{p:.1f}% ({c:,})" for p, c in zip(missing_df["Missing Pct"], missing_df["Missing Count"])],
            textposition="outside",
            marker=dict(
                color=missing_df["Missing Pct"],
                colorscale=[[0, "#E0F2FE"], [1.0, "#0284C7"]],
                line=dict(color="#0284C7", width=1)
            )
        ))
        fig_miss.update_layout(
            title="Missing Value Prevalence by Column",
            xaxis_title="Missing Percentage (%)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=180, r=40, t=50, b=40),
            yaxis=dict(autorange="reversed"),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(missing_df["Missing Pct"].max() * 1.3, 10)]),
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
        )
        st.plotly_chart(fig_miss, use_container_width=True)
        
    with col_target:
        if has_target:
            target_counts = clean_df[TARGET_COLUMN].value_counts()
            fig_tgt = go.Figure(data=[go.Pie(
                labels=["Non-Delinquent (0)", "Delinquent (1)"],
                values=[target_counts.get(0, 0), target_counts.get(1, 0)],
                hole=0.6,
                marker=dict(colors=["#38BDF8", "#E11D48"]),
                textinfo="label+percent"
            )])
            fig_tgt.update_layout(
                title="Class Imbalance: Target Distribution",
                paper_bgcolor="white",
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False,
                font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
            )
            st.plotly_chart(fig_tgt, use_container_width=True)
        else:
            st.info("Uploaded data has no target column to profile.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 4. Data Dictionary & Schema Reference
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">Data Dictionary & BFSI Variable Semantics</div>', unsafe_allow_html=True)
    
    dict_rows = []
    for col_name, info in data_dict.items():
        dict_rows.append({
            "Variable Name": col_name,
            "Type": info.get("type", "Predictor"),
            "Description": info.get("description", ""),
            "Benchmark / Guidance": info.get("benchmark", "")
        })
    st.dataframe(pd.DataFrame(dict_rows), use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 5. Export Scored Portfolio Cohort as CSV
    st.markdown('<div class="fin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="fin-panel-title">📥 Export Scored Portfolio Results</div>', unsafe_allow_html=True)
    
    st.write("Generate and download a scored analytical cohort with AI-predicted delinquency probabilities and risk bands:")
    
    active_model_name = st.session_state.get("active_model", "XGBoost")
    model = artifacts["models"].get(active_model_name)
    preprocessor = artifacts["preprocessor"]
    
    # Generate scored batch for download
    export_df = predict_batch_portfolio(
        clean_df.head(2000),  # Top 2000 for fast export
        model=model,
        preprocessor=preprocessor,
        low_risk_threshold=st.session_state.get("low_risk_threshold", 0.10),
        high_risk_threshold=st.session_state.get("high_risk_threshold", 0.25)
    )
    
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    st.download_button(
        label=f"💾 Download Scored Cohort ({len(export_df):,} Rows) as CSV",
        data=csv_bytes,
        file_name=f"creditrisk_ai_scored_{active_model_name.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)
