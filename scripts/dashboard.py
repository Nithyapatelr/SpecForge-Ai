"""
Streamlit visualization dashboard for SpecForge AI.

Usage:
    streamlit run scripts/dashboard.py
"""

import os
import sys

import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.dashboard_helpers import process_report_data
from specforge.config import settings

st.set_page_config(page_title="SpecForge AI Dashboard", layout="wide")

st.title("🛡️ SpecForge AI — Diagnostic Dashboard")
st.markdown("Classifies requirement intent (RIT Taxonomy) and flags ambiguity before multi-agent execution.")

api_url = os.environ.get("API_BASE_URL", settings.api_base_url)

with st.sidebar:
    st.header("Configuration")
    doc_id_input = st.text_input("Source Document ID", value="sample-01")
    load_btn = st.button("Load Report", type="primary")

if load_btn or doc_id_input:
    try:
        resp = requests.get(f"{api_url}/report/{doc_id_input}", timeout=10)
        if resp.status_code == 200:
            report_data = resp.json()
            processed = process_report_data(report_data)

            # Top Metrics
            m1, m2 = st.columns(2)
            m1.metric("Total Atomic Requirements", processed["total_count"])
            m2.metric("High Ambiguity Flagged (> 0.6)", processed["high_ambiguity_count"], delta_color="inverse")

            st.divider()

            # Chart & Distribution
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📊 RIT Label Distribution")
                dist = processed["label_distribution"]
                if dist:
                    df_chart = pd.DataFrame(list(dist.items()), columns=["Category", "Count"]).set_index("Category")
                    st.bar_chart(df_chart)
                else:
                    st.info("No distribution data available.")

            with col2:
                st.subheader("⚠️ High Ambiguity Requirements (> 0.6)")
                high_amb = [r for r in processed["requirements"] if r.get("ambiguity_score", 0.0) > 0.6]
                if high_amb:
                    for h in high_amb:
                        st.warning(f"**Score {h['ambiguity_score']:.2f}:** {h['atomic_unit_text']}\n\n*Reasons:* {', '.join(h['ambiguity_reasons'])}")
                else:
                    st.success("No high ambiguity requirements flagged!")

            st.divider()

            # Detailed Table
            st.subheader("📋 All Requirements (Sorted by Ambiguity Score Descending)")
            reqs = processed["requirements"]
            if reqs:
                df_reqs = pd.DataFrame(reqs)[["atomic_unit_text", "rit_label", "rit_confidence", "ambiguity_score"]]
                df_reqs.columns = ["Requirement Text", "RIT Label", "Confidence", "Ambiguity Score"]

                # Highlight rows with high ambiguity
                def highlight_high_amb(val):
                    color = "#ffcccc" if isinstance(val, (int, float)) and val > 0.6 else ""
                    return f"background-color: {color}"

                st.dataframe(df_reqs.style.map(highlight_high_amb, subset=["Ambiguity Score"]), use_container_width=True)

        elif resp.status_code == 404:
            st.error(f"No document report found for ID '{doc_id_input}'. Please run pipeline or ingest first.")
        else:
            st.error(f"API Error {resp.status_code}: {resp.text}")

    except Exception as e:
        st.error(f"Could not connect to FastAPI server at {api_url}: {e}")
