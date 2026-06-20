from __future__ import annotations

import importlib
from pathlib import Path

import streamlit as st

from utils.data_loader import load_results, resolve_results_path
from utils.helpers import format_number, inject_css, system_health


ROOT = Path(__file__).parent


PAGES = {
    "Dashboard": ("pages.dashboard", "Executive overview"),
    "Log Analysis": ("pages.log_analysis", "Traffic and category analytics"),
    "Anomaly Detection": ("pages.anomaly_detection", "Security risk review"),
    "Performance Metrics": ("pages.performance_metrics", "Demonstration visualization"),
    "Algorithm Visualization": ("pages.algorithm_visualization", "Divide and conquer workflow"),
    "About Project": ("pages.about_project", "Project documentation"),
}


def render_sidebar(data: dict) -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-block">
                <div class="brand-mark">DL</div>
                <div>
                    <div class="brand-title">Log Analysis</div>
                    <div class="brand-subtitle">Divide and Conquer</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
            key="active_page",
        )

        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
        health = system_health(data)
        st.markdown(
            f"""
            <div class="sidebar-panel">
                <span class="eyebrow">System Health</span>
                <h3>{health["label"]}</h3>
                <p>{health["detail"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric("Total Logs", format_number(data.get("total_lines", 0)))
        st.metric("Anomalies", format_number(data.get("anomaly_count", 0)))

        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        results_path = resolve_results_path(ROOT)
        if results_path:
            st.caption(f"Data source: {results_path.name}")
        else:
            st.caption("Data source: waiting for results.json")

    return selected


def main() -> None:
    st.set_page_config(
        page_title="Distributed Log Analysis Dashboard",
        page_icon="DL",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css(ROOT / "assets" / "styles.css")

    data, load_error = load_results(ROOT)
    selected = render_sidebar(data)

    if load_error:
        st.warning(load_error)

    module_name, description = PAGES[selected]
    st.markdown(
        f"""
        <div class="page-heading">
            <span class="eyebrow">Distributed Log File Analysis System</span>
            <h1>{selected}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = importlib.import_module(module_name)
    page.render(data, ROOT)


if __name__ == "__main__":
    main()
