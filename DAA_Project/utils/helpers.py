from __future__ import annotations

from pathlib import Path

import streamlit as st


def inject_css(path: Path) -> None:
    if path.exists():
        st.markdown(f"<style>{path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def format_number(value: int | float) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return f"{int(number):,}"


def percentage(part: int | float, total: int | float) -> float:
    if not total:
        return 0.0
    return round((part / total) * 100, 2)


def system_health(data: dict) -> dict[str, str]:
    total = data.get("total_lines", 0) or 0
    anomalies = data.get("anomaly_count", 0) or 0
    errors = data.get("total_errors", 0) or 0
    anomaly_rate = anomalies / total if total else 0
    error_rate = errors / total if total else 0

    if anomaly_rate > 0.001 or error_rate > 0.15:
        return {"label": "Attention Required", "detail": "Elevated anomaly or error density detected."}
    if error_rate > 0.05:
        return {"label": "Watch", "detail": "Traffic is stable with visible error pressure."}
    return {"label": "Healthy", "detail": "Log distribution is within expected operating range."}


def kpi_card(title: str, value: str, subtitle: str, tone: str = "accent") -> None:
    st.markdown(
        f"""
        <div class="kpi-card {tone}">
            <div class="kpi-topline">
                <span>{title}</span>
                <span class="kpi-dot"></span>
            </div>
            <strong>{value}</strong>
            <small>{subtitle}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-title">
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
