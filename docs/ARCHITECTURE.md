# Architecture

NEXUS AI is organized around shared services rather than independent mini-apps.

**Flow:** Upload → ingestion → extraction → normalization → chunking → metadata → embeddings → FAISS → hybrid search → agent orchestration → evidence → LLM → verification → response/report.

**Agents:** Search, Document, Research, Data, Citation, Verification, Report, Orchestrator.

**Persistence:** SQLite for metadata/activity, filesystem for uploads/reports, FAISS for semantic retrieval.

**External research:** Semantic Scholar, OpenAlex and Crossref metadata endpoints. Missing metadata is represented as unavailable rather than guessed.

**UI:** Dashboard, Knowledge Base, Global Search, Ask NEXUS, Research, Data Intelligence, Citation Finder, Reports, Analytics and Settings.
