import streamlit as st


def sidebar(settings, kb):
    with st.sidebar:
        st.markdown('<div class="brand">NEXUS<span> AI</span></div>', unsafe_allow_html=True)
        st.caption("Enterprise AI Intelligence Platform")
        st.divider()
        st.markdown("**WORKSPACE INGESTION**")
        files = st.file_uploader(
            "Upload files",
            type=["pdf", "docx", "txt", "csv", "xlsx"],
            accept_multiple_files=True,
            help="Documents become searchable evidence. CSV/XLSX become business intelligence data.",
        )
        for f in files or []:
            marker = f"uploaded::{f.name}::{len(f.getvalue())}"
            if marker in st.session_state.get("processed_uploads", set()):
                continue
            try:
                result = kb.ingest(f.name, f.getvalue())
                st.session_state.setdefault("processed_uploads", set()).add(marker)
                if result.get("status") == "dataset":
                    st.session_state.setdefault("dataset_paths", []).append(result["path"])
                st.success(f"Ready · {f.name}")
            except Exception as exc:
                st.error(f"Could not process {f.name}: {exc}")
        st.divider()
        st.caption("All intelligence operations are opened automatically from the command center.")
    return None
