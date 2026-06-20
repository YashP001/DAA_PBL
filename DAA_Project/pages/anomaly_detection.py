from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.data_loader import ip_dataframe
from utils.helpers import format_number, kpi_card, section_title


def render(data: dict, root: Path) -> None:
    ips = ip_dataframe(data)
    anomalies = ips[ips["anomaly"] == True].copy() if not ips.empty else ips

    columns = st.columns(3)
    with columns[0]:
        kpi_card("Detected Anomalies", format_number(len(anomalies)), "Records flagged by backend", "danger")
    with columns[1]:
        peak = int(anomalies["count"].max()) if not anomalies.empty else 0
        kpi_card("Peak IP Requests", format_number(peak), "Highest suspicious frequency", "warning")
    with columns[2]:
        total = int(anomalies["count"].sum()) if not anomalies.empty else 0
        kpi_card("Suspicious Traffic", format_number(total), "Combined flagged requests", "danger")

    section_title("Alert Cards", "High-frequency IP addresses detected by anomaly rules.")
    if anomalies.empty:
        st.success("No anomaly entries were found in ip_frequency.")
    else:
        top_alerts = anomalies.head(6)
        rows = [st.columns(3), st.columns(3)]
        for index, (_, row) in enumerate(top_alerts.iterrows()):
            with rows[index // 3][index % 3]:
                st.markdown(
                    f"""
                    <div class="alert-card">
                        <span class="risk-pill">High Risk</span>
                        <br><br>
                        <strong>{row["ip"]}</strong>
                        <p>{int(row["count"]):,} requests exceeded the anomaly threshold.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    section_title("Suspicious IP Table", "IP address, request count, and risk status.")
    table = anomalies[["ip", "count", "risk_status"]].rename(
        columns={"ip": "IP Address", "count": "Request Count", "risk_status": "Risk Status"}
    )
    st.dataframe(table, use_container_width=True, hide_index=True)
