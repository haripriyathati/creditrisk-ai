"""
CreditRisk AI - Main Streamlit Application
Explainable Credit Delinquency Prediction and Borrower Risk Profiling
BFSI Production-Grade Analytics Application
"""

import os
import sys
import tempfile

# Ensure Matplotlib cache is located in a writable directory for Windows sandboxes
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_creditrisk"))

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd

from components.theme import apply_fintech_theme
from components.utils import generate_synthetic_credit_data
from models.pipeline import load_artifacts, train_and_evaluate_all_models
from pages.executive_dashboard import render_executive_dashboard
from pages.individual_assessment import render_individual_assessment
from pages.model_performance import render_model_performance
from pages.explainable_ai import render_explainable_ai
from pages.dataset_explorer import render_dataset_explorer

# Page Configuration
st.set_page_config(
    page_title="CreditRisk AI | Banking Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Bespoke Fintech Theme
apply_fintech_theme()

# Ensure Data & Models exist
@st.cache_resource(show_spinner="Initializing CreditRisk AI engine & loading artifacts...")
def initialize_system():
    """Initializes demo dataset and artifacts if not already present."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    demo_path = os.path.join(data_dir, "cs_training_demo.csv")
    
    if not os.path.exists(demo_path):
        os.makedirs(data_dir, exist_ok=True)
        demo_df = generate_synthetic_credit_data(15000, random_state=42)
        demo_df.to_csv(demo_path, index=False)
        
    artifacts = load_artifacts()
    if artifacts is None or "models" not in artifacts or not artifacts["models"]:
        demo_df = pd.read_csv(demo_path) if os.path.exists(demo_path) else generate_synthetic_credit_data(15000, random_state=42)
        train_and_evaluate_all_models(demo_df)
        artifacts = load_artifacts()
        
    return artifacts

artifacts = initialize_system()

# Session State defaults
if "active_dataset_path" not in st.session_state:
    st.session_state["active_dataset_path"] = "data/cs_training_demo.csv"
if "is_demo" not in st.session_state:
    st.session_state["is_demo"] = True
if "active_model" not in st.session_state:
    st.session_state["active_model"] = "XGBoost"
if "low_risk_threshold" not in st.session_state:
    st.session_state["low_risk_threshold"] = 0.10
if "high_risk_threshold" not in st.session_state:
    st.session_state["high_risk_threshold"] = 0.25

# Load active dataset
dataset_path = st.session_state["active_dataset_path"]
if os.path.exists(dataset_path):
    active_df = pd.read_csv(dataset_path)
else:
    active_df = pd.read_csv("data/cs_training_demo.csv")
    st.session_state["is_demo"] = True

# --- SIDEBAR NAVIGATION & SETTINGS ---
with st.sidebar:
    st.markdown("""
    <div style="padding: 12px 0 20px 0; border-bottom: 1px solid #334155;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="background:#0284C7; width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">🏦</div>
            <div>
                <div style="font-weight:700; font-size:1.15rem; color:#F8FAFC; letter-spacing:-0.01em;">CreditRisk AI</div>
                <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;">BFSI Analytics Suite</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;'>Navigation</p>", unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        [
            "Executive Dashboard",
            "Individual Risk Assessment",
            "Model Performance",
            "Explainable AI",
            "Dataset Explorer"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='height: 16px; border-bottom: 1px solid #334155; margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    # Global Model Architecture Selector
    st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;'>Active Scoring Model</p>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "Active Scoring Model",
        list(artifacts["models"].keys()),
        index=list(artifacts["models"].keys()).index(st.session_state["active_model"]) if st.session_state["active_model"] in artifacts["models"] else 0,
        label_visibility="collapsed"
    )
    st.session_state["active_model"] = selected_model
    
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;'>Underwriting Risk Cutoffs</p>", unsafe_allow_html=True)
    
    # Configurable Risk Tiers
    low_cutoff = st.slider(
        "Low Risk (Prime) Upper Bound",
        min_value=0.02,
        max_value=0.20,
        value=float(st.session_state["low_risk_threshold"]),
        step=0.01,
        format="%.2f"
    )
    st.session_state["low_risk_threshold"] = low_cutoff
    
    high_cutoff = st.slider(
        "High Risk (Subprime) Lower Bound",
        min_value=0.15,
        max_value=0.50,
        value=float(st.session_state["high_risk_threshold"]),
        step=0.01,
        format="%.2f"
    )
    st.session_state["high_risk_threshold"] = high_cutoff
    
    st.markdown("<div style='height: 16px; border-bottom: 1px solid #334155; margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    # Active Cohort Badge
    if st.session_state["is_demo"]:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; border-radius: 6px; padding: 10px; font-size: 0.78rem;">
            <strong style="color: #FBBF24;">DEMO DATASET ACTIVE</strong><br>
            <span style="color: #CBD5E1;">15,000 synthetic records calibrated to Give Me Some Credit.</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; border-radius: 6px; padding: 10px; font-size: 0.78rem;">
            <strong style="color: #34D399;">VERIFIED DATASET ACTIVE</strong><br>
            <span style="color: #CBD5E1;">Operating on verified user-uploaded dataset.</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Reset to Benchmark Demo"):
            st.session_state["active_dataset_path"] = "data/cs_training_demo.csv"
            st.session_state["is_demo"] = True
            st.rerun()

# --- PAGE ROUTING ---
if page == "Executive Dashboard":
    render_executive_dashboard(active_df, artifacts, is_demo=st.session_state["is_demo"])
elif page == "Individual Risk Assessment":
    render_individual_assessment(artifacts, is_demo=st.session_state["is_demo"])
elif page == "Model Performance":
    render_model_performance(artifacts, is_demo=st.session_state["is_demo"])
elif page == "Explainable AI":
    render_explainable_ai(artifacts, is_demo=st.session_state["is_demo"])
elif page == "Dataset Explorer":
    render_dataset_explorer(active_df, artifacts, is_demo=st.session_state["is_demo"])
