from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOTLY_TEMPLATE = "plotly_dark"
BG = "rgba(0,0,0,0)"
GRID = "rgba(148,163,184,0.18)"
TEXT = "#CBD5E1"
ACCENT = "#38BDF8"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"


def apply_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family="Inter, Segoe UI, sans-serif"),
        height=height,
        margin=dict(l=24, r=24, t=42, b=24),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig


def log_distribution_pie(frame: pd.DataFrame, hole: float = 0.0) -> go.Figure:
    fig = px.pie(
        frame,
        names="category",
        values="count",
        hole=hole,
        color="category",
        color_discrete_map={"Errors": DANGER, "Warnings": WARNING, "Information": SUCCESS},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="#0F172A", width=2)))
    return apply_layout(fig)


def status_bar(frame: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        frame,
        x="status",
        y="count",
        color="status",
        text="count",
        color_discrete_sequence=[SUCCESS, WARNING, DANGER],
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    return apply_layout(fig)


def top_ip_bar(frame: pd.DataFrame, limit: int = 10) -> go.Figure:
    top = frame.head(limit).sort_values("count", ascending=True)
    colors = top["anomaly"].map(lambda value: DANGER if value else ACCENT) if not top.empty else []
    fig = go.Figure(
        go.Bar(
            x=top["count"] if not top.empty else [],
            y=top["ip"] if not top.empty else [],
            orientation="h",
            marker_color=colors,
            text=top["count"] if not top.empty else [],
            texttemplate="%{text:,}",
            hovertemplate="IP %{y}<br>Requests %{x:,}<extra></extra>",
        )
    )
    fig.update_layout(title="Top IP Addresses")
    return apply_layout(fig, height=420)


def category_analysis(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=frame["category"],
            y=frame["count"],
            marker_color=[DANGER, WARNING, SUCCESS],
            text=frame["count"],
            texttemplate="%{text:,}",
        )
    )
    fig.update_layout(title="Log Category Analysis")
    return apply_layout(fig)


def performance_speedup() -> go.Figure:
    frame = pd.DataFrame(
        {
            "threads": [1, 2, 4, 8, 16],
            "sequential": [1, 1, 1, 1, 1],
            "parallel": [1, 1.82, 3.35, 5.9, 8.6],
        }
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame["threads"], y=frame["parallel"], mode="lines+markers", name="Parallel speedup", line=dict(color=ACCENT, width=4)))
    fig.add_trace(go.Scatter(x=frame["threads"], y=frame["sequential"], mode="lines+markers", name="Sequential baseline", line=dict(color=WARNING, dash="dash")))
    fig.update_layout(title="Conceptual Speedup", xaxis_title="Worker Threads", yaxis_title="Relative Speedup")
    return apply_layout(fig)


def cpu_utilization() -> go.Figure:
    labels = ["Thread 1", "Thread 2", "Thread 3", "Thread 4"]
    values = [86, 82, 88, 84]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=[ACCENT, SUCCESS, WARNING, DANGER], text=values, texttemplate="%{text}%"))
    fig.update_layout(title="CPU Utilization Visualization", yaxis_title="Utilization")
    fig.update_yaxes(range=[0, 100])
    return apply_layout(fig)


def thread_distribution() -> go.Figure:
    labels = ["Chunk 1", "Chunk 2", "Chunk 3", "Chunk 4"]
    values = [25, 25, 25, 25]
    fig = px.pie(names=labels, values=values, hole=0.58, color_discrete_sequence=[ACCENT, SUCCESS, WARNING, DANGER])
    fig.update_layout(title="Thread Distribution Diagram")
    fig.update_traces(textinfo="label+percent")
    return apply_layout(fig)
