import streamlit as st
from core.config import get_settings
from database.store import Database
from database.knowledge_base import KnowledgeBase
from ui.styles import inject_styles
from ui.navigation import sidebar
from ui.pages import render

st.set_page_config(page_title="NEXUS AI", page_icon="N", layout="wide", initial_sidebar_state="expanded")
settings = get_settings()
inject_styles()
if "db" not in st.session_state:
    st.session_state.db = Database(settings.database_url)
if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase(st.session_state.db, settings)
if "answer" not in st.session_state:
    st.session_state.answer = None
if "processed_uploads" not in st.session_state:
    st.session_state.processed_uploads = set()
if "dataset_paths" not in st.session_state:
    st.session_state.dataset_paths = [d.path for d in st.session_state.db.datasets() if getattr(d, "path", None)]

sidebar(settings, st.session_state.kb)
render(settings, st.session_state.db, st.session_state.kb)
