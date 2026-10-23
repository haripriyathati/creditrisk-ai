"""
CreditRisk AI - UI Theme and Visual Styling Components
Provides a modern banking analytics aesthetic: charcoal/navy navigation,
crisp light canvas, restrained teal and blue accents, and institutional micro-typography.
"""

import streamlit as st
from typing import Optional

def apply_fintech_theme():
    """Injects bespoke fintech CSS into the Streamlit session."""
    st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Global Page Canvas */
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* Dark Charcoal/Navy Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #334155 !important;
    }

    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stSlider label {
        color: #94A3B8 !important;
        font-size: 0.82rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Modern Financial Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
        transform: translateY(-2px);
    }

    .metric-card-accent-blue {
        border-top: 4px solid #0284C7;
    }
    
    .metric-card-accent-teal {
        border-top: 4px solid #0D9488;
    }

    .metric-card-accent-amber {
        border-top: 4px solid #F59E0B;
    }

    .metric-card-accent-rose {
        border-top: 4px solid #E11D48;
    }

    .metric-title {
        color: #64748B;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }

    .metric-value {
        color: #0F172A;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
        letter-spacing: -0.02em;
        font-feature-settings: "tnum";
    }

    .metric-subtext {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Badges & Pills */
    .fin-pill {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .fin-pill-blue {
        background-color: #E0F2FE;
        color: #0369A1;
    }

    .fin-pill-emerald {
        background-color: #DCFCE7;
        color: #15803D;
    }

    .fin-pill-amber {
        background-color: #FEF3C7;
        color: #B45309;
    }

    .fin-pill-rose {
        background-color: #FFE4E6;
        color: #BE123C;
    }

    /* Institutional Header Banner */
    .fin-header-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
    }

    .fin-header-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .fin-header-subtitle {
        font-size: 0.9rem;
        color: #64748B;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Card Panels */
    .fin-panel {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.03);
    }

    .fin-panel-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Regulatory & Compliance Callout */
    .compliance-box {
        background-color: #F8FAFC;
        border-left: 4px solid #64748B;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-top: 18px;
        font-size: 0.82rem;
        color: #475569;
        line-height: 1.5;
    }

    /* Mode Banner */
    .mode-banner-demo {
        background-color: #FEF3C7;
        border: 1px solid #FCD34D;
        color: #92400E;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .mode-banner-real {
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Modern Table Styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }

    /* Streamlit Buttons */
    div.stButton > button:first-child {
        background-color: #0284C7;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 18px;
        border: none;
        transition: background-color 0.15s ease;
    }

    div.stButton > button:first-child:hover {
        background-color: #0369A1;
        color: white;
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 18px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #64748B;
        padding: 10px 18px;
        border-radius: 8px 8px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: #0284C7 !important;
        border-bottom: 2px solid #0284C7 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(title: str, subtitle: str, tag: str = "BFSI Production Grade", is_demo: bool = True):
    """Renders a sleek institutional top bar with status tags."""
    banner_html = ""
    if is_demo:
        banner_html = """
        <div class="mode-banner-demo">
            <span><strong>DEMONSTRATION MODE:</strong> Operating on synthetic benchmark data calibrated to the Kaggle "Give Me Some Credit" distribution. Real <code>cs-training.csv</code> can be uploaded anytime via Dataset Explorer.</span>
        </div>
        """
    else:
        banner_html = """
        <div class="mode-banner-real">
            <span><strong>VERIFIED DATASET ACTIVE:</strong> Successfully verified against Kaggle Give Me Some Credit schema and calibrated on uploaded cohort.</span>
        </div>
        """

    st.markdown(banner_html, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="fin-header-container">
        <div>
            <h1 class="fin-header-title">{title}</h1>
            <p class="fin-header-subtitle">{subtitle}</p>
        </div>
        <div>
            <span class="fin-pill fin-pill-blue">{tag}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(
    title: str,
    value: str,
    subtext: str = "",
    accent: str = "blue",
    pill_text: Optional[str] = None,
    pill_color: str = "blue"
):
    """Renders a modern financial metric card."""
    pill_html = f'<span class="fin-pill fin-pill-{pill_color}">{pill_text}</span>' if pill_text else ""
    st.markdown(f"""
    <div class="metric-card metric-card-accent-{accent}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="metric-title">{title}</div>
            {pill_html}
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtext">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

def render_regulatory_disclaimer():
    """Renders mandatory BFSI educational and model governance disclaimer."""
    st.markdown("""
    <div class="compliance-box">
        <strong>Governance & Educational Disclaimer:</strong> This application is developed for collegiate and academic research purposes in machine learning interpretability and credit delinquency modeling. Model outputs and risk scores are statistical estimates, not automated credit decisions. In compliance with fair lending principles (ECOA / Reg B and FCRA), real-world credit decisions require adverse action notices, independent validation, and human-in-the-loop underwriting review.
    </div>
    """, unsafe_allow_html=True)
