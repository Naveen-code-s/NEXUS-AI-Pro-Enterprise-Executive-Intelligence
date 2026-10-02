# NEXUS AI — Pro Intelligence Architecture

## Product principle

NEXUS AI is a unified enterprise intelligence layer. Users ask for outcomes in one natural-language command; they do not need to select Analytics, Charts, Research, Verification or Reports manually.

## Execution model

`Command → Intent → Execution Plan → Retrieval/Data → Agents → Verification → Dynamic Results`

The intent router converts a request into an execution plan such as:

- search
- data_analysis
- visualization
- external_research
- evidence_verification
- business_intelligence
- comparison
- risk_analysis
- opportunity_analysis
- report_generation

Only requested/relevant operations are rendered.

## Intelligence layers

1. **Workspace knowledge** — PDF, DOCX and TXT evidence with page/source metadata.
2. **Business intelligence** — CSV/XLSX profiling, quality checks, metrics, trends, correlations and real-data Plotly charts.
3. **External research** — Semantic Scholar, OpenAlex and Crossref provider adapters.
4. **Reasoning** — Groq/LangChain synthesis over retrieved evidence and computed data.
5. **Verification** — evidence strength classification and explicit uncertainty.
6. **Citation layer** — source metadata is preserved; missing metadata is not fabricated.
7. **Reporting** — requested reports are generated from the executed workflow.

## Company-facing behavior

A request such as:

> Analyze our sales performance, show monthly revenue and top products, identify risks, research current market conditions, verify the evidence and prepare an executive report.

can activate data analysis, charts, external research, evidence verification, business insights and report generation in one execution.

## UI rule

The sidebar is intentionally restricted to workspace ingestion. The main workspace is the command center. This prevents tool fragmentation while retaining modular backend services.

## Trust rule

NEXUS must never present generated information as verified without evidence. External and local sources remain distinguishable, and unavailable metadata is represented as unavailable.

## Scale path

The MVP boundaries allow migration from SQLite → PostgreSQL and FAISS → pgvector without redesigning the command center or agent contracts.
