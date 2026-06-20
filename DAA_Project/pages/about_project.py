from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.helpers import section_title


def render(data: dict, root: Path) -> None:
    st.markdown(
        """
        <div class="glass-card">
            <span class="eyebrow">Project Title</span>
            <h2>Distributed Log File Analysis System using Divide and Conquer</h2>
            <p class="muted">M3 - System Integration and UI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Team Members")
    team_cols = st.columns(3)
    members = ["Yash Purwar (1RV24CI143)", "Janvi S Hegde (1RV24CI145)", "Simran S Patil (1RV24CI146)"]
    for col, member in zip(team_cols, members):
        with col:
            st.markdown(f"<div class='glass-card'><strong>{member}</strong></div>", unsafe_allow_html=True)

    section_title("Problem Statement")
    st.markdown(
        """
        <div class="glass-card">
            <p class="muted">
                Large log files are difficult to inspect manually and become expensive to process sequentially.
                The project solves this by using a distributed-style divide-and-conquer pipeline that partitions
                the input, analyzes chunks in parallel, aggregates metrics, and exposes the results through a
                professional analytics dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        section_title("Objectives")
        st.markdown(
            """
            <div class="glass-card">
                <p class="muted">Analyze log severity counts, status codes, and high-frequency IP addresses.</p>
                <p class="muted">Demonstrate divide-and-conquer design with parallel processing.</p>
                <p class="muted">Detect suspicious traffic patterns through anomaly flags.</p>
                <p class="muted">Present backend output through an enterprise-style dashboard.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        section_title("Algorithms Used")
        st.markdown(
            """
            <div class="glass-card">
                <p class="muted">Divide and Conquer file partitioning.</p>
                <p class="muted">Parallel chunk processing with pthreads.</p>
                <p class="muted">Frequency counting for IP request analysis.</p>
                <p class="muted">Threshold-based anomaly detection.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("Backend Architecture")
    st.html(
        (
            '<div class="flow-grid">'
            '<div class="flow-card"><span>Input</span><h3>test.log</h3><p>Large generated log file.</p></div>'
            '<div class="flow-card"><span>Loader</span><h3>file_loader.c</h3><p>Memory maps the file.</p></div>'
            '<div class="flow-card"><span>Divide</span><h3>partitioner.c</h3><p>Creates balanced chunks.</p></div>'
            '<div class="flow-card"><span>Conquer</span><h3>worker.c</h3><p>Threads scan records.</p></div>'
            '<div class="flow-card"><span>Combine</span><h3>aggregator.c</h3><p>Merges local results.</p></div>'
            '<div class="flow-card"><span>Output</span><h3>output.c</h3><p>Writes results.json.</p></div>'
            '<div class="flow-card"><span>UI</span><h3>Streamlit</h3><p>Displays analytics.</p></div>'
            "</div>"
        )
    )

    section_title("Expected Outcomes")
    st.markdown(
        """
        <div class="glass-card">
            <p class="muted">
                The final system should show faster conceptual scalability than sequential analysis, provide
                meaningful summaries of large logs, identify suspicious IP activity, and clearly communicate
                DAA concepts through a polished UI suitable for demonstration.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
