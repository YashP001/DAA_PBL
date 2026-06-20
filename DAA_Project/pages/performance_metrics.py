from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.charts import cpu_utilization, performance_speedup, thread_distribution
from utils.helpers import kpi_card, section_title


def render(data: dict, root: Path) -> None:
    st.markdown(
        """
        <div class="glass-card">
            <span class="eyebrow">Demonstration Visualization</span>
            <p class="muted">
                The backend JSON does not include measured execution time, so this page presents conceptual
                performance visuals for explaining the divide-and-conquer design during evaluation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    with columns[0]:
        kpi_card("Sequential Processing", "1 worker", "Single scan over the complete file", "warning")
    with columns[1]:
        kpi_card("Parallel Processing", "N workers", "Chunks processed concurrently")
    with columns[2]:
        kpi_card("Aggregation", "Mutex merge", "Thread results combined safely", "success")

    left, right = st.columns(2)
    with left:
        section_title("Sequential vs Parallel Processing", "Conceptual speedup as workers increase.")
        st.plotly_chart(performance_speedup(), use_container_width=True)
    with right:
        section_title("CPU Utilization Visualization", "Balanced worker activity across chunks.")
        st.plotly_chart(cpu_utilization(), use_container_width=True)

    section_title("Thread Distribution Diagram", "Each worker receives a partition of the mapped log file.")
    st.plotly_chart(thread_distribution(), use_container_width=True)

    st.markdown(
        """
        <div class="glass-card">
            <h3>Why Divide and Conquer Improves Scalability</h3>
            <p class="muted">
                The log file is divided at safe newline boundaries, workers conquer their chunks independently,
                and the aggregator combines partial counts. This reduces wall-clock time on multi-core machines
                because parsing work is distributed while the final merge remains compact.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
