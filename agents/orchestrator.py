from agents.document_agent import DocumentAgent
from agents.data_agent import DataAgent
from agents.verification_agent import VerificationAgent
from agents.citation_agent import CitationAgent
from agents.business_advisor import BusinessAdvisor
from core.intent_router import classify
from core.llm import invoke
from search.global_search import search_global
from reports.generator import generate


class Orchestrator:
    """Unified command-to-intelligence execution engine.

    The UI never needs to know which tool to open. Intent determines the
    execution plan, and the returned result contains only the operations
    that actually ran.
    """

    def run(self, settings, q, mode="auto", dataset_paths=None):
        intent = classify(q)
        dataset_paths = dataset_paths or []
        sources = []
        sections = []
        agents = []

        if intent.data:
            if dataset_paths:
                for path in dataset_paths[:3]:
                    try:
                        data_result = DataAgent().run(path, q)
                        sections.append({"type": "data", **data_result})
                        agents.append("Data Intelligence")
                    except Exception as exc:
                        sections.append({"type": "warning", "title": "Data analysis", "message": f"Dataset could not be analyzed: {exc}"})
            else:
                sections.append({"type": "warning", "title": "Business data", "message": "No CSV/XLSX dataset is available. Upload a dataset in the sidebar to activate analytics and charts."})

        if intent.advice:
            data_sections = [s for s in sections if s.get("type") == "data"]
            advice = BusinessAdvisor().run(data_sections, q)
            sections.append(advice)
            agents.append("Business Advisor")

        local = search_global(settings, q, local=True, external=False, limit=settings.top_k)
        if local:
            sources.extend(local)
            agents.append("Knowledge Retrieval")

        if intent.research or intent.external or mode == "research":
            external = search_global(settings, q, local=False, external=True, limit=settings.top_k)
            sources.extend(external)
            agents.append("Research Intelligence")

        # Normalize and deduplicate before verification.
        sources = self._dedupe_sources(sources)
        evidence = VerificationAgent().run(q, sources) if (intent.evidence or sources) else []
        citations = CitationAgent().run(sources)
        if sources:
            agents.append("Citation Intelligence")
        if evidence:
            agents.append("Evidence Verification")

        grounded = self._synthesize(settings, q, sources, sections, intent)
        if grounded:
            sections.insert(0, {"type": "answer", "title": "NEXUS synthesis", "answer": grounded})
            agents.append("NEXUS Reasoning")

        report_path = None
        if intent.report:
            report_path = generate(
                settings,
                "NEXUS AI Intelligence Report",
                grounded or "Evidence not available.",
                citations,
                evidence,
            )
            sections.append({"type": "report", "path": report_path})
            agents.append("Report Intelligence")

        if intent.business:
            sections.append({"type": "business", "title": "Business intelligence", "insights": self._business_insights(q, sections, sources)})
            agents.append("Business Intelligence")

        executive_summary = self._executive_summary(q, sections, evidence, sources)

        return {
            "query": q,
            "answer": grounded or "Evidence not available. Upload relevant workspace material or request an external research query.",
            "executive_summary": executive_summary,
            "sources": citations,
            "evidence": evidence,
            "sections": sections,
            "agents_used": list(dict.fromkeys(agents)),
            "intent": intent.__dict__,
            "operations": intent.operations,
            "report_requested": intent.report,
            "report_path": report_path,
        }

    @staticmethod
    def _dedupe_sources(items):
        out, seen = [], set()
        for item in items:
            if not isinstance(item, dict):
                continue
            key = (item.get("doi") or item.get("source_id") or item.get("title") or "").strip().lower()
            if key and key not in seen:
                seen.add(key)
                out.append(item)
        return out

    @staticmethod
    def _synthesize(settings, query, sources, sections, intent):
        evidence = []
        for s in sources[:8]:
            title = s.get("title") or "Not available"
            passage = s.get("abstract") or s.get("passage") or "Evidence not available"
            evidence.append(f"SOURCE: {title}\n{passage[:1800]}")
        data_context = [s.get("answer", "") for s in sections if s.get("type") == "data"]
        if not evidence and not data_context:
            return ""
        prompt = (
            "You are NEXUS AI, an enterprise intelligence reasoning layer. "
            "Answer the user's request using only the supplied evidence and computed data. "
            "Do not invent facts, citations, statistics, URLs, DOI values, or page numbers. "
            "Clearly state uncertainty when evidence is insufficient. Keep the response decision-useful.\n\n"
            f"USER REQUEST:\n{query}\n\nCOMPUTED DATA:\n{'\n\n'.join(data_context)}\n\nEVIDENCE:\n{'\n\n'.join(evidence)}"
        )
        return invoke(settings, prompt) or (data_context[0] if data_context else "")


    @staticmethod
    def _executive_summary(query, sections, evidence, sources):
        data = [s for s in sections if s.get("type") == "data"]
        advice = next((s for s in sections if s.get("type") == "business_advice"), None)
        findings = []
        for section in data:
            findings.extend(section.get("insights", [])[:2])
        parts = []
        if findings:
            parts.append("Key observed findings: " + " ".join(findings[:3]))
        if advice:
            parts.append(f"Decision support: {len(advice.get('opportunities', []))} opportunity signals and {len(advice.get('risks', []))} risk signals were identified.")
        if sources:
            parts.append(f"Evidence base: {len(sources)} unique source(s) were retrieved.")
        if evidence:
            direct = sum(1 for e in evidence if e.get("level") == "Direct evidence")
            parts.append(f"Verification: {direct} source(s) were classified as direct evidence.")
        return " ".join(parts) or "NEXUS completed the requested workflow, but the available evidence was insufficient for a stronger executive summary."

    @staticmethod
    def _business_insights(query, sections, sources):
        insights = []
        for s in sections:
            if s.get("type") == "data":
                insights.extend(s.get("insights", [])[:4])
        if not insights and sources:
            insights.append(f"{len(sources)} evidence sources were retrieved for the business request.")
        if not insights:
            insights.append("Business-specific evidence is not available yet.")
        return insights
