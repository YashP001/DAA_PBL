from __future__ import annotations

from pathlib import Path

import plotly.express as px
import streamlit as st

from utils.charts import apply_layout, category_analysis, log_distribution_pie, status_bar, top_ip_bar
from utils.data_loader import category_dataframe, ip_dataframe, status_dataframe
from utils.helpers import section_title


def render(data: dict, root: Path) -> None:
    categories = category_dataframe(data)
    statuses = status_dataframe(data)
    ips = ip_dataframe(data)

    query = st.text_input("Search IP address", placeholder="Example: 192.168.1.2")
    if query:
        filtered = ips[ips["ip"].str.contains(query, case=False, na=False)]
    else:
        filtered = ips

    left, right = st.columns(2)
    with left:
        section_title("Interactive Pie Chart", "Severity composition across all parsed lines.")
        st.plotly_chart(log_distribution_pie(categories), use_container_width=True)
    with right:
        section_title("Interactive Donut Chart", "Same distribution optimized for quick comparison.")
        st.plotly_chart(log_distribution_pie(categories, hole=0.58), use_container_width=True)

    left, right = st.columns(2)
    with left:
        section_title("Status Code Bar Graph", "2xx, 4xx, and 5xx response groups.")
        st.plotly_chart(status_bar(statuses), use_container_width=True)
    with right:
        section_title("Log Category Analysis", "Absolute volume by log category.")
        st.plotly_chart(category_analysis(categories), use_container_width=True)

    section_title("IP Frequency Analysis", "Searchable request-frequency table and ranked bar chart.")
    st.plotly_chart(top_ip_bar(filtered, 15), use_container_width=True)
    display = filtered.copy()
    if not display.empty:
        display["anomaly"] = display["anomaly"].map(lambda value: "Yes" if value else "No")
    st.dataframe(display, use_container_width=True, hide_index=True)

    if not ips.empty:
        scatter = px.scatter(
            ips,
            x="count",
            y="ip",
            color="risk_status",
            size="count",
            color_discrete_map={"High Risk": "#EF4444", "Normal": "#38BDF8"},
            title="Interactive IP Request Density",
        )
        st.plotly_chart(apply_layout(scatter, height=520), use_container_width=True)
