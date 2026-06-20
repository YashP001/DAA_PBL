from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.charts import log_distribution_pie, status_bar, top_ip_bar
from utils.data_loader import category_dataframe, ip_dataframe, status_dataframe
from utils.helpers import format_number, kpi_card, percentage, section_title, system_health


def render(data: dict, root: Path) -> None:
    total = data.get("total_lines", 0)
    columns = st.columns(5)
    with columns[0]:
        kpi_card("Total Log Entries", format_number(total), "Processed by C backend")
    with columns[1]:
        kpi_card("Total Errors", format_number(data.get("total_errors", 0)), f"{percentage(data.get('total_errors', 0), total)}% of logs", "danger")
    with columns[2]:
        kpi_card("Total Warnings", format_number(data.get("total_warnings", 0)), f"{percentage(data.get('total_warnings', 0), total)}% of logs", "warning")
    with columns[3]:
        kpi_card("Information Logs", format_number(data.get("total_info", 0)), f"{percentage(data.get('total_info', 0), total)}% of logs", "success")
    with columns[4]:
        kpi_card("Total Anomalies", format_number(data.get("anomaly_count", 0)), "IP frequency flags", "danger")

    health = system_health(data)
    st.markdown(
        f"""
        <div class="glass-card health-strip">
            <div>
                <span class="eyebrow">Quick System Health Indicator</span>
                <br><strong>{health["label"]}</strong>
                <p class="muted">{health["detail"]}</p>
            </div>
            <span class="status-pill">Live JSON Loaded</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    categories = category_dataframe(data)
    statuses = status_dataframe(data)
    ips = ip_dataframe(data)

    left, right = st.columns([1, 1])
    with left:
        section_title("Log Severity Distribution", "Error, warning, and information split.")
        st.plotly_chart(log_distribution_pie(categories), use_container_width=True)
    with right:
        section_title("Status Code Distribution", "HTTP response groups found during parsing.")
        st.plotly_chart(status_bar(statuses), use_container_width=True)

    section_title("Top 10 IP Addresses", "Highest request volumes, with anomalies highlighted in red.")
    st.plotly_chart(top_ip_bar(ips, 10), use_container_width=True)

    payload_path = root / "results.json"
    if payload_path.exists():
        st.download_button(
            "Download JSON",
            payload_path.read_bytes(),
            file_name="results.json",
            mime="application/json",
            use_container_width=True,
        )
