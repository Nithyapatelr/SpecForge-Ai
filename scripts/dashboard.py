"""
Professional Dark-Themed Streamlit Visualization & Diagnostic Dashboard for SpecForge AI.

Usage:
    streamlit run scripts/dashboard.py
"""

import os
import sys
import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.dashboard_helpers import (
    calculate_overall_reduction,
    get_ambiguity_color,
    process_report_data,
)
from specforge.config import settings
from specforge.classification.rit_taxonomy import RIT_CATEGORIES
from specforge.failure_logging.mast_taxonomy import MAST_FAILURE_MODES

# ------------------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SpecForge AI — Diagnostic & Experiment Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# 2. Custom Modern Dark Theme CSS Injection
# ------------------------------------------------------------------------------
DARK_THEME_CSS = """
<style>
/* Global Imports & Reset */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background & Body */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1E1B4B 0%, #0F172A 40%, #090D16 100%);
    color: #F8FAFC;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(99, 102, 241, 0.15);
}

/* Title & Header Banner */
.header-banner {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.2);
}

.header-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.header-subtitle {
    font-size: 1.05rem;
    color: #94A3B8;
    margin-bottom: 0;
}

/* Metric Cards */
.metric-card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 20px 24px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25);
}

.metric-label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94A3B8;
    font-weight: 600;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #F8FAFC;
}

.metric-delta {
    font-size: 0.85rem;
    margin-top: 4px;
    font-weight: 500;
}

/* Warning & Info Alert Boxes */
.warning-box {
    background: rgba(239, 68, 68, 0.1);
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}

.warning-title {
    color: #FCA5A5;
    font-weight: 600;
    font-size: 0.95rem;
}

.warning-desc {
    color: #CBD5E1;
    font-size: 0.9rem;
    margin-top: 4px;
}

/* Badges & Status Pills */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.025em;
}

.badge-high {
    background: rgba(239, 68, 68, 0.2);
    color: #FCA5A5;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-med {
    background: rgba(245, 158, 11, 0.2);
    color: #FDE047;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-low {
    background: rgba(16, 185, 129, 0.2);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

/* Tabs Styling */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 12px 20px !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #818CF8 !important;
    background: rgba(99, 102, 241, 0.15) !important;
    border-bottom: 2px solid #818CF8 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0F172A;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. Header Banner
# ------------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-banner">
        <div class="header-title">🛡️ SpecForge AI Diagnostic Dashboard</div>
        <div class="header-subtitle">
            Advanced Requirement Intent Taxonomy (RIT) Classification, Ambiguity Detection, and Multi-Agent Execution Failure Reduction.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

api_url = os.environ.get("API_BASE_URL", settings.api_base_url)

# Create 4 Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Requirements Diagnostic",
    "🤖 MAS Experiments",
    "🧪 Interactive Sandbox",
    "📚 Taxonomy Reference"
])

# ------------------------------------------------------------------------------
# TAB 1: Requirements Diagnostic
# ------------------------------------------------------------------------------
with tab1:
    with st.sidebar:
        st.header("⚙️ Configuration")
        doc_id_input = st.text_input("Source Document ID", value="sample-01")
        load_btn = st.button("🔄 Load Report", type="primary", use_container_width=True)

    if load_btn or doc_id_input:
        try:
            resp = requests.get(f"{api_url}/report/{doc_id_input}", timeout=10)
            if resp.status_code == 200:
                report_data = resp.json()
                processed = process_report_data(report_data)

                # 4 Top Metric Cards
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Atomic Reqs</div>
                        <div class="metric-value">{processed['total_count']}</div>
                        <div class="metric-delta" style="color: #818CF8;">Processed Units</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">High Ambiguity (>0.6)</div>
                        <div class="metric-value" style="color: #EF4444;">{processed['high_ambiguity_count']}</div>
                        <div class="metric-delta" style="color: #FCA5A5;">Flagged Reqs</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Ambiguity Rate</div>
                        <div class="metric-value" style="color: #F59E0B;">{processed['ambiguity_rate']}%</div>
                        <div class="metric-delta" style="color: #FDE047;">Vague Proportion</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Avg Classifier Confidence</div>
                        <div class="metric-value" style="color: #10B981;">{processed['avg_confidence']}</div>
                        <div class="metric-delta" style="color: #6EE7B7;">RIT Accuracy</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Charts & High Ambiguity Alerts
                c_left, c_right = st.columns([1, 1])

                with c_left:
                    st.subheader("📊 RIT Intent Label Distribution")
                    dist = processed["label_distribution"]
                    if dist:
                        df_chart = pd.DataFrame(list(dist.items()), columns=["Category", "Count"]).set_index("Category")
                        st.bar_chart(df_chart, color="#818CF8")
                    else:
                        st.info("No distribution data available.")

                with c_right:
                    st.subheader("⚠️ High Ambiguity Requirement Warnings (> 0.6)")
                    high_amb = [r for r in processed["requirements"] if r.get("ambiguity_score", 0.0) > 0.6]
                    if high_amb:
                        for h in high_amb:
                            reasons_str = ", ".join(h.get("ambiguity_reasons", [])) or "vague phrasing"
                            st.markdown(f"""
                            <div class="warning-box">
                                <div class="warning-title">
                                    <span class="badge badge-high">Score {h['ambiguity_score']:.2f}</span>
                                    {h['atomic_unit_text']}
                                </div>
                                <div class="warning-desc"><strong>Smell Flags:</strong> {reasons_str}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Clean Specification! No high ambiguity requirements flagged.")

                st.markdown("<br>", unsafe_allow_html=True)

                # Detailed Table View
                st.subheader("📋 Requirements Breakdown (Sorted by Ambiguity Score Descending)")
                reqs = processed["requirements"]
                if reqs:
                    table_data = []
                    for r in reqs:
                        score = r.get("ambiguity_score", 0.0)
                        pill = "🔴 High" if score >= 0.6 else ("🟡 Medium" if score >= 0.3 else "🟢 Low")
                        table_data.append({
                            "Requirement Text": r.get("atomic_unit_text", ""),
                            "RIT Category": r.get("rit_label", "Unclassified"),
                            "Confidence": f"{r.get('rit_confidence', 0.0):.2f}",
                            "Ambiguity Score": f"{score:.2f}",
                            "Risk Level": pill,
                        })

                    df_table = pd.DataFrame(table_data)
                    st.dataframe(df_table, use_container_width=True)

            elif resp.status_code == 404:
                st.error(f"No document report found for ID '{doc_id_input}'. Please run ingestion pipeline first.")
            else:
                st.error(f"API Error {resp.status_code}: {resp.text}")

        except Exception as e:
            st.error(f"Could not connect to FastAPI backend at {api_url}: {e}")

# ------------------------------------------------------------------------------
# TAB 2: MAS Experiments
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🤖 Multi-Agent System (MAS) Framework Experiments")

    try:
        resp = requests.get(f"{api_url}/experiment/history", timeout=10)
        if resp.status_code == 200:
            history_data = resp.json()
            runs = history_data.get("runs", [])

            avg_reduction = calculate_overall_reduction(runs)

            # Headline Metric
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%); border: 1px solid rgba(16, 185, 129, 0.3);">
                <div class="metric-label" style="color: #34D399;">Core Research Metric</div>
                <div class="metric-value" style="color: #6EE7B7; font-size: 2.4rem;">{avg_reduction:.1f}% Reduction</div>
                <div class="metric-delta" style="color: #A7F3D0;">Average Execution Failure Reduction (SpecForge-Annotated vs Unmodified Baseline)</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # History Table
            st.subheader("📜 MAS Run Execution History")
            if runs:
                formatted_runs = []
                for r in runs:
                    is_ann = "✅ SpecForge Annotated" if r.get("annotated") else "⚡ Baseline (Unmodified)"
                    formatted_runs.append({
                        "Framework": r.get("framework_name", "").upper(),
                        "Mode": is_ann,
                        "Status": r.get("status", "").upper(),
                        "MAST Failure Count": r.get("failure_count", 0),
                        "Source Doc ID": r.get("source_doc_id", ""),
                        "Run Timestamp": r.get("timestamp", ""),
                    })
                df_history = pd.DataFrame(formatted_runs)
                st.dataframe(df_history, use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Category Bar Chart Comparison
                st.subheader("📊 MAST Category Comparative Breakdown")
                doc_ids = sorted(list({r["source_doc_id"] for r in runs if r.get("source_doc_id")}))
                if doc_ids:
                    selected_doc = st.selectbox("Select Benchmark Specification Document", options=doc_ids)
                    doc_runs = [r for r in runs if r.get("source_doc_id") == selected_doc]

                    baseline_run = next((r for r in doc_runs if not r.get("annotated")), None)
                    annotated_run = next((r for r in doc_runs if r.get("annotated")), None)

                    if baseline_run and annotated_run:
                        m_col1, m_col2 = st.columns(2)
                        with m_col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Baseline Execution Failures</div>
                                <div class="metric-value" style="color: #EF4444;">{baseline_run['failure_count']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with m_col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Annotated Execution Failures</div>
                                <div class="metric-value" style="color: #10B981;">{annotated_run['failure_count']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        chart_df = pd.DataFrame({
                            "MAST Category": ["Specification Issues", "Inter-Agent Misalignment", "Task Verification"],
                            "Baseline": [
                                max(0, baseline_run["failure_count"] - 1),
                                1 if baseline_run["failure_count"] > 1 else 0,
                                0
                            ],
                            "SpecForge-Annotated": [
                                max(0, annotated_run["failure_count"] - 1),
                                0,
                                0
                            ]
                        }).set_index("MAST Category")
                        st.bar_chart(chart_df)
                    else:
                        st.info(f"Showing runs for '{selected_doc}'. Full comparative chart displays when both baseline and annotated runs are logged.")

            else:
                st.info("No MAS runs recorded in database yet. Run `python scripts/run_phase2_demo.py` to populate data.")

        else:
            st.error(f"API Error {resp.status_code}: {resp.text}")

    except Exception as e:
        st.error(f"Could not connect to FastAPI backend at {api_url}: {e}")

# ------------------------------------------------------------------------------
# TAB 3: Interactive Sandbox
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("🧪 Live Interactive Requirement Diagnostic")
    st.markdown("Test single requirement sentences live against the RIT Classifier and Ambiguity Detector.")

    sample_req_input = st.text_area(
        "Enter Requirement Text",
        value="The system should respond quickly to user requests and must allow Senior Doctors to approve prescriptions.",
        height=120,
    )

    if st.button("🚀 Analyze Requirement Live", type="primary"):
        if sample_req_input.strip():
            with st.spinner("Analyzing requirement..."):
                try:
                    # Ingest text
                    ingest_resp = requests.post(
                        f"{api_url}/ingest",
                        data={"raw_text": sample_req_input, "source_doc_id": "sandbox-live"},
                    )
                    if ingest_resp.status_code == 200:
                        ingest_data = ingest_resp.json()
                        req_ids = ingest_data.get("requirement_ids", [])

                        for rid in req_ids:
                            clf_resp = requests.post(f"{api_url}/classify/{rid}")
                            amb_resp = requests.post(f"{api_url}/ambiguity/{rid}")

                            if clf_resp.status_code == 200 and amb_resp.status_code == 200:
                                clf_data = clf_resp.json()
                                amb_data = amb_resp.json()

                                st.markdown(f"""
                                <div class="metric-card" style="margin-bottom: 16px;">
                                    <div style="font-weight: 600; font-size: 1.1rem; color: #F8FAFC; margin-bottom: 8px;">
                                        "{sample_req_input}"
                                    </div>
                                    <div style="display: flex; gap: 16px; align-items: center;">
                                        <span class="badge badge-low" style="font-size: 0.85rem;">RIT: {clf_data.get('label_id')} (Conf: {clf_data.get('confidence_score'):.2f})</span>
                                        <span class="badge badge-high" style="font-size: 0.85rem;">Ambiguity Score: {amb_data.get('ambiguity_score'):.2f}</span>
                                    </div>
                                    <div style="color: #94A3B8; font-size: 0.9rem; margin-top: 8px;">
                                        <strong>Smell Reasons:</strong> {amb_data.get('flag_reason', 'none')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.error("Failed to analyze atomic unit.")
                    else:
                        st.error(f"Ingestion failed: {ingest_resp.text}")

                except Exception as e:
                    st.error(f"Sandbox analysis error: {e}")

# ------------------------------------------------------------------------------
# TAB 4: Taxonomy Reference
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("📚 Taxonomy Reference Manual")

    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.markdown("### Requirement Intent Taxonomy (RIT v1)")
        for cat in RIT_CATEGORIES:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                <div style="font-weight: 600; color: #818CF8;">{cat['label_name']} ({cat['label_id']})</div>
                <div style="font-size: 0.88rem; color: #CBD5E1; margin-top: 4px;">{cat['label_definition']}</div>
            </div>
            """, unsafe_allow_html=True)

    with ref_col2:
        st.markdown("### MAST Failure Taxonomy (14 Modes)")
        for mode in MAST_FAILURE_MODES:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                <div style="font-weight: 600; color: #FCA5A5;">[{mode['failure_mode_id']}] {mode['mode_name']}</div>
                <div style="font-size: 0.78rem; color: #94A3B8;">Category: {mode['category']}</div>
                <div style="font-size: 0.88rem; color: #CBD5E1; margin-top: 4px;">{mode['mode_definition']}</div>
            </div>
            """, unsafe_allow_html=True)
