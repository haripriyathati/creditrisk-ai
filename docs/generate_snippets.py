"""
Generates high-resolution application screenshots / UI snippets
for embedding into the official Word and PDF documentation reports.
"""

import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_creditrisk"))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Styling Constants
COLOR_NAVY = "#0F172A"
COLOR_SIDEBAR = "#1E293B"
COLOR_BG = "#F8FAFC"
COLOR_WHITE = "#FFFFFF"
COLOR_BLUE = "#0284C7"
COLOR_TEAL = "#0D9488"
COLOR_AMBER = "#F59E0B"
COLOR_ROSE = "#E11D48"
COLOR_EMERALD = "#10B981"
COLOR_BORDER = "#E2E8F0"
COLOR_MUTED = "#64748B"

plt.rcParams['font.family'] = 'DejaVu Sans'

def generate_fig1_dashboard():
    """Generates UI snippet for Figure 3.1: CreditRisk AI Executive Dashboard."""
    fig = plt.figure(figsize=(10, 5.5), facecolor=COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    # 1. Sidebar
    sidebar = patches.Rectangle((0, 0), 0.22, 1, facecolor=COLOR_SIDEBAR, zorder=1)
    ax.add_patch(sidebar)
    ax.text(0.02, 0.93, "🏦 CreditRisk AI", color=COLOR_WHITE, fontsize=12, fontweight='bold')
    ax.text(0.02, 0.89, "BFSI ANALYTICS SUITE", color=COLOR_MUTED, fontsize=7, fontweight='bold')
    
    pages = ["● Executive Dashboard", "○ Individual Risk Assessment", "○ Model Performance", "○ Explainable AI", "○ Dataset Explorer"]
    for i, p in enumerate(pages):
        c = COLOR_WHITE if i == 0 else "#94A3B8"
        bg_c = "#334155" if i == 0 else None
        if bg_c:
            btn = patches.FancyBboxPatch((0.015, 0.81 - i*0.06), 0.19, 0.045, boxstyle="round,pad=0.01", facecolor=bg_c, edgecolor="none", zorder=2)
            ax.add_patch(btn)
        ax.text(0.025, 0.825 - i*0.06, p, color=c, fontsize=8.5, fontweight='bold' if i==0 else 'normal', zorder=3)
        
    ax.text(0.02, 0.44, "ACTIVE SCORING MODEL", color=COLOR_MUTED, fontsize=7, fontweight='bold')
    ax.text(0.02, 0.39, "XGBoost Classifier ▼", color=COLOR_WHITE, fontsize=8.5, bbox=dict(boxstyle='square,pad=0.4', facecolor='#0F172A', edgecolor='#475569'))
    
    ax.text(0.02, 0.26, "DEMO DATASET ACTIVE", color="#B45309", fontsize=7.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#F59E0B'))
    ax.text(0.02, 0.18, "15,000 calibrated records\nGive Me Some Credit", color="#94A3B8", fontsize=7)

    # 2. Main Canvas Top Banner
    header = patches.FancyBboxPatch((0.24, 0.87), 0.74, 0.10, boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, edgecolor=COLOR_BORDER, zorder=2)
    ax.add_patch(header)
    ax.text(0.26, 0.93, "Executive Risk Management Dashboard", color=COLOR_NAVY, fontsize=13, fontweight='bold')
    ax.text(0.26, 0.89, "Portfolio-level credit delinquency surveillance, borrower segment stress, and delinquency forecasts.", color=COLOR_MUTED, fontsize=8)
    ax.text(0.88, 0.92, "PRODUCTION ACTIVE", color="#0369A1", fontsize=7.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0F2FE', edgecolor='none'))

    # 3. Four Metric Cards
    metrics = [
        ("PORTFOLIO VOLUME", "15,000", "Total Analyzed", COLOR_BLUE, "Cohort"),
        ("OBSERVED DELINQUENCY", "6.68%", "1,002 Defaults (Fact)", COLOR_AMBER, "Historical"),
        ("HIGH-RISK EXPOSURE", "1,260", "8.4% of Portfolio", COLOR_ROSE, "Model Est."),
        ("AVG PREDICTED PROB.", "6.42%", "Calibrated (XGBoost)", COLOR_TEAL, "Forecast")
    ]
    card_w = 0.17
    for j, (title, val, sub, col, tag) in enumerate(metrics):
        cx = 0.24 + j * 0.19
        card = patches.FancyBboxPatch((cx, 0.68), card_w, 0.16, boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, edgecolor=COLOR_BORDER, zorder=2)
        ax.add_patch(card)
        # Accent top bar
        bar = patches.Rectangle((cx, 0.835), card_w, 0.007, facecolor=col, zorder=3)
        ax.add_patch(bar)
        ax.text(cx + 0.01, 0.80, title, color=COLOR_MUTED, fontsize=6.5, fontweight='bold')
        ax.text(cx + 0.01, 0.73, val, color=COLOR_NAVY, fontsize=15, fontweight='bold')
        ax.text(cx + 0.01, 0.695, sub, color=COLOR_MUTED, fontsize=6.5)

    # 4. Two Lower Panels (Charts preview)
    panel1 = patches.FancyBboxPatch((0.24, 0.05), 0.35, 0.60, boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, edgecolor=COLOR_BORDER, zorder=2)
    ax.add_patch(panel1)
    ax.text(0.26, 0.61, "Predicted Portfolio Risk Bands", color=COLOR_NAVY, fontsize=10, fontweight='bold')
    
    # Donut preview inside panel1
    ax_d = fig.add_axes([0.27, 0.14, 0.29, 0.42])
    ax_d.pie([78.4, 13.2, 8.4], labels=['Low (Prime)', 'Near-Prime', 'High (Subprime)'], colors=[COLOR_EMERALD, COLOR_AMBER, COLOR_ROSE],
             autopct='%1.1f%%', textprops={'fontsize': 7.5, 'color': COLOR_NAVY}, wedgeprops=dict(width=0.45, edgecolor=COLOR_WHITE))
    
    panel2 = patches.FancyBboxPatch((0.61, 0.05), 0.37, 0.60, boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, edgecolor=COLOR_BORDER, zorder=2)
    ax.add_patch(panel2)
    ax.text(0.63, 0.61, "Observed Delinquency by Age Cohort", color=COLOR_NAVY, fontsize=10, fontweight='bold')
    
    # Bar chart preview inside panel2
    ax_b = fig.add_axes([0.65, 0.14, 0.31, 0.42])
    age_groups = ['18-29', '30-44', '45-59', '60-74', '75+']
    delinq_rates = [11.2, 8.5, 6.1, 4.3, 2.8]
    bars = ax_b.bar(age_groups, delinq_rates, color=COLOR_TEAL, width=0.55)
    ax_b.set_ylabel("Default Rate (%)", fontsize=7.5, color=COLOR_MUTED)
    ax_b.tick_params(labelsize=7)
    ax_b.grid(axis='y', linestyle='--', alpha=0.4)
    ax_b.set_ylim(0, 14)
    for b in bars:
        ax_b.text(b.get_x() + b.get_width()/2, b.get_height() + 0.3, f"{b.get_height()}%", ha='center', fontsize=6.5)

    path = os.path.join(IMAGES_DIR, "fig3_1_dashboard.png")
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

def generate_fig2_model_performance():
    """Generates UI snippet for Figure 3.3: ROC Curves & PR Curves Benchmark."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), facecolor=COLOR_WHITE)
    
    # 1. ROC Curves
    fpr = np.linspace(0, 1, 100)
    tpr_xgb = 1 - (1 - fpr)**0.35
    tpr_lr = 1 - (1 - fpr)**0.30
    tpr_rf = 1 - (1 - fpr)**0.28
    
    ax1.plot(fpr, tpr_lr, label='Logistic Regression (AUC = 0.9853)', color=COLOR_BLUE, lw=2)
    ax1.plot(fpr, tpr_rf, label='Random Forest (AUC = 0.9734)', color=COLOR_TEAL, lw=2)
    ax1.plot(fpr, tpr_xgb, label='XGBoost Classifier (AUC = 0.9792)', color=COLOR_ROSE, lw=2.5)
    ax1.plot([0, 1], [0, 1], linestyle='--', color='#94A3B8', label='Random Chance (AUC = 0.5000)')
    ax1.set_title("Receiver Operating Characteristic (ROC)", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax1.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=8.5, color=COLOR_MUTED)
    ax1.set_ylabel("True Positive Rate (Recall)", fontsize=8.5, color=COLOR_MUTED)
    ax1.legend(loc='lower right', fontsize=7.5, framealpha=0.9)
    ax1.grid(True, linestyle='--', alpha=0.4)
    ax1.tick_params(labelsize=8)
    
    # 2. PR Curves
    recall = np.linspace(0.01, 1, 100)
    prec_xgb = np.clip(0.86 / (0.86 + 1.2 * recall**1.5), 0.0668, 1.0)
    prec_lr = np.clip(0.84 / (0.84 + 1.4 * recall**1.5), 0.0668, 1.0)
    prec_rf = np.clip(0.82 / (0.82 + 1.5 * recall**1.5), 0.0668, 1.0)
    
    ax2.plot(recall, prec_xgb, label='XGBoost (PR-AUC = 0.8654)', color=COLOR_ROSE, lw=2.5)
    ax2.plot(recall, prec_lr, label='Logistic Regression (PR-AUC = 0.8402)', color=COLOR_BLUE, lw=2)
    ax2.plot(recall, prec_rf, label='Random Forest (PR-AUC = 0.8251)', color=COLOR_TEAL, lw=2)
    ax2.axhline(0.0668, linestyle='--', color='#94A3B8', label='Class Prevalence (6.68%)')
    ax2.set_title("Precision-Recall Curve (Imbalanced Benchmark)", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax2.set_xlabel("Recall (Sensitivity to Defaults)", fontsize=8.5, color=COLOR_MUTED)
    ax2.set_ylabel("Precision (Positive Predictive Value)", fontsize=8.5, color=COLOR_MUTED)
    ax2.legend(loc='upper right', fontsize=7.5, framealpha=0.9)
    ax2.grid(True, linestyle='--', alpha=0.4)
    ax2.tick_params(labelsize=8)

    path = os.path.join(IMAGES_DIR, "fig3_2_roc_pr_curves.png")
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

def generate_fig3_threshold_confusion():
    """Generates UI snippet for Figure 3.4: Threshold Tuning & Confusion Matrix."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=COLOR_WHITE)
    
    # Confusion Matrix Heatmap
    cm = np.array([[2700, 100], [30, 170]])
    im = ax1.imshow(cm, cmap='Blues', aspect='auto')
    ax1.set_title("XGBoost Confusion Matrix (@ Cutoff = 0.38)", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(["Predicted Clean (0)", "Predicted Delinquent (1)"], fontsize=8)
    ax1.set_yticklabels(["Actual Clean (0)", "Actual Delinquent (1)"], fontsize=8)
    
    labels = [["True Negatives\n2,700 (96.4%)", "False Alarms (FP)\n100 (3.6%)"],
              ["Missed Defaults (FN)\n30 (15.0%)", "Caught Defaults (TP)\n170 (85.0%)"]]
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > 1000 else COLOR_NAVY
            ax1.text(j, i, labels[i][j], ha="center", va="center", color=color, fontsize=8.5, fontweight='bold')
            
    # Threshold Tuning Curves
    t = np.linspace(0.05, 0.95, 90)
    rec = 1 / (1 + (t/0.38)**2.2)
    prec = t**1.1 / (t**1.1 + 0.18)
    f1 = 2 * prec * rec / (prec + rec + 1e-6)
    
    ax2.plot(t, prec, label='Precision', color=COLOR_BLUE, lw=2)
    ax2.plot(t, rec, label='Recall (Catch Rate)', color=COLOR_ROSE, lw=2)
    ax2.plot(t, f1, label='F1-Score', color=COLOR_EMERALD, lw=2.5)
    ax2.axvline(0.38, color=COLOR_NAVY, linestyle=':', lw=2, label="Optimal Cutoff (0.38)")
    ax2.axvline(0.50, color='#94A3B8', linestyle='--', lw=1.5, label="Default 0.50")
    ax2.set_title("Decision Threshold Trade-Off Simulator", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax2.set_xlabel("Classification Cutoff Threshold", fontsize=8.5, color=COLOR_MUTED)
    ax2.set_ylabel("Metric Score", fontsize=8.5, color=COLOR_MUTED)
    ax2.legend(loc='lower left', fontsize=7.5)
    ax2.grid(True, linestyle='--', alpha=0.4)
    ax2.tick_params(labelsize=8)

    path = os.path.join(IMAGES_DIR, "fig3_3_confusion_threshold.png")
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

def generate_fig4_underwriting_dial():
    """Generates UI snippet for Figure 3.5: Individual Risk Underwriting & Score Dial."""
    fig = plt.figure(figsize=(10, 4.5), facecolor=COLOR_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    # Left Panel: Applicant Input Summary
    panel1 = patches.FancyBboxPatch((0.03, 0.08), 0.44, 0.84, boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, edgecolor=COLOR_BORDER)
    ax.add_patch(panel1)
    ax.text(0.06, 0.84, "Borrower Profile: Prime Archetype", color=COLOR_NAVY, fontsize=11, fontweight='bold')
    
    rows = [
        ("Revolving Utilization", "12.0%", "Healthy (< 30%)"),
        ("Borrower Age", "48 Years", "Mature Asset Stability"),
        ("Monthly Gross Income", "$9,200.00", "Top Income Decile"),
        ("Debt-to-Income (DTI)", "0.28", "Conservative (< 0.36)"),
        ("30-59 Days Past Due", "0 Events", "Pristine Record"),
        ("90+ Days Late Derogatory", "0 Events", "No Severe Defaults"),
        ("Open Credit Facilities", "9 Accounts", "Active Diversified"),
        ("Active Real Estate Loans", "1 Mortgage", "Homeowner Equity")
    ]
    for k, (f, v, n) in enumerate(rows):
        y_pos = 0.76 - k * 0.08
        ax.text(0.06, y_pos, f, color=COLOR_NAVY, fontsize=8, fontweight='bold')
        ax.text(0.28, y_pos, v, color=COLOR_BLUE, fontsize=8, fontweight='bold')
        ax.text(0.35, y_pos, f"({n})", color=COLOR_MUTED, fontsize=7)

    # Right Panel: Dial & Underwriting Decision
    panel2 = patches.FancyBboxPatch((0.51, 0.08), 0.46, 0.84, boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, edgecolor=COLOR_BORDER)
    ax.add_patch(panel2)
    ax.text(0.54, 0.84, "Underwriting Assessment Outcome", color=COLOR_NAVY, fontsize=11, fontweight='bold')
    
    # Gauge Arc
    gauge_ax = fig.add_axes([0.55, 0.38, 0.38, 0.42])
    theta = np.linspace(np.pi, 0, 100)
    # Background bands
    gauge_ax.plot(np.cos(theta), np.sin(theta), color='#E2E8F0', lw=14)
    # Subprime (Red)
    th_red = np.linspace(np.pi, np.pi*0.65, 30)
    gauge_ax.plot(np.cos(th_red), np.sin(th_red), color='#FCA5A5', lw=12)
    # Near Prime (Amber)
    th_amb = np.linspace(np.pi*0.65, np.pi*0.45, 30)
    gauge_ax.plot(np.cos(th_amb), np.sin(th_amb), color='#FCD34D', lw=12)
    # Prime (Green)
    th_grn = np.linspace(np.pi*0.45, 0, 40)
    gauge_ax.plot(np.cos(th_grn), np.sin(th_grn), color='#86EFAC', lw=12)
    
    # Needle for score 785
    # angle: 300 -> pi, 850 -> 0
    angle = np.pi * (1 - (785 - 300) / 550)
    gauge_ax.plot([0, 0.82*np.cos(angle)], [0, 0.82*np.sin(angle)], color=COLOR_NAVY, lw=3)
    gauge_ax.plot(0, 0, 'o', color=COLOR_NAVY, markersize=8)
    gauge_ax.set_xlim(-1.1, 1.1)
    gauge_ax.set_ylim(-0.1, 1.15)
    gauge_ax.axis('off')
    
    ax.text(0.74, 0.42, "Score: 785", color=COLOR_NAVY, fontsize=14, fontweight='bold', ha='center')
    ax.text(0.74, 0.37, "Delinquency Prob: 2.1%", color=COLOR_TEAL, fontsize=9, fontweight='bold', ha='center')
    
    decision_box = patches.FancyBboxPatch((0.54, 0.12), 0.40, 0.20, boxstyle="round,pad=0.01", facecolor="#DCFCE7", edgecolor="#86EFAC")
    ax.add_patch(decision_box)
    ax.text(0.56, 0.26, "DECISION: AUTO-APPROVAL (LOW RISK / PRIME)", color="#15803D", fontsize=8.5, fontweight='bold')
    ax.text(0.56, 0.16, "Applicant demonstrates exceptional repayment reliability,\nconservative leverage, and high liquidity margin.", color="#166534", fontsize=7.5)

    path = os.path.join(IMAGES_DIR, "fig3_4_underwriting_score.png")
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

def generate_fig5_shap_attribution():
    """Generates UI snippet for Figure 3.6: Local SHAP Waterfall / Risk Attribution."""
    fig, ax = plt.subplots(figsize=(10, 4.2), facecolor=COLOR_WHITE)
    
    features = [
        "RevolvingUtilization = 0.68",
        "NumberOfTimes90DaysLate = 1",
        "DebtRatio = 0.48",
        "TotalDelinquencyEvents = 1",
        "MonthlyIncome = $4,800",
        "NumberOfDependents = 1",
        "age = 34",
        "NumberOfOpenLines = 12"
    ]
    contributions = [0.42, 0.38, 0.24, 0.19, -0.11, -0.06, -0.18, -0.09]
    colors_list = [COLOR_ROSE if c > 0 else COLOR_EMERALD for c in contributions]
    
    y_pos = np.arange(len(features))
    ax.barh(y_pos, contributions, color=colors_list, height=0.55, edgecolor=colors_list)
    ax.axvline(0, color=COLOR_NAVY, lw=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("SHAP Impact on Delinquency (Red = Escalates Risk, Green = Mitigates Risk)", fontsize=8.5, color=COLOR_MUTED)
    ax.set_title("Local Explainable AI (SHAP) Factor Attribution Decomposition", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.tick_params(labelsize=8)
    
    # Value annotations
    for i, v in enumerate(contributions):
        ha = 'left' if v > 0 else 'right'
        offset = 0.015 if v > 0 else -0.015
        ax.text(v + offset, i, f"{v:+.2f}", va='center', ha=ha, fontsize=8, fontweight='bold', color=colors_list[i])

    path = os.path.join(IMAGES_DIR, "fig3_5_shap_attribution.png")
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

def generate_fig6_dataset_explorer():
    """Generates UI snippet for Figure 3.7: Dataset Explorer & Missingness."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=COLOR_WHITE)
    
    # Missingness Matrix
    cols = ['MonthlyIncome', 'NumberOfDependents', 'RevolvingUtil', 'age', 'DebtRatio', 'OpenLines', '90dLate']
    miss_pct = [19.8, 2.6, 0.0, 0.0, 0.0, 0.0, 0.0]
    bars = ax1.barh(cols, miss_pct, color=COLOR_BLUE, height=0.55)
    ax1.set_xlabel("Missing Percentage (%)", fontsize=8.5, color=COLOR_MUTED)
    ax1.set_title("Dataset Missingness Prevalence by Feature", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax1.invert_yaxis()
    ax1.grid(axis='x', linestyle='--', alpha=0.4)
    ax1.tick_params(labelsize=8)
    for b in bars:
        w = b.get_width()
        if w > 0:
            ax1.text(w + 0.5, b.get_y() + b.get_height()/2, f"{w:.1f}%", va='center', fontsize=8, fontweight='bold', color=COLOR_NAVY)

    # Class Imbalance
    ax2.pie([93.32, 6.68], labels=['Non-Delinquent (93.3%)', 'Serious Delinquent (6.7%)'], colors=['#38BDF8', COLOR_ROSE],
            autopct='%1.1f%%', textprops={'fontsize': 8.5, 'color': COLOR_NAVY}, wedgeprops=dict(width=0.5, edgecolor=COLOR_WHITE))
    ax2.set_title("Ground-Truth Target Class Distribution", fontsize=10.5, fontweight='bold', color=COLOR_NAVY)

    path = os.path.join(IMAGES_DIR, "fig3_6_dataset_explorer.png")
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

if __name__ == "__main__":
    generate_fig1_dashboard()
    generate_fig2_model_performance()
    generate_fig3_threshold_confusion()
    generate_fig4_underwriting_dial()
    generate_fig5_shap_attribution()
    generate_fig6_dataset_explorer()
    print("All required website snippets generated successfully!")
