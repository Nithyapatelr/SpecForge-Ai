"""
Minimalistic, Clean SpecForge AI Dashboard.
Inspired by clean job/specification search portals: Red header, top taskbar, left refine panel, clean white card listings.

Usage:
    streamlit run scripts/dashboard.py
"""

import os
import sys
import html
import pandas as pd
import requests
import streamlit as st
from sqlalchemy import select, distinct, func

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.config import settings
from specforge.classification.rit_taxonomy import RIT_CATEGORIES
from specforge.failure_logging.mast_taxonomy import MAST_FAILURE_MODES
from specforge.db.session import get_session
from specforge.db.models import Requirement, Classification, AmbiguityFlag, MASRuns, FailureLogs
from scripts.dashboard_helpers import calculate_overall_reduction, process_report_data

# ------------------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SpecForge AI — Requirement Intelligence",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------------------
# 2. Minimalist Clean CSS
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1F2937;
    background-color: #FAFAFA;
}

.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1360px !important;
}

#MainMenu, footer, header {
    visibility: hidden;
}

/* Red Header Bar */
.top-red-header {
    background-color: #DC2626;
    color: #FFFFFF;
    padding: 14px 28px;
    margin: -1rem -1rem 0 -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}

.top-red-header .brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 8px;
}

.top-red-header .brand-subtitle {
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.88);
    font-weight: 400;
}

/* Tabs Bar */
[data-baseweb="tab-list"] {
    background-color: #FFFFFF !important;
    border-bottom: 1px solid #E5E7EB !important;
    padding: 0 16px !important;
    gap: 16px !important;
    margin-bottom: 20px !important;
}

button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    color: #4B5563 !important;
    padding: 12px 14px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}

button[data-baseweb="tab"]:hover {
    color: #DC2626 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #DC2626 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #DC2626 !important;
}

[data-baseweb="tab-highlight"] {
    background-color: #DC2626 !important;
}

/* Filter Section Left Column */
.filter-pane {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 18px 20px;
}

.filter-heading {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 14px;
}

.filter-subheading {
    font-size: 0.82rem;
    font-weight: 600;
    color: #4B5563;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-top: 14px;
    margin-bottom: 8px;
}

/* Active Filter Pills */
.pill-active {
    display: inline-flex;
    align-items: center;
    background-color: #FEF2F2;
    border: 1px solid #F87171;
    color: #DC2626;
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 500;
    margin-right: 8px;
    margin-bottom: 8px;
}

/* Requirement Card */
.req-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}

.req-card:hover {
    border-color: #D1D5DB;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.req-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}

.req-card-title {
    font-size: 0.98rem;
    font-weight: 600;
    color: #DC2626;
    line-height: 1.4;
    text-decoration: none;
}

.req-card-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 8px;
    margin-bottom: 12px;
    font-size: 0.8rem;
    color: #6B7280;
}

.req-card-meta span {
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.req-card-body {
    font-size: 0.88rem;
    color: #374151;
    line-height: 1.55;
}

.req-card-footer {
    margin-top: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    padding-top: 10px;
    border-top: 1px solid #F3F4F6;
}

/* Status Badges */
.badge-risk-high {
    background: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FCA5A5;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
}

.badge-risk-med {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FCD34D;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
}

.badge-risk-low {
    background: #DEF7EC;
    color: #03543F;
    border: 1px solid #84E1BC;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
}

.badge-category {
    background: #F3F4F6;
    color: #1F2937;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 500;
}

/* Stat Box */
.summary-box {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
}

.summary-num {
    font-size: 1.7rem;
    font-weight: 700;
    color: #111827;
}

.summary-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6B7280;
    margin-top: 2px;
}

/* Input Fields & Buttons */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    border: 1px solid #D1D5DB !important;
    border-radius: 6px !important;
    font-size: 0.88rem !important;
}

.stButton > button[kind="primary"] {
    background-color: #DC2626 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 6px 16px !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #B91C1C !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. Top Header Bar
# ------------------------------------------------------------------------------
st.markdown("""
<div class="top-red-header">
    <div class="brand-title">
        <span>SpecForge AI</span>
    </div>
    <div class="brand-subtitle">
        Requirement Intelligence & Multi-Agent Reliability Platform
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

api_url = os.environ.get("API_BASE_URL", settings.api_base_url)


# ------------------------------------------------------------------------------
# Helper: Fetch Available Source Documents
# ------------------------------------------------------------------------------
@st.cache_data(ttl=15)
def get_available_source_docs():
    try:
        with get_session() as session:
            docs = session.execute(
                select(distinct(Requirement.source_doc_id)).order_by(Requirement.source_doc_id)
            ).scalars().all()
            return [d for d in docs if d]
    except Exception:
        return ["sample-01", "ecommerce-01", "banking-01", "gaming-01", "fintech-01"]


# ------------------------------------------------------------------------------
# Helper: Fetch Full Diagnostic Dataset for a Source Document
# ------------------------------------------------------------------------------
def fetch_document_data(doc_id: str):
    try:
        resp = requests.get(f"{api_url}/report/{doc_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct DB fallback if API fails
    try:
        with get_session() as session:
            reqs = session.query(Requirement).filter_by(source_doc_id=doc_id).all()
            items = []
            for r in reqs:
                clf = session.query(Classification).filter_by(requirement_id=r.requirement_id).first()
                amb = session.query(AmbiguityFlag).filter_by(requirement_id=r.requirement_id).first()
                items.append({
                    "requirement_id": r.requirement_id,
                    "atomic_unit_text": r.raw_text,
                    "rit_label": clf.label_id if clf else "Unclassified",
                    "rit_confidence": clf.confidence_score if clf else 0.0,
                    "ambiguity_score": amb.ambiguity_score if amb else 0.0,
                    "ambiguity_reasons": [amb.flag_reason] if (amb and amb.flag_reason) else [],
                })
            return {
                "source_doc_id": doc_id,
                "summary": {
                    "total_requirements": len(items),
                    "high_ambiguity_count": sum(1 for i in items if i["ambiguity_score"] >= 0.6),
                },
                "requirements": items,
            }
    except Exception:
        return None


# ------------------------------------------------------------------------------
# 4. Top Navigation Tabs
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Requirements Search",
    "MAS Experiments",
    "Interactive Sandbox",
    "Taxonomy Reference",
])

# ==============================================================================
# TAB 1: Requirements Search & Explorer (Matching Reference UI)
# ==============================================================================
with tab1:
    available_docs = get_available_source_docs()
    
    col_left, col_right = st.columns([1, 3])

    # Left Column: Refine Your Search (Filters)
    with col_left:
        st.markdown('<div class="filter-heading">Refine your search</div>', unsafe_allow_html=True)
        
        # Document Selection
        st.markdown('<div class="filter-subheading">Source Document</div>', unsafe_allow_html=True)
        selected_doc = st.selectbox(
            "Select Document",
            options=available_docs if available_docs else ["sample-01"],
            index=0,
            label_visibility="collapsed"
        )
        
        # Load the document requirements
        raw_doc_data = fetch_document_data(selected_doc)
        all_reqs = raw_doc_data.get("requirements", []) if raw_doc_data else []
        
        # Category Counts
        category_counts = {}
        for r in all_reqs:
            cat = r.get("rit_label", "Other")
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        st.markdown('<div class="filter-subheading">Category / Intent</div>', unsafe_allow_html=True)
        selected_categories = []
        for cat_name, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if st.checkbox(f"{cat_name} ({count})", value=False, key=f"cat_{cat_name}"):
                selected_categories.append(cat_name)
                
        # Ambiguity Level Filter
        st.markdown('<div class="filter-subheading">Risk / Ambiguity Level</div>', unsafe_allow_html=True)
        high_cnt = sum(1 for r in all_reqs if r.get("ambiguity_score", 0.0) >= 0.6)
        med_cnt = sum(1 for r in all_reqs if 0.3 <= r.get("ambiguity_score", 0.0) < 0.6)
        low_cnt = sum(1 for r in all_reqs if r.get("ambiguity_score", 0.0) < 0.3)
        
        filter_high = st.checkbox(f"High Risk (> 0.60) ({high_cnt})", value=False)
        filter_med = st.checkbox(f"Medium Risk (0.30 - 0.59) ({med_cnt})", value=False)
        filter_low = st.checkbox(f"Low Risk (< 0.30) ({low_cnt})", value=False)

    # Right Column: Search Bar & Requirement Cards List
    with col_right:
        # Active Filter Chips Row
        active_chips_html = f'<div style="display:flex; align-items:center; flex-wrap:wrap; margin-bottom:12px;">'
        active_chips_html += f'<span class="pill-active">Document: {html.escape(selected_doc)}</span>'
        if selected_categories:
            for sc in selected_categories:
                active_chips_html += f'<span class="pill-active">{html.escape(sc)}</span>'
        if filter_high:
            active_chips_html += '<span class="pill-active">High Risk</span>'
        if filter_med:
            active_chips_html += '<span class="pill-active">Medium Risk</span>'
        if filter_low:
            active_chips_html += '<span class="pill-active">Low Risk</span>'
        active_chips_html += '</div>'
        st.markdown(active_chips_html, unsafe_allow_html=True)

        # Search Bar & Sort Row
        s_col1, s_col2 = st.columns([3, 1.2])
        with s_col1:
            search_query = st.text_input(
                "Search",
                placeholder="🔍 Search from requirements list...",
                label_visibility="collapsed"
            )
        with s_col2:
            sort_option = st.selectbox(
                "Sort by",
                options=["Highest Ambiguity", "Lowest Ambiguity", "Highest Confidence", "Original Order"],
                index=0,
                label_visibility="collapsed"
            )

        # Summary Metrics Bar
        tot = len(all_reqs)
        high_amb_count = sum(1 for r in all_reqs if r.get("ambiguity_score", 0.0) >= 0.6)
        amb_rate = round((high_amb_count / tot * 100), 1) if tot > 0 else 0.0
        confs = [r.get("rit_confidence", 0.0) for r in all_reqs if "rit_confidence" in r]
        avg_conf = round(sum(confs) / len(confs), 2) if confs else 0.0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="summary-box"><div class="summary-num">{tot}</div><div class="summary-label">Total Requirements</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="summary-box"><div class="summary-num" style="color:#DC2626;">{high_amb_count}</div><div class="summary-label">High Ambiguity</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="summary-box"><div class="summary-num" style="color:#D97706;">{amb_rate}%</div><div class="summary-label">Ambiguity Rate</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="summary-box"><div class="summary-num" style="color:#059669;">{avg_conf}</div><div class="summary-label">Avg Confidence</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Filter Requirements
        filtered = list(all_reqs)

        if selected_categories:
            filtered = [r for r in filtered if r.get("rit_label") in selected_categories]

        risk_selected = []
        if filter_high:
            risk_selected.append("high")
        if filter_med:
            risk_selected.append("med")
        if filter_low:
            risk_selected.append("low")

        if risk_selected:
            def matches_risk(r):
                s = r.get("ambiguity_score", 0.0)
                if "high" in risk_selected and s >= 0.6:
                    return True
                if "med" in risk_selected and 0.3 <= s < 0.6:
                    return True
                if "low" in risk_selected and s < 0.3:
                    return True
                return False
            filtered = [r for r in filtered if matches_risk(r)]

        if search_query.strip():
            q = search_query.lower()
            filtered = [r for r in filtered if q in r.get("atomic_unit_text", "").lower() or q in r.get("rit_label", "").lower()]

        # Sort
        if sort_option == "Highest Ambiguity":
            filtered = sorted(filtered, key=lambda r: r.get("ambiguity_score", 0.0), reverse=True)
        elif sort_option == "Lowest Ambiguity":
            filtered = sorted(filtered, key=lambda r: r.get("ambiguity_score", 0.0))
        elif sort_option == "Highest Confidence":
            filtered = sorted(filtered, key=lambda r: r.get("rit_confidence", 0.0), reverse=True)

        # Render Cards
        if filtered:
            st.markdown(f"<div style='font-size:0.85rem; color:#6B7280; margin-bottom:12px;'>Showing <strong>{len(filtered)}</strong> of {tot} requirements</div>", unsafe_allow_html=True)
            for idx, r in enumerate(filtered, 1):
                raw_text = r.get("atomic_unit_text", "")
                cat = r.get("rit_label", "Unclassified")
                conf = r.get("rit_confidence", 0.0)
                amb = r.get("ambiguity_score", 0.0)
                reasons = r.get("ambiguity_reasons", [])

                if amb >= 0.6:
                    risk_badge = f'<span class="badge-risk-high">High Risk ({amb:.2f})</span>'
                elif amb >= 0.3:
                    risk_badge = f'<span class="badge-risk-med">Medium Risk ({amb:.2f})</span>'
                else:
                    risk_badge = f'<span class="badge-risk-low">Low Risk ({amb:.2f})</span>'

                reasons_html = ""
                if reasons:
                    clean_reasons = ", ".join(reasons)
                    reasons_html = f'<div style="font-size:0.78rem; color:#DC2626; margin-top:6px;"><strong>Flags:</strong> {html.escape(clean_reasons)}</div>'

                card_html = f"""
                <div class="req-card">
                    <div class="req-card-header">
                        <div class="req-card-title">{html.escape(raw_text)}</div>
                        <div style="font-size:1.1rem; color:#9CA3AF; cursor:pointer;" title="Bookmark">☆</div>
                    </div>
                    <div class="req-card-meta">
                        <span>📁 <strong style="color:#374151;">Category:</strong> {html.escape(cat)}</span>
                        <span>⚡ <strong style="color:#374151;">Confidence:</strong> {conf:.2f}</span>
                        <span>📄 <strong style="color:#374151;">Doc:</strong> {html.escape(selected_doc)}</span>
                    </div>
                    {reasons_html}
                    <div class="req-card-footer">
                        <div>{risk_badge} <span class="badge-category">{html.escape(cat)}</span></div>
                        <div style="font-size:0.75rem; color:#9CA3AF;">ID: {r.get('requirement_id', '')[:8]}...</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("No requirements match the selected filters.")


# ==============================================================================
# TAB 2: MAS Experiments
# ==============================================================================
with tab2:
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    try:
        resp = requests.get(f"{api_url}/experiment/history", timeout=10)
        if resp.status_code == 200:
            history_data = resp.json()
            runs = history_data.get("runs", [])
            avg_reduction = calculate_overall_reduction(runs)

            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-left:4px solid #DC2626; border-radius:8px; padding:20px 24px; margin-bottom:20px;">
                <div style="font-size:0.8rem; font-weight:600; color:#DC2626; text-transform:uppercase; letter-spacing:0.04em;">Core Research Metric</div>
                <div style="font-size:2rem; font-weight:700; color:#111827; margin-top:2px;">{avg_reduction:.1f}% Reduction</div>
                <div style="font-size:0.85rem; color:#6B7280; margin-top:2px;">Average Multi-Agent Execution Failure Reduction (SpecForge-Annotated vs Baseline)</div>
            </div>
            """, unsafe_allow_html=True)

            if runs:
                formatted_runs = []
                for r in runs:
                    formatted_runs.append({
                        "Framework": r.get("framework_name", "").upper(),
                        "Mode": "✅ Annotated" if r.get("annotated") else "⚡ Baseline",
                        "Status": r.get("status", "").capitalize(),
                        "Failures": r.get("failure_count", 0),
                        "Document": r.get("source_doc_id", ""),
                        "Timestamp": r.get("timestamp", ""),
                    })
                st.markdown('<div class="filter-heading">Execution Run History</div>', unsafe_allow_html=True)
                df_history = pd.DataFrame(formatted_runs)
                st.dataframe(df_history, use_container_width=True, height=280)
            else:
                st.info("No experiment runs logged yet. Run `python scripts/run_phase2_demo.py` to record live runs.")
        else:
            st.error(f"API returned status {resp.status_code}")
    except Exception as e:
        st.error(f"Could not connect to API: {e}")


# ==============================================================================
# TAB 3: Interactive Sandbox
# ==============================================================================
with tab3:
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="filter-heading">Live Requirement Analysis</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#6B7280;'>Input custom specification text to inspect RIT classification and smell detection in real time.</p>", unsafe_allow_html=True)

    test_input = st.text_area(
        "Requirement text",
        value="The system should respond quickly to user requests and must allow Senior Doctors to approve prescriptions.",
        height=90,
        label_visibility="collapsed",
    )

    if st.button("Analyze Requirement", type="primary"):
        if test_input.strip():
            with st.spinner("Analyzing..."):
                try:
                    ingest_resp = requests.post(
                        f"{api_url}/ingest",
                        data={"raw_text": test_input, "source_doc_id": "sandbox-live"},
                    )
                    if ingest_resp.status_code == 200:
                        req_ids = ingest_resp.json().get("requirement_ids", [])
                        for rid in req_ids:
                            clf_resp = requests.post(f"{api_url}/classify/{rid}")
                            amb_resp = requests.post(f"{api_url}/ambiguity/{rid}")

                            if clf_resp.status_code == 200 and amb_resp.status_code == 200:
                                clf_data = clf_resp.json()
                                amb_data = amb_resp.json()
                                amb_val = amb_data.get("ambiguity_score", 0.0)

                                if amb_val >= 0.6:
                                    risk_pill = f'<span class="badge-risk-high">High Risk ({amb_val:.2f})</span>'
                                elif amb_val >= 0.3:
                                    risk_pill = f'<span class="badge-risk-med">Medium Risk ({amb_val:.2f})</span>'
                                else:
                                    risk_pill = f'<span class="badge-risk-low">Low Risk ({amb_val:.2f})</span>'

                                st.markdown(f"""
                                <div class="req-card" style="margin-top:16px;">
                                    <div class="req-card-title">"{html.escape(test_input)}"</div>
                                    <div class="req-card-meta">
                                        <span>📁 <strong>Category:</strong> {html.escape(clf_data.get('label_id', ''))}</span>
                                        <span>⚡ <strong>Confidence:</strong> {clf_data.get('confidence_score', 0.0):.2f}</span>
                                    </div>
                                    <div style="margin-top:8px;">{risk_pill} <span class="badge-category">RIT: {html.escape(clf_data.get('label_id', ''))}</span></div>
                                    <div style="font-size:0.8rem; color:#DC2626; margin-top:8px;">
                                        <strong>Smell Reasons:</strong> {html.escape(amb_data.get('flag_reason', 'None detected'))}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Analysis error: {e}")


# ==============================================================================
# TAB 4: Taxonomy Reference
# ==============================================================================
with tab4:
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown('<div class="filter-heading">Requirement Intent Taxonomy (RIT)</div>', unsafe_allow_html=True)
        for cat in RIT_CATEGORIES:
            st.markdown(f"""
            <div class="req-card" style="padding:14px 18px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; color:#111827; font-size:0.9rem;">{html.escape(cat['label_name'])}</span>
                    <span style="color:#DC2626; font-weight:600; font-size:0.8rem;">{html.escape(cat['label_id'])}</span>
                </div>
                <div style="font-size:0.82rem; color:#6B7280; margin-top:4px;">{html.escape(cat['label_definition'])}</div>
            </div>
            """, unsafe_allow_html=True)

    with t_col2:
        st.markdown('<div class="filter-heading">MAST Failure Taxonomy</div>', unsafe_allow_html=True)
        for mode in MAST_FAILURE_MODES:
            st.markdown(f"""
            <div class="req-card" style="padding:14px 18px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; color:#111827; font-size:0.9rem;">{html.escape(mode['mode_name'])}</span>
                    <span style="color:#DC2626; font-weight:600; font-size:0.8rem;">{html.escape(mode['failure_mode_id'])}</span>
                </div>
                <div style="font-size:0.75rem; color:#9CA3AF; margin-top:2px;">{html.escape(mode['category'])}</div>
                <div style="font-size:0.82rem; color:#6B7280; margin-top:4px;">{html.escape(mode['mode_definition'])}</div>
            </div>
            """, unsafe_allow_html=True)
