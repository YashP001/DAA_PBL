from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


def _load_asset(root: Path, name: str) -> str:
    path = root / "assets" / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_visualization_html(data: dict, root: Path) -> str:
    total = int(data.get("total_lines", 0) or 0)
    errors = int(data.get("total_errors", 0) or 0)
    warnings = int(data.get("total_warnings", 0) or 0)
    anomalies = int(data.get("anomaly_count", 0) or 0)

    css = _load_asset(root, "algo_viz.css")
    js = _load_asset(root, "algo_viz.js")

    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><style>{css}</style></head>
<body>
<div class="sim-shell active" id="simShell" style="--speed:1" data-total="{total}">
    <div class="particles" aria-hidden="true"></div>

    <div class="sim-header">
        <div>
            <span class="eyebrow">Live Architecture Simulation</span>
            <h2>Divide &amp; Conquer &mdash; Log Analysis Pipeline</h2>
            <p class="muted">Watch the log file split, process in parallel, merge, and feed the dashboard.</p>
        </div>
        <div class="muted" style="font-size:0.8rem;text-align:right">Hover nodes for details<br><span style="color:var(--accent);font-weight:800">{total:,}</span> log lines</div>
    </div>

    <!-- CONTROLS -->
    <div class="ctrl">
        <button class="primary" id="playBtn">&#9654; Play</button>
        <button id="pauseBtn">&#9208; Pause</button>
        <button class="danger-btn" id="resetBtn">&#8635; Reset</button>
        <select id="speedSel" aria-label="Speed">
            <option value="0.6">&#128034; Slow</option>
            <option value="1" selected>&#9654; Medium</option>
            <option value="1.8">&#9889; Fast</option>
        </select>
        <label class="toggle"><input type="checkbox" id="stepMode"> Step-by-step</label>
        <div class="ctrl-right">
            <button id="nextBtn">Next Step &rarr;</button>
            <span class="muted" id="stepStatus" style="font-size:0.82rem">Idle</span>
        </div>
    </div>

    <!-- STEP PROGRESS BAR -->
    <div class="step-bar">
        <div class="step-dot" title="Divide">1</div><div class="step-line"></div>
        <div class="step-dot" title="Allocate">2</div><div class="step-line"></div>
        <div class="step-dot" title="Conquer">3</div><div class="step-line"></div>
        <div class="step-dot" title="Combine">4</div><div class="step-line"></div>
        <div class="step-dot" title="Output">5</div><div class="step-line"></div>
        <div class="step-dot" title="Dashboard">6</div>
    </div>

    <!-- STAGE -->
    <div class="stage" id="stage">
        <div class="scanner" id="scanner"></div>

        <svg class="connections" viewBox="0 0 1200 1140" preserveAspectRatio="none">
            <defs>
                <marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#38BDF8"/></marker>
                <marker id="arrG" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#F59E0B"/></marker>
                <marker id="arrR" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#EF4444"/></marker>
            </defs>
            <!-- Divide wires: log -> partitions -->
            <path class="wire divide-wire" d="M600 125 C600 158 130 158 130 200" marker-end="url(#arr)"/>
            <path class="wire divide-wire" d="M600 125 C600 158 410 158 410 200" marker-end="url(#arr)"/>
            <path class="wire divide-wire" d="M600 125 C600 158 690 158 690 200" marker-end="url(#arr)"/>
            <path class="wire divide-wire" d="M600 125 C600 158 970 158 970 200" marker-end="url(#arr)"/>
            <!-- Thread wires: partitions -> threads -->
            <path class="wire thread-wire green" d="M130 290 L130 400" marker-end="url(#arr)"/>
            <path class="wire thread-wire green" d="M410 290 L410 400" marker-end="url(#arr)"/>
            <path class="wire thread-wire green" d="M690 290 L690 400" marker-end="url(#arr)"/>
            <path class="wire thread-wire green" d="M970 290 L970 400" marker-end="url(#arr)"/>
            <!-- Combine wires: threads -> aggregator -->
            <path class="wire combine-wire gold" d="M130 500 C180 580 400 620 590 625" marker-end="url(#arrG)"/>
            <path class="wire combine-wire gold" d="M410 500 C440 580 520 620 590 625" marker-end="url(#arrG)"/>
            <path class="wire combine-wire gold" d="M690 500 C670 580 640 620 610 625" marker-end="url(#arrG)"/>
            <path class="wire combine-wire gold" d="M970 500 C920 580 780 620 610 625" marker-end="url(#arrG)"/>
            <!-- Output wires: aggregator -> json -> dashboard -->
            <path class="wire output-wire red" d="M600 730 L600 790" marker-end="url(#arrR)"/>
            <path class="wire dash-wire" d="M600 895 L600 1020" marker-end="url(#arr)"/>
        </svg>

        <!-- LOG FILE NODE -->
        <div class="node log-file pulse" data-tip="file_loader.c: Memory-maps the input for efficient I/O">
            <span class="label">Input</span>
            <h3>&#128196; Large Log File</h3>
            <p>{total:,} records &bull; Awaiting partitioning</p>
            <span class="src-badge">file_loader.c</span>
        </div>

        <!-- PARTITIONS -->
        <div class="node partition p1" data-tip="partitioner.c: Newline-safe chunk boundary"><span class="label">Partition 1</span><h3>Chunk A</h3><p>{total//4:,} lines</p><span class="src-badge">partitioner.c</span></div>
        <div class="node partition p2" data-tip="partitioner.c: Balanced file region"><span class="label">Partition 2</span><h3>Chunk B</h3><p>{total//4:,} lines</p><span class="src-badge">partitioner.c</span></div>
        <div class="node partition p3" data-tip="partitioner.c: Independent scan unit"><span class="label">Partition 3</span><h3>Chunk C</h3><p>{total//4:,} lines</p><span class="src-badge">partitioner.c</span></div>
        <div class="node partition p4" data-tip="partitioner.c: Parallel-ready data block"><span class="label">Partition 4</span><h3>Chunk D</h3><p>{total//4:,} lines</p><span class="src-badge">partitioner.c</span></div>

        <!-- THREADS -->
        <div class="node thread t1" data-tip="worker.c: POSIX thread processing chunk independently"><span class="label">Thread 1 &rarr; Partition 1</span><h3>&#9881; Worker 1</h3><p><span class="counter">0</span> lines parsed</p><div class="progress"><div class="bar"></div></div><div class="spinner"></div></div>
        <div class="node thread t2" data-tip="worker.c: Parses ERROR/WARN/INFO + HTTP codes"><span class="label">Thread 2 &rarr; Partition 2</span><h3>&#9881; Worker 2</h3><p><span class="counter">0</span> lines parsed</p><div class="progress"><div class="bar"></div></div><div class="spinner"></div></div>
        <div class="node thread t3" data-tip="worker.c: Counts IP frequencies per chunk"><span class="label">Thread 3 &rarr; Partition 3</span><h3>&#9881; Worker 3</h3><p><span class="counter">0</span> lines parsed</p><div class="progress"><div class="bar"></div></div><div class="spinner"></div></div>
        <div class="node thread t4" data-tip="worker.c: Detects anomalous IPs above threshold"><span class="label">Thread 4 &rarr; Partition 4</span><h3>&#9881; Worker 4</h3><p><span class="counter">0</span> lines parsed</p><div class="progress"><div class="bar"></div></div><div class="spinner"></div></div>

        <!-- AGGREGATOR -->
        <div class="node aggregator" data-tip="aggregator.c: Merges all thread-local results into global counters">
            <span class="label">Combine</span>
            <h3>&#128279; Aggregator.c</h3>
            <p>Thread results converge into global totals.</p>
            <span class="src-badge">aggregator.c</span>
        </div>

        <!-- JSON OUTPUT -->
        <div class="node json-out" data-tip="output.c: Serializes aggregated data to JSON">
            <span class="label">Output</span>
            <h3>&#128196; results.json</h3>
            <div class="json-preview">{{"errors": {errors:,},<br>"warnings": {warnings:,},<br>"anomalies": {anomalies:,}}}</div>
            <span class="src-badge">output.c</span>
        </div>

        <!-- DASHBOARD -->
        <div class="node dash-node" data-tip="Streamlit dashboard reads results.json and renders visualizations">
            <span class="label">Visualization</span>
            <h3>&#128202; Dashboard</h3>
            <p>Interactive KPIs, charts, anomaly tables</p>
            <span class="src-badge">app.py</span>
        </div>

        <!-- PACKETS -->
        <div class="packet" id="pA"></div>
        <div class="packet" id="pB"></div>
        <div class="packet" id="pC"></div>
        <div class="packet" id="pD"></div>

        <!-- PHASE INFO PANEL -->
        <div class="phase-info" id="phaseInfo">
            <h4 id="phaseTitle"></h4>
            <p id="phaseDesc"></p>
            <div class="src" id="phaseSrc"></div>
        </div>
    </div>

    <!-- LIVE METRICS -->
    <div class="metrics-strip">
        <div class="metric"><span>Pipeline Phase</span><strong id="phaseText">Ready</strong></div>
        <div class="metric"><span>Worker Status</span><strong id="workerText">&mdash;</strong></div>
        <div class="metric"><span>Total Log Lines</span><strong>{total:,}</strong></div>
        <div class="metric"><span>Generated Output</span><strong>results.json</strong></div>
    </div>

    <!-- D&C ALGORITHM MAPPING -->
    <div class="dc-map">
        <div class="dc-card"><div class="dc-phase divide">&#9473; Divide</div><h4>partitioner.c</h4><p>Splits large file into 4 newline-safe chunks for independent processing.</p></div>
        <div class="dc-card"><div class="dc-phase conquer">&#9876; Conquer</div><h4>worker.c + parser.c</h4><p>Each thread parses its chunk: log levels, HTTP codes, IP frequencies.</p></div>
        <div class="dc-card"><div class="dc-phase combine">&#128279; Combine</div><h4>aggregator.c</h4><p>Merges thread-local counters into global results and flags anomalies.</p></div>
        <div class="dc-card"><div class="dc-phase output">&#128196; Output</div><h4>output.c</h4><p>Serializes aggregated data into results.json consumed by the dashboard.</p></div>
    </div>
</div>

<script>{js}</script>
</body>
</html>"""


def render(data: dict, root: Path) -> None:
    components.html(build_visualization_html(data, root), height=1660, scrolling=False)
