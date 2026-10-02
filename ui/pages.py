import html
from pathlib import Path
import streamlit as st

from agents.orchestrator import Orchestrator
from ui.components import source


def _pill(text):
    return f'<span class="op-pill">{html.escape(str(text).replace("_", " ").title())}</span>'


def _money(value):
    try:
        return f"{float(value):,.2f}"
    except Exception:
        return str(value)


def _render_data(section, section_index=0):
    st.markdown("#### Data intelligence")
    s = section["summary"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{s['rows']:,}")
    c2.metric("Columns", s["columns"])
    c3.metric("Missing cells", f"{s['missing']:,}")
    c4.metric("Numeric fields", len(s["numeric"]))

    if section.get("metrics"):
        st.markdown("**Key measured values**")
        metric_cols = st.columns(min(4, max(1, len(section["metrics"]))))
        for idx, (label, value) in enumerate(section["metrics"].items()):
            metric_cols[idx % len(metric_cols)].metric(str(label), _money(value) if isinstance(value, (int, float)) else str(value))

    st.markdown("**Clear findings**")
    for idx, insight in enumerate(section.get("insights", []), 1):
        st.markdown(f"**Finding {idx}.** {insight}")

    for idx, chart in enumerate(section.get("charts", [])):
        st.markdown(f"**{chart['title']}**")
        st.plotly_chart(
            chart["figure"],
            use_container_width=True,
            config={"displaylogo": False},
            key=f"nexus_chart_{section_index}_{idx}_{chart.get('id', idx)}",
        )

    if section.get("data_quality"):
        with st.expander("Data quality details"):
            for item in section["data_quality"]:
                st.write(f"• {item}")


def _advice_item(item):
    st.markdown(f"**{item.get('title', 'Recommendation')}**")
    st.write(item.get("action", ""))
    meta = " · ".join([
        f"Impact: {item.get('impact', 'Medium')}",
        f"Effort: {item.get('effort', 'Medium')}",
        f"Confidence: {item.get('confidence', 'Medium')}",
    ])
    st.caption(meta)
    if item.get("basis"):
        st.caption(f"Evidence basis: {item['basis']}")
    if item.get("validation"):
        st.caption(f"Validate: {item['validation']}")


def _render_advisor(section):
    st.divider()
    st.markdown("### NEXUS Business Advisor")
    st.markdown(f"**Decision summary:** {section.get('summary', '')}")
    st.caption(section.get("decision_note", section.get("disclaimer", "")))

    kpis = section.get("kpis", [])
    if kpis:
        st.markdown("**Business signals**")
        cols = st.columns(min(4, len(kpis)))
        for i, kpi in enumerate(kpis):
            value = kpi.get("value")
            if kpi.get("format") == "currency":
                display = _money(value)
            elif kpi.get("format") == "percent":
                display = f"{float(value):+.1f}%"
            else:
                display = str(value)
            cols[i % len(cols)].metric(kpi.get("label", "Signal"), display)

    tabs = st.tabs(["Growth opportunities", "Risks", "Options", "Action plan"])
    with tabs[0]:
        for item in section.get("opportunities", []):
            _advice_item(item)
            st.divider()
    with tabs[1]:
        for item in section.get("risks", []):
            _advice_item(item)
            st.divider()
    with tabs[2]:
        for item in section.get("alternatives", []):
            _advice_item(item)
            st.divider()
    with tabs[3]:
        for item in section.get("next_steps", []):
            st.markdown(f"**{item.get('step', '')}. {item.get('action', '')}**")
            st.caption(f"Owner: {item.get('owner', 'Unassigned')} · KPI: {item.get('kpi', 'Define KPI')}")
            st.divider()


def _render_evidence(result):
    if not result.get("evidence"):
        return
    st.divider()
    st.markdown("### Evidence verification")
    direct = sum(1 for e in result["evidence"] if e.get("level") == "Direct evidence")
    related = sum(1 for e in result["evidence"] if e.get("level") == "Related evidence")
    insufficient = sum(1 for e in result["evidence"] if e.get("level") == "Insufficient evidence")
    c1, c2, c3 = st.columns(3)
    c1.metric("Direct", direct)
    c2.metric("Related", related)
    c3.metric("Insufficient", insufficient)
    for e in result["evidence"]:
        level = e.get("level", "Insufficient evidence")
        st.markdown(f"**{level}**")
        st.write(e.get("reason", "No verification explanation available."))


def render(settings, db, kb):
    counts = db.counts()
    st.markdown(
        '<section class="hero"><div class="kicker">NEXUS AI · ENTERPRISE INTELLIGENCE</div>'
        '<h1>One command. Clear business decisions.</h1>'
        '<p class="muted">NEXUS automatically chooses the required intelligence operations and returns measurable findings, evidence, visual analysis, business options and next actions.</p></section>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    for col, (label, value) in zip(cols, [("Sources", counts["documents"]), ("Pages", counts["pages"]), ("Chunks", counts["chunks"]), ("Datasets", counts["datasets"]), ("Reports", counts["reports"]) ]):
        col.metric(label, value)

    st.markdown('<div class="command-label">NEXUS COMMAND CENTER</div>', unsafe_allow_html=True)
    q = st.text_area(
        "NEXUS command",
        placeholder="Example: Analyze our sales, explain the main drivers and risks, show the right charts, suggest 3 ways to improve revenue and margin, compare the options, verify the evidence and create an executive report.",
        height=120,
        label_visibility="collapsed",
    )
    c1, c2 = st.columns([1, 7])
    run = c1.button("Run Intelligence", type="primary", use_container_width=True)
    clear = c2.button("Clear workspace result", use_container_width=False)
    if clear:
        st.session_state.answer = None
        st.rerun()

    if run and q.strip():
        with st.status("NEXUS is planning and executing the workflow…", expanded=True) as status:
            try:
                result = Orchestrator().run(settings, q, dataset_paths=st.session_state.get("dataset_paths", []))
                st.session_state.answer = result
                st.session_state.last_query = q
                st.write("Execution plan: " + " → ".join(result.get("operations", ["search"])))
                status.update(label="NEXUS intelligence workflow complete", state="complete")
            except Exception:
                status.update(label="Workflow failed", state="error")
                st.error("NEXUS could not complete the workflow. Technical details are logged by the application.")

    result = st.session_state.get("answer")
    if not result:
        st.markdown('<div class="empty-state"><div class="kicker">READY</div><h3>Ask for an outcome, not a tool.</h3><p>NEXUS decides which capabilities to activate and presents only the operations needed for your request.</p><div class="chips"><span>Analyze</span><span>Explain</span><span>Research</span><span>Advise</span><span>Verify</span><span>Report</span></div></div>', unsafe_allow_html=True)
        return

    st.divider()
    st.markdown("### Executive result")
    st.markdown("".join(_pill(x) for x in result.get("operations", [])), unsafe_allow_html=True)
    if result.get("executive_summary"):
        st.info(result["executive_summary"])

    for section_index, section in enumerate(result.get("sections", [])):
        kind = section.get("type")
        if kind == "answer":
            st.markdown("### NEXUS synthesis")
            st.write(section.get("answer", ""))
        elif kind == "data":
            st.divider()
            _render_data(section, section_index)
        elif kind == "business":
            st.divider()
            st.markdown("### Business intelligence")
            for insight in section.get("insights", []):
                st.markdown(f"• {insight}")
        elif kind == "business_advice":
            _render_advisor(section)
        elif kind == "report":
            path = Path(section.get("path", ""))
            st.divider()
            st.markdown("### Report")
            if path.exists():
                st.success("Evidence-backed report generated from the completed workflow.")
                st.download_button("Download intelligence report", path.read_bytes(), file_name=path.name, mime="text/markdown", key=f"report_{section_index}")
        elif kind == "warning":
            st.warning(section.get("message", "Operation unavailable."))

    _render_evidence(result)

    st.divider()
    st.markdown("### Sources & citations")
    if result.get("sources"):
        for item in result["sources"]:
            source(item)
    else:
        st.info("Evidence not available.")
