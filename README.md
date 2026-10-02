# NEXUS AI

**Enterprise AI Intelligence Platform**

NEXUS AI is a unified enterprise intelligence platform for documents, business data, research, evidence and executive reporting. It is intentionally designed so a user can describe an outcome in one command while NEXUS automatically decides which internal intelligence capabilities must execute.

## What makes the Pro workflow different

NEXUS is not a PDF chatbot and not a collection of disconnected pages. The user uploads knowledge/data once, then uses one command center. NEXUS can automatically activate:

- private knowledge retrieval
- business data analysis
- dynamic charts and graphs
- external academic research
- comparisons and business insights
- evidence verification
- citation/source presentation
- executive report generation

The UI does **not** require users to open Analytics, Charts, Research, Verification or Reports manually.

## Example command

> Analyze our sales performance, show the monthly revenue trend and top products, identify major risks, research the current market context, verify the evidence and prepare an executive report.

The execution plan can automatically become:

`SEARCH → DATA ANALYSIS → VISUALIZATION → EXTERNAL RESEARCH → BUSINESS INTELLIGENCE → EVIDENCE VERIFICATION → REPORT GENERATION`

## Product workflow

UPLOAD → INGEST → EXTRACT → NORMALIZE → CHUNK → METADATA → EMBED → INDEX → KNOWLEDGE BASE → SEARCH / ASK / ANALYZE / RESEARCH → AGENT ORCHESTRATION → EVIDENCE → REASONING → VERIFICATION → ANSWER / INSIGHT / REPORT → CITATIONS + SOURCES

## Supported content

- PDF
- DOCX
- TXT
- CSV
- XLSX

## Architecture

- **UI:** Streamlit command center
- **LLM:** Groq through LangChain-compatible integration
- **Embeddings:** Hugging Face
- **Vector retrieval:** FAISS
- **Metadata:** SQLite/SQLAlchemy
- **Research:** Semantic Scholar, OpenAlex, Crossref adapters
- **Analytics:** pandas + Plotly
- **Documents:** PyMuPDF + python-docx
- **Reports:** Markdown, with export layer available
- **Tests:** pytest
- **CI:** GitHub Actions

See `docs/PRO_ARCHITECTURE.md` for the execution model.

## Run in VS Code

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Set `GROQ_API_KEY` in `.env` for LLM synthesis. External research metadata can operate through the configured public provider endpoints; provider/network availability can vary.

### Tests

```bash
pytest -q
```

## Trust and security

- secrets are environment-based
- `.env` is ignored by Git
- uploads are restricted to supported formats
- filenames are sanitized
- duplicate document ingestion is checked by checksum
- source metadata is preserved for citations
- unavailable metadata is not invented
- analytics use actual uploaded data
- normal UI errors do not expose raw tracebacks

## Scale path

The repository keeps UI, orchestration, retrieval, storage and analytics boundaries separate so SQLite can migrate to PostgreSQL and FAISS can migrate to pgvector without rebuilding the product concept.
