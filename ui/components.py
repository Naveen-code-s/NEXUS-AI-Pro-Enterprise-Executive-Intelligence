import html
import streamlit as st

def metric(label, value):
    st.markdown(f'<div class="card"><div class="muted">{html.escape(str(label))}</div><div class="metric">{html.escape(str(value))}</div></div>', unsafe_allow_html=True)

def source(s):
    title = html.escape(str(s.get("title") or "Not available"))
    meta = " · ".join(str(x) for x in [s.get("source_type"), s.get("provider"), s.get("year"), ("p." + str(s.get("page"))) if s.get("page") is not None else None] if x)
    text = html.escape(str(s.get("passage") or s.get("abstract") or "Evidence not available")[:650])
    url = s.get("url")
    link = f'<a href="{html.escape(str(url))}" target="_blank">Open source</a>' if url else ""
    st.markdown(f'<div class="source"><b>{title}</b><br><span class="muted">{html.escape(meta)}</span><br>{text}<br>{link}</div>', unsafe_allow_html=True)
