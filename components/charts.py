"""
CreditRisk AI - Interactive Plotly Visualizations
Provides institutional-grade financial charts: ROC/PR curves, confusion matrices,
risk score gauges, segmentation heatmaps, and SHAP attribution plots.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional

FIN_PALETTE = {
    "navy": "#0F172A",
    "blue": "#0284C7",
    "teal": "#0D9488",
    "amber": "#F59E0B",
    "rose": "#E11D48",
    "indigo": "#6366F1",
    "emerald": "#10B981",
    "slate": "#64748B",
    "light_bg": "#FFFFFF",
    "grid": "#F1F5F9"
}

def create_roc_curves_chart(models_dict: Dict[str, Any]) -> go.Figure:
    """Plots ROC curves for all trained models with AUC legends."""
    fig = go.Figure()
    
    colors = [FIN_PALETTE["blue"], FIN_PALETTE["teal"], FIN_PALETTE["indigo"]]
    
    for idx, (name, m_data) in enumerate(models_dict.items()):
        roc = m_data.get("roc_curve", {})
        fpr = roc.get("fpr", [])
        tpr = roc.get("tpr", [])
        auc = m_data.get("roc_auc", 0.5)
        color = colors[idx % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"{name} (AUC = {auc:.4f})",
            line=dict(color=color, width=2.5),
            hovertemplate="<b>" + name + "</b><br>FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>"
        ))
        
    # Baseline random chance
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Random Classifier (AUC = 0.5000)",
        line=dict(color="#94A3B8", width=1.5, dash="dash"),
        hoverinfo="skip"
    ))
    
    fig.update_layout(
        title="Receiver Operating Characteristic (ROC) Benchmark",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Recall / Sensitivity)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest",
        legend=dict(x=0.45, y=0.08, bgcolor="rgba(255,255,255,0.9)", bordercolor="#E2E8F0", borderwidth=1),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 1]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 1.02]),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig

def create_pr_curves_chart(models_dict: Dict[str, Any], base_rate: float = 0.0668) -> go.Figure:
    """Plots Precision-Recall curves with average precision scores."""
    fig = go.Figure()
    colors = [FIN_PALETTE["blue"], FIN_PALETTE["teal"], FIN_PALETTE["indigo"]]
    
    for idx, (name, m_data) in enumerate(models_dict.items()):
        pr = m_data.get("pr_curve", {})
        recall = pr.get("recall", [])
        precision = pr.get("precision", [])
        pr_auc = m_data.get("pr_auc", 0.0)
        color = colors[idx % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=recall,
            y=precision,
            mode="lines",
            name=f"{name} (PR-AUC = {pr_auc:.4f})",
            line=dict(color=color, width=2.5),
            hovertemplate="<b>" + name + "</b><br>Recall: %{x:.3f}<br>Precision: %{y:.3f}<extra></extra>"
        ))
        
    # Baseline prevalence
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[base_rate, base_rate],
        mode="lines",
        name=f"Class Prevalence ({base_rate*100:.1f}%)",
        line=dict(color="#94A3B8", width=1.5, dash="dash"),
        hoverinfo="skip"
    ))
    
    fig.update_layout(
        title="Precision-Recall Curve (Critical for Imbalanced Delinquency Data)",
        xaxis_title="Recall (Sensitivity to Delinquents)",
        yaxis_title="Precision (Positive Predictive Value)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest",
        legend=dict(x=0.45, y=0.88, bgcolor="rgba(255,255,255,0.9)", bordercolor="#E2E8F0", borderwidth=1),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 1]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 1.02]),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig

def create_confusion_matrix_heatmap(cm_dict: Dict[str, int], title: str = "Confusion Matrix") -> go.Figure:
    """Renders an interactive confusion matrix heatmap with banking labels."""
    tn = cm_dict["tn"]
    fp = cm_dict["fp"]
    fn = cm_dict["fn"]
    tp = cm_dict["tp"]
    
    z = [[tn, fp], [fn, tp]]
    text = [
        [f"True Neg (Non-Def)<br><b>{tn:,}</b>", f"False Pos (False Alarm)<br><b>{fp:,}</b>"],
        [f"False Neg (Missed Def)<br><b>{fn:,}</b>", f"True Pos (Caught Def)<br><b>{tp:,}</b>"]
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=["Predicted Non-Delinquent (0)", "Predicted Delinquent (1)"],
        y=["Actual Non-Delinquent (0)", "Actual Delinquent (1)"],
        text=text,
        texttemplate="%{text}",
        textfont={"size": 13, "family": "Plus Jakarta Sans"},
        colorscale=[
            [0, "#EFF6FF"],
            [0.5, "#93C5FD"],
            [1.0, "#1D4ED8"]
        ],
        showscale=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Decision / Predicted Classification",
        yaxis_title="Ground Truth Outcome",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=50, b=40),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A"),
        yaxis=dict(autorange="reversed")
    )
    return fig

def create_threshold_tuning_chart(y_true: np.ndarray, y_prob: np.ndarray) -> go.Figure:
    """Plots precision, recall, and F1 across decision thresholds (0.05 to 0.95)."""
    thresholds = np.linspace(0.05, 0.95, 91)
    precisions = []
    recalls = []
    f1s = []
    
    for t in thresholds:
        preds = (y_prob >= t).astype(int)
        tp = np.sum((y_true == 1) & (preds == 1))
        fp = np.sum((y_true == 0) & (preds == 1))
        fn = np.sum((y_true == 1) & (preds == 0))
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
        
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        
    best_f1_idx = int(np.argmax(f1s))
    best_f1_thresh = thresholds[best_f1_idx]
    best_f1_val = f1s[best_f1_idx]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thresholds, y=precisions, name="Precision", line=dict(color=FIN_PALETTE["blue"], width=2.5)))
    fig.add_trace(go.Scatter(x=thresholds, y=recalls, name="Recall (Catch Rate)", line=dict(color=FIN_PALETTE["rose"], width=2.5)))
    fig.add_trace(go.Scatter(x=thresholds, y=f1s, name="F1-Score", line=dict(color=FIN_PALETTE["emerald"], width=2.5)))
    
    # Add vertical line for max F1
    fig.add_vline(
        x=best_f1_thresh,
        line_width=1.5,
        line_dash="dot",
        line_color="#475569",
        annotation_text=f"Max F1 ({best_f1_thresh:.2f})",
        annotation_position="top left"
    )
    
    # Add vertical line for standard 0.50
    fig.add_vline(
        x=0.50,
        line_width=1.5,
        line_dash="dash",
        line_color="#CBD5E1",
        annotation_text="Default 0.50",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title="Decision Threshold Trade-Off Simulator",
        xaxis_title="Classification Cutoff Threshold",
        yaxis_title="Metric Score",
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(x=0.02, y=0.15, bgcolor="rgba(255,255,255,0.9)", bordercolor="#E2E8F0"),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0.05, 0.95]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 1.02]),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig

def create_score_gauge(probability: float, simulated_score: int) -> go.Figure:
    """Renders a modern credit risk radial gauge dial."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=simulated_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Borrower Risk Score<br><span style='font-size:0.85em;color:#64748B'>Delinquency Probability: {probability*100:.1f}%</span>", 'font': {'size': 16, 'family': 'Plus Jakarta Sans'}},
        gauge={
            'axis': {'range': [300, 850], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#0F172A", 'thickness': 0.25},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [300, 580], 'color': 'rgba(239, 68, 68, 0.35)'},   # Subprime (Red)
                {'range': [580, 670], 'color': 'rgba(245, 158, 11, 0.35)'},  # Near Prime (Amber)
                {'range': [670, 740], 'color': 'rgba(13, 148, 136, 0.35)'},  # Prime (Teal)
                {'range': [740, 850], 'color': 'rgba(16, 185, 129, 0.40)'}   # Super Prime (Green)
            ],
            'threshold': {
                'line': {'color': "#0F172A", 'width': 4},
                'thickness': 0.75,
                'value': simulated_score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="white",
        height=280,
        margin=dict(l=30, r=30, t=50, b=20),
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F172A")
    )
    return fig

def create_feature_importance_bar(importance_data: List[Dict[str, Any]], title: str = "Global Feature Importance") -> go.Figure:
    """Renders horizontal bar chart for global feature importance."""
    # Top 10 features
    top_items = sorted(importance_data, key=lambda x: x["importance"], reverse=True)[:10]
    top_items.reverse()  # For bottom-up plotting
    
    features = [d["feature"] for d in top_items]
    importances = [d["importance"] for d in top_items]
    
    fig = go.Figure(go.Bar(
        x=importances,
        y=features,
        orientation="h",
        marker=dict(
            color=importances,
            colorscale=[[0, "#93C5FD"], [1.0, "#0284C7"]],
            line=dict(color="#0284C7", width=1)
        ),
        hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Relative Attribution / Importance Weight",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=200, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig

def create_local_attribution_chart(contributions: List[Dict[str, Any]], title: str = "Borrower Risk Factor Decomposition") -> go.Figure:
    """Renders waterfall-like bar chart showing positive vs negative risk drivers."""
    top_items = contributions[:8]
    top_items.reverse()
    
    features = [d["feature"] for d in top_items]
    values = [d["attribution"] for d in top_items]
    colors = [FIN_PALETTE["rose"] if v > 0 else FIN_PALETTE["emerald"] for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker=dict(color=colors, line=dict(width=1, color=colors)),
        hovertemplate="<b>%{y}</b><br>SHAP Contribution: %{x:.4f}<extra></extra>"
    ))
    
    fig.add_vline(x=0, line_width=1.5, line_color="#0F172A")
    
    fig.update_layout(
        title=title,
        xaxis_title="Risk Impact (Red = Escalates Delinquency Risk, Green = Mitigates Risk)",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=200, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig

def create_segmentation_chart(df: pd.DataFrame) -> go.Figure:
    """Calculates and plots empirical delinquency rate across age brackets."""
    clean_df = df.copy()
    if "age" not in clean_df.columns or "SeriousDlqin2yrs" not in clean_df.columns:
        return go.Figure()
        
    bins = [18, 30, 45, 60, 75, 100]
    labels = ["18-29", "30-44", "45-59", "60-74", "75+"]
    clean_df["Age_Bracket"] = pd.cut(clean_df["age"], bins=bins, labels=labels, right=False)
    
    summary = clean_df.groupby("Age_Bracket", observed=True)["SeriousDlqin2yrs"].agg(["mean", "count"]).reset_index()
    summary["Delinquency_Pct"] = summary["mean"] * 100
    
    fig = go.Figure(go.Bar(
        x=summary["Age_Bracket"],
        y=summary["Delinquency_Pct"],
        text=[f"{v:.1f}%<br>({c:,})" for v, c in zip(summary["Delinquency_Pct"], summary["count"])],
        textposition="outside",
        marker=dict(
            color=summary["Delinquency_Pct"],
            colorscale=[[0, "#99F6E4"], [1.0, "#0D9488"]],
            line=dict(color="#0D9488", width=1)
        )
    ))
    
    fig.update_layout(
        title="Observed Delinquency Rate by Borrower Age Segment",
        xaxis_title="Borrower Age Cohort",
        yaxis_title="Historical Delinquency Rate (%)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=50, b=40),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, max(summary["Delinquency_Pct"].max() * 1.3, 10)]),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig

def create_risk_distribution_donut(predicted_probs: np.ndarray, low_thresh: float = 0.10, high_thresh: float = 0.25) -> go.Figure:
    """Plots donut chart of portfolio risk distribution."""
    low_count = int(np.sum(predicted_probs < low_thresh))
    med_count = int(np.sum((predicted_probs >= low_thresh) & (predicted_probs < high_thresh)))
    high_count = int(np.sum(predicted_probs >= high_thresh))
    
    labels = ["Low Risk (Prime)", "Medium Risk (Near-Prime)", "High Risk (Subprime)"]
    values = [low_count, med_count, high_count]
    colors = [FIN_PALETTE["emerald"], FIN_PALETTE["amber"], FIN_PALETTE["rose"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Applicants: %{value:,}<br>Share: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title="Predicted Portfolio Risk Distribution",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#0F172A")
    )
    return fig
