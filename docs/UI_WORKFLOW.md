# NEXUS AI Pro UI Workflow

## Product interaction model

NEXUS AI uses one primary intelligence surface rather than forcing the user through separate feature pages.

### Sidebar
The sidebar is intentionally limited to:
- NEXUS AI branding
- workspace file upload
- model/status context

Supported uploads:
- PDF / DOCX / TXT -> evidence knowledge base
- CSV / XLSX -> business intelligence datasets

### Main command surface
The main page contains one command box. A single request can combine multiple capabilities:

> Analyze our revenue trend, compare it with the uploaded market research, verify the supporting evidence, and prepare an executive report.

The intent router detects which capabilities are required. The orchestrator then composes the shared agents and services instead of navigating to separate pages.

## Capability routing

- Knowledge questions -> local RAG
- Research/latest/literature -> external scholarly search + local evidence
- Dataset/business questions -> Data Agent + real uploaded CSV/XLSX data
- Evidence/citation/verification -> verification + citation services
- Report/briefing/export requests -> report generation
- Mixed requests -> multiple agents in one workflow

## Evidence policy

Every source is normalized to a common source contract. Missing fields remain unavailable rather than being fabricated.

Verification levels:
- Direct evidence
- Related evidence
- Insufficient evidence

The system should never invent a page number, DOI, URL, statistic, or source.
