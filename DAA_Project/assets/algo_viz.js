(() => {
    const $ = id => document.getElementById(id);
    const shell = $("simShell"), stage = $("stage");
    const playBtn = $("playBtn"), pauseBtn = $("pauseBtn"), resetBtn = $("resetBtn");
    const speedSel = $("speedSel"), stepMode = $("stepMode"), nextBtn = $("nextBtn");
    const phaseText = $("phaseText"), workerText = $("workerText"), stepStatus = $("stepStatus");
    const phaseInfo = $("phaseInfo"), phaseTitle = $("phaseTitle"), phaseDesc = $("phaseDesc"), phaseSrc = $("phaseSrc");
    const scanner = $("scanner");
    const totalLines = parseInt(shell.dataset.total) || 500000;
    const counters = [...document.querySelectorAll(".counter")];
    const bars = [...document.querySelectorAll(".bar")];
    const packets = ["pA","pB","pC","pD"].map(id => $(id));
    const stepDots = [...document.querySelectorAll(".step-dot")];
    const stepLines = [...document.querySelectorAll(".step-line")];

    const steps = [
        { name:"Step 1 — Divide", phase:"Divide", desc:"The large log file is partitioned into 4 equal chunks using newline-safe boundaries.", src:"partitioner.c", show:[".partition",".divide-wire"] },
        { name:"Step 2 — Thread Allocation", phase:"Allocate", desc:"Each partition is assigned to an independent POSIX thread for parallel processing.", src:"worker.c", show:[".partition",".divide-wire",".thread",".thread-wire"] },
        { name:"Step 3 — Parallel Processing", phase:"Conquer", desc:"All 4 threads parse log entries simultaneously — counting errors, warnings, status codes, and IP frequencies.", src:"parser.c + worker.c", show:[".partition",".divide-wire",".thread",".thread-wire"] },
        { name:"Step 4 — Combine", phase:"Combine", desc:"Thread-local results are merged into global counters. Anomalous IPs exceeding threshold are flagged.", src:"aggregator.c", show:[".partition",".thread",".combine-wire",".aggregator"] },
        { name:"Step 5 — JSON Output", phase:"Output", desc:"Aggregated metrics are serialized into results.json for the dashboard to consume.", src:"output.c", show:[".aggregator",".json-out",".output-wire"] },
        { name:"Step 6 — Dashboard", phase:"Dashboard", desc:"The Streamlit dashboard reads results.json and renders interactive charts, KPIs, and anomaly tables.", src:"app.py (Streamlit)", show:[".aggregator",".json-out",".dash-node",".output-wire",".dash-wire"] }
    ];
    let timers = [], stepIdx = -1, isPaused = false;

    function addParticles() {
        const layer = document.querySelector(".particles");
        layer.innerHTML = "";
        for (let i = 0; i < 48; i++) {
            const p = document.createElement("span");
            p.className = "particle";
            p.style.setProperty("--x", Math.random()*100+"%");
            p.style.setProperty("--y", 15+Math.random()*80+"%");
            p.style.setProperty("--dl", (Math.random()*9).toFixed(2));
            p.style.setProperty("--dur", (7+Math.random()*11).toFixed(2));
            layer.appendChild(p);
        }
    }

    function clearTimers() { timers.forEach(t => clearTimeout(t)); timers = []; }

    function resetVisuals() {
        clearTimers(); isPaused = false;
        shell.classList.remove("paused");
        pauseBtn.textContent = "⏸ Pause";
        document.querySelectorAll(".partition,.thread,.aggregator,.json-out,.dash-node").forEach(el => { el.style.opacity = ""; el.style.transform = ""; el.className = el.className.replace(/ glow-\w+/g,""); });
        document.querySelectorAll(".wire").forEach(el => el.style.opacity = "0");
        bars.forEach(b => b.style.width = "0%");
        counters.forEach(c => c.textContent = "0");
        packets.forEach(p => { p.style.opacity = "0"; });
        phaseText.textContent = "Ready";
        workerText.textContent = "—";
        stepStatus.textContent = "Idle";
        phaseInfo.classList.remove("show");
        scanner.classList.remove("on");
        stepDots.forEach(d => { d.classList.remove("done","active"); });
        stepLines.forEach(l => l.classList.remove("done"));
        stepIdx = -1;
    }

    function reveal(sel) {
        document.querySelectorAll(sel).forEach(el => {
            el.style.opacity = "1";
            if (el.classList.contains("partition") || el.classList.contains("thread"))
                el.style.transform = "translateY(0) scale(1)";
            if (el.classList.contains("aggregator") || el.classList.contains("json-out") || el.classList.contains("dash-node"))
                el.style.transform = "translateX(-50%) scale(1)";
        });
    }

    function setStepProgress(idx) {
        stepDots.forEach((d,i) => {
            d.classList.remove("done","active");
            if (i < idx) d.classList.add("done");
            else if (i === idx) d.classList.add("active");
        });
        stepLines.forEach((l,i) => {
            l.classList.toggle("done", i < idx);
        });
    }

    function showPhaseInfo(step) {
        phaseTitle.textContent = step.phase;
        phaseDesc.textContent = step.desc;
        phaseSrc.textContent = "📁 " + step.src;
        phaseInfo.classList.add("show");
    }

    function animCounters(duration) {
        const start = performance.now();
        const perW = Math.floor(totalLines / 4);
        function frame(now) {
            const r = Math.min((now - start) / duration, 1);
            const e = 1 - Math.pow(1 - r, 3);
            counters.forEach((c, i) => { c.textContent = Math.floor(perW * e + i * 137).toLocaleString("en-IN"); });
            bars.forEach(b => b.style.width = Math.floor(e * 100) + "%");
            if (r < 1 && !isPaused) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    function animPacket(pkt, pts, delay) {
        pkt.style.opacity = "0";
        timers.push(setTimeout(() => {
            pkt.animate([
                { transform: `translate(${pts[0][0]}px,${pts[0][1]}px)`, opacity: 0 },
                { transform: `translate(${pts[1][0]}px,${pts[1][1]}px)`, opacity: 1 },
                { transform: `translate(${pts[2][0]}px,${pts[2][1]}px)`, opacity: 0 }
            ], { duration: 1200 / Number(speedSel.value), iterations: 2, easing: "ease-in-out" });
        }, delay));
    }

    function playAnim() {
        resetVisuals();
        const sp = Number(speedSel.value);
        const t = b => b / sp;
        stepStatus.textContent = "▶ Running full simulation";
        scanner.classList.add("on");

        /* Step 1: Divide */
        timers.push(setTimeout(() => {
            phaseText.textContent = "Divide";
            workerText.textContent = "Partitioning...";
            reveal(".partition"); reveal(".divide-wire");
            setStepProgress(0);
            showPhaseInfo(steps[0]);
        }, t(300)));

        /* Step 2: Thread Allocation */
        timers.push(setTimeout(() => {
            phaseText.textContent = "Thread Allocation";
            workerText.textContent = "4 threads spawned";
            reveal(".thread"); reveal(".thread-wire");
            setStepProgress(1);
            showPhaseInfo(steps[1]);
        }, t(1600)));

        /* Step 3: Parallel Processing */
        timers.push(setTimeout(() => {
            phaseText.textContent = "Parallel Processing";
            workerText.textContent = "4 workers active";
            document.querySelectorAll(".thread").forEach(el => el.classList.add("glow-green"));
            animCounters(t(3200));
            setStepProgress(2);
            showPhaseInfo(steps[2]);
        }, t(2600)));

        /* Step 4: Combine */
        timers.push(setTimeout(() => {
            phaseText.textContent = "Combine";
            workerText.textContent = "Merging results...";
            document.querySelectorAll(".thread").forEach(el => el.classList.remove("glow-green"));
            reveal(".combine-wire"); reveal(".aggregator");
            document.querySelector(".aggregator").classList.add("glow-gold");
            animPacket(packets[0], [[100,380],[340,570],[570,620]], 0);
            animPacket(packets[1], [[360,380],[480,570],[590,620]], 80);
            animPacket(packets[2], [[620,380],[600,570],[600,620]], 140);
            animPacket(packets[3], [[880,380],[750,570],[610,620]], 200);
            setStepProgress(3);
            showPhaseInfo(steps[3]);
        }, t(6200)));

        /* Step 5: JSON Output */
        timers.push(setTimeout(() => {
            phaseText.textContent = "JSON Output";
            workerText.textContent = "Writing results.json";
            document.querySelector(".aggregator").classList.remove("glow-gold");
            reveal(".json-out"); reveal(".output-wire");
            document.querySelector(".json-out").classList.add("glow-red");
            animPacket(packets[0], [[590,680],[590,740],[590,790]], 0);
            setStepProgress(4);
            showPhaseInfo(steps[4]);
        }, t(8400)));

        /* Step 6: Dashboard */
        timers.push(setTimeout(() => {
            phaseText.textContent = "Dashboard";
            workerText.textContent = "Rendering charts";
            document.querySelector(".json-out").classList.remove("glow-red");
            reveal(".dash-node"); reveal(".dash-wire");
            document.querySelector(".dash-node").classList.add("pulse");
            animPacket(packets[0], [[590,920],[590,970],[590,1020]], 0);
            setStepProgress(5);
            showPhaseInfo(steps[5]);
            stepStatus.textContent = "✓ Simulation complete";
            scanner.classList.remove("on");
        }, t(10200)));
    }

    function applyStep(idx) {
        resetVisuals();
        shell.classList.add("paused");
        isPaused = true;
        const step = steps[idx];
        steps.slice(0, idx + 1).flatMap(s => s.show).forEach(sel => reveal(sel));
        if (idx >= 2) {
            counters.forEach((c, w) => c.textContent = Math.floor(totalLines / 4 + w * 137).toLocaleString("en-IN"));
            bars.forEach(b => b.style.width = "100%");
        }
        phaseText.textContent = step.phase;
        workerText.textContent = step.desc.substring(0, 35) + "...";
        stepStatus.textContent = step.name;
        setStepProgress(idx);
        showPhaseInfo(step);
    }

    playBtn.onclick = () => { stepMode.checked = false; shell.classList.remove("paused"); isPaused = false; playAnim(); };

    pauseBtn.onclick = () => {
        isPaused = !isPaused;
        shell.classList.toggle("paused", isPaused);
        pauseBtn.textContent = isPaused ? "▶ Resume" : "⏸ Pause";
    };

    resetBtn.onclick = () => { resetVisuals(); stepMode.checked = false; };

    speedSel.onchange = () => {
        shell.style.setProperty("--speed", speedSel.value);
        if (!stepMode.checked && !isPaused) playAnim();
    };

    stepMode.onchange = () => {
        stepIdx = -1; resetVisuals();
        isPaused = stepMode.checked;
        shell.classList.toggle("paused", stepMode.checked);
        stepStatus.textContent = stepMode.checked ? "Step mode — click Next Step" : "Idle";
    };

    nextBtn.onclick = () => {
        if (!stepMode.checked) stepMode.checked = true;
        stepIdx = (stepIdx + 1) % steps.length;
        applyStep(stepIdx);
    };

    addParticles();
    playAnim();
})();
