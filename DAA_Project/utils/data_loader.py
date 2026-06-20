from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


REQUIRED_KEYS = {
    "total_lines": 0,
    "total_errors": 0,
    "total_warnings": 0,
    "total_info": 0,
    "status_2xx": 0,
    "status_4xx": 0,
    "status_5xx": 0,
    "anomaly_count": 0,
    "ip_frequency": [],
}


def candidate_paths(root: Path) -> list[Path]:
    return [
        root / "results.json",
        root.parent / "Distributed-Log-Analysis-System" / "results.json",
    ]


def resolve_results_path(root: Path) -> Path | None:
    for path in candidate_paths(root):
        if path.exists():
            return path
    return None


@st.cache_data(show_spinner=False)
def _read_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload


def normalize_results(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = REQUIRED_KEYS.copy()
    normalized.update(payload or {})

    for key in REQUIRED_KEYS:
        if key != "ip_frequency":
            try:
                normalized[key] = int(normalized.get(key, 0) or 0)
            except (TypeError, ValueError):
                normalized[key] = 0

    ip_rows = normalized.get("ip_frequency") or []
    cleaned_rows = []
    for row in ip_rows:
        if not isinstance(row, dict):
            continue
        cleaned_rows.append(
            {
                "ip": str(row.get("ip", "Unknown")),
                "count": int(row.get("count", 0) or 0),
                "anomaly": bool(row.get("anomaly", False)),
            }
        )
    normalized["ip_frequency"] = cleaned_rows
    normalized["anomaly_count"] = max(
        normalized["anomaly_count"],
        sum(1 for row in cleaned_rows if row["anomaly"]),
    )
    return normalized


def load_results(root: Path) -> tuple[dict[str, Any], str | None]:
    path = resolve_results_path(root)
    if not path:
        return REQUIRED_KEYS.copy(), "results.json was not found. Run the backend or place results.json inside DAA_Project."

    try:
        return normalize_results(_read_json(str(path))), None
    except json.JSONDecodeError as exc:
        return REQUIRED_KEYS.copy(), f"results.json could not be parsed: {exc}"
    except OSError as exc:
        return REQUIRED_KEYS.copy(), f"results.json could not be read: {exc}"


def ip_dataframe(data: dict[str, Any]) -> pd.DataFrame:
    frame = pd.DataFrame(data.get("ip_frequency", []), columns=["ip", "count", "anomaly"])
    if frame.empty:
        return pd.DataFrame(columns=["ip", "count", "anomaly", "risk_status"])
    frame["risk_status"] = frame["anomaly"].map(lambda value: "High Risk" if value else "Normal")
    return frame.sort_values("count", ascending=False).reset_index(drop=True)


def category_dataframe(data: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"category": "Errors", "count": data.get("total_errors", 0), "color": "#EF4444"},
            {"category": "Warnings", "count": data.get("total_warnings", 0), "color": "#F59E0B"},
            {"category": "Information", "count": data.get("total_info", 0), "color": "#22C55E"},
        ]
    )


def status_dataframe(data: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"status": "2xx Success", "count": data.get("status_2xx", 0), "color": "#22C55E"},
            {"status": "4xx Client Error", "count": data.get("status_4xx", 0), "color": "#F59E0B"},
            {"status": "5xx Server Error", "count": data.get("status_5xx", 0), "color": "#EF4444"},
        ]
    )
