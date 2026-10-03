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

    The UI does not need to know which tool to open.
    User intent determines the execution plan, and the returned
    result contains only the operations that actually ran.
    """

    def run(self, settings, q, mode="auto", dataset_paths=None):
        intent = classify(q)
        dataset_paths = dataset_paths or []

        sources = []
        sections = []
        agents = []

        # ---------------------------------------------------------
        # DATA INTELLIGENCE
        # ---------------------------------------------------------
        if intent.data:
            if dataset_paths:
                for path in dataset_paths[:3]:
                    try:
                        data_result = DataAgent().run(path, q)

                        sections.append(
                            {
                                "type": "data",
                                **data_result,
                            }
                        )

                        agents.append("Data Intelligence")

                    except Exception as exc:
                        sections.append(
                            {
                                "type": "warning",
                                "title": "Data analysis",
                                "message": (
                                    f"Dataset could not be analyzed: {exc}"
                                ),
                            }
                        )
            else:
                sections.append(
                    {
                        "type": "warning",
                        "title": "Business data",
                        "message": (
                            "No CSV/XLSX dataset is available. "
                            "Upload a dataset in the sidebar to activate "
                            "analytics and charts."
                        ),
                    }
                )

        # ---------------------------------------------------------
        # BUSINESS ADVISOR
        # ---------------------------------------------------------
        if intent.advice:
            data_sections = [
                section
                for section in sections
                if section.get("type") == "data"
            ]

            advice = BusinessAdvisor().run(
                data_sections,
                q,
            )

            sections.append(advice)
            agents.append("Business Advisor")

        # ---------------------------------------------------------
        # LOCAL KNOWLEDGE RETRIEVAL
        # ---------------------------------------------------------
        local = search_global(
            settings,
            q,
            local=True,
            external=False,
            limit=settings.top_k,
        )

        if local:
            sources.extend(local)
            agents.append("Knowledge Retrieval")

        # ---------------------------------------------------------
        # EXTERNAL RESEARCH
        # ---------------------------------------------------------
        if (
            intent.research
            or intent.external
            or mode == "research"
        ):
            external = search_global(
                settings,
                q,
                local=False,
                external=True,
                limit=settings.top_k,
            )

            sources.extend(external)
            agents.append("Research Intelligence")

        # ---------------------------------------------------------
        # SOURCE NORMALIZATION + DEDUPLICATION
        # ---------------------------------------------------------
        sources = self._dedupe_sources(sources)

        # ---------------------------------------------------------
        # EVIDENCE VERIFICATION
        # ---------------------------------------------------------
        evidence = (
            VerificationAgent().run(q, sources)
            if (intent.evidence or sources)
            else []
        )

        # ---------------------------------------------------------
        # CITATION GENERATION
        # ---------------------------------------------------------
        citations = CitationAgent().run(sources)

        if sources:
            agents.append("Citation Intelligence")

        if evidence:
            agents.append("Evidence Verification")

        # ---------------------------------------------------------
        # NEXUS REASONING / SYNTHESIS
        # ---------------------------------------------------------
        grounded = self._synthesize(
            settings,
            q,
            sources,
            sections,
            intent,
        )

        if grounded:
            sections.insert(
                0,
                {
                    "type": "answer",
                    "title": "NEXUS synthesis",
                    "answer": grounded,
                },
            )

            agents.append("NEXUS Reasoning")

        # ---------------------------------------------------------
        # REPORT GENERATION
        # ---------------------------------------------------------
        report_path = None

        if intent.report:
            report_path = generate(
                settings,
                "NEXUS AI Intelligence Report",
                grounded or "Evidence not available.",
                citations,
                evidence,
            )

            sections.append(
                {
                    "type": "report",
                    "path": report_path,
                }
            )

            agents.append("Report Intelligence")

        # ---------------------------------------------------------
        # BUSINESS INTELLIGENCE
        # ---------------------------------------------------------
        if intent.business:
            sections.append(
                {
                    "type": "business",
                    "title": "Business intelligence",
                    "insights": self._business_insights(
                        q,
                        sections,
                        sources,
                    ),
                }
            )

            agents.append("Business Intelligence")

        # ---------------------------------------------------------
        # EXECUTIVE SUMMARY
        # ---------------------------------------------------------
        executive_summary = self._executive_summary(
            q,
            sections,
            evidence,
            sources,
        )

        # ---------------------------------------------------------
        # FINAL RESPONSE
        # ---------------------------------------------------------
        return {
            "query": q,
            "answer": (
                grounded
                or (
                    "Evidence not available. Upload relevant "
                    "workspace material or request an external "
                    "research query."
                )
            ),
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

    # =============================================================
    # SOURCE DEDUPLICATION
    # =============================================================

    @staticmethod
    def _dedupe_sources(items):
        """Normalize source collection and remove duplicate sources."""

        out = []
        seen = set()

        if not isinstance(items, (list, tuple)):
            return out

        for item in items:
            if not isinstance(item, dict):
                continue

            key = (
                item.get("doi")
                or item.get("source_id")
                or item.get("title")
                or ""
            )

            key = str(key).strip().lower()

            if key and key not in seen:
                seen.add(key)
                out.append(item)

        return out

    # =============================================================
    # NEXUS SYNTHESIS
    # =============================================================

    @staticmethod
    def _synthesize(
        settings,
        query,
        sources,
        sections,
        intent,
    ):
        """Create a grounded answer from retrieved evidence and data.

        Important:
        - Never invent citations.
        - Never invent statistics.
        - Never invent DOI/URLs/page numbers.
        - Use uploaded dataset calculations when available.
        - Clearly communicate when evidence is insufficient.
        """

        evidence = []

        # ---------------------------------------------------------
        # BUILD EVIDENCE CONTEXT
        # ---------------------------------------------------------
        for source in sources[:8]:
            title = source.get("title") or "Not available"

            passage = (
                source.get("abstract")
                or source.get("passage")
                or source.get("snippet")
                or source.get("text")
                or "Evidence not available"
            )

            passage = str(passage)

            evidence.append(
                f"SOURCE: {title}\n"
                f"{passage[:1800]}"
            )

        # ---------------------------------------------------------
        # BUILD COMPUTED DATA CONTEXT
        # ---------------------------------------------------------
        data_context = []

        for section in sections:
            if section.get("type") != "data":
                continue

            answer = section.get("answer")

            if answer:
                data_context.append(
                    str(answer)
                )

            # Include deterministic insights if answer is empty.
            insights = section.get("insights", [])

            if insights and not answer:
                data_context.extend(
                    str(item)
                    for item in insights
                    if item
                )

        # ---------------------------------------------------------
        # NOTHING TO SYNTHESIZE
        # ---------------------------------------------------------
        if not evidence and not data_context:
            return ""

        # ---------------------------------------------------------
        # SAFE STRING JOIN
        # ---------------------------------------------------------
        computed_data_text = "\n\n".join(
            data_context
        )

        evidence_text = "\n\n".join(
            evidence
        )

        # ---------------------------------------------------------
        # GROUNDED LLM PROMPT
        # ---------------------------------------------------------
        prompt = (
            "You are NEXUS AI, an enterprise intelligence "
            "reasoning layer. "
            "Answer the user's request using only the supplied "
            "evidence and computed data. "
            "Do not invent facts, citations, statistics, URLs, "
            "DOI values, or page numbers. "
            "Clearly state uncertainty when evidence is insufficient. "
            "Keep the response decision-useful.\n\n"

            f"USER REQUEST:\n"
            f"{query}\n\n"

            f"COMPUTED DATA:\n"
            f"{computed_data_text}\n\n"

            f"EVIDENCE:\n"
            f"{evidence_text}"
        )

        # ---------------------------------------------------------
        # LLM INVOCATION
        # ---------------------------------------------------------
        response = invoke(
            settings,
            prompt,
        )

        if response:
            return response

        # ---------------------------------------------------------
        # DETERMINISTIC FALLBACK
        # ---------------------------------------------------------
        if data_context:
            return data_context[0]

        return ""

    # =============================================================
    # EXECUTIVE SUMMARY
    # =============================================================

    @staticmethod
    def _executive_summary(
        query,
        sections,
        evidence,
        sources,
    ):
        """Build a concise deterministic executive summary."""

        data_sections = [
            section
            for section in sections
            if section.get("type") == "data"
        ]

        advice = next(
            (
                section
                for section in sections
                if section.get("type") == "business_advice"
            ),
            None,
        )

        findings = []

        # ---------------------------------------------------------
        # DATA FINDINGS
        # ---------------------------------------------------------
        for section in data_sections:
            insights = section.get("insights", [])

            if isinstance(insights, list):
                findings.extend(
                    str(item)
                    for item in insights[:2]
                    if item
                )

        parts = []

        if findings:
            parts.append(
                "Key observed findings: "
                + " ".join(findings[:3])
            )

        # ---------------------------------------------------------
        # BUSINESS ADVICE
        # ---------------------------------------------------------
        if advice:
            opportunities = advice.get(
                "opportunities",
                [],
            )

            risks = advice.get(
                "risks",
                [],
            )

            parts.append(
                "Decision support: "
                f"{len(opportunities)} opportunity signals "
                f"and {len(risks)} risk signals were identified."
            )

        # ---------------------------------------------------------
        # SOURCE COUNT
        # ---------------------------------------------------------
        if sources:
            parts.append(
                "Evidence base: "
                f"{len(sources)} unique source(s) were retrieved."
            )

        # ---------------------------------------------------------
        # VERIFICATION COUNT
        # ---------------------------------------------------------
        if evidence:
            direct = sum(
                1
                for item in evidence
                if item.get("level") == "Direct evidence"
            )

            calculated = sum(
                1
                for item in evidence
                if item.get("level") == "Calculated evidence"
            )

            conflicting = sum(
                1
                for item in evidence
                if item.get("level") == "Conflicting evidence"
            )

            verification_parts = []

            if direct:
                verification_parts.append(
                    f"{direct} direct"
                )

            if calculated:
                verification_parts.append(
                    f"{calculated} calculated"
                )

            if conflicting:
                verification_parts.append(
                    f"{conflicting} conflicting"
                )

            if verification_parts:
                parts.append(
                    "Verification: "
                    + ", ".join(verification_parts)
                    + " evidence item(s) were identified."
                )

        # ---------------------------------------------------------
        # FINAL SUMMARY
        # ---------------------------------------------------------
        if parts:
            return " ".join(parts)

        return (
            "NEXUS completed the requested workflow, "
            "but the available evidence was insufficient "
            "for a stronger executive summary."
        )

    # =============================================================
    # BUSINESS INSIGHTS
    # =============================================================

    @staticmethod
    def _business_insights(
        query,
        sections,
        sources,
    ):
        """Collect business-relevant insights from executed operations."""

        insights = []

        # ---------------------------------------------------------
        # DATA INSIGHTS
        # ---------------------------------------------------------
        for section in sections:
            if section.get("type") != "data":
                continue

            section_insights = section.get(
                "insights",
                [],
            )

            if isinstance(section_insights, list):
                insights.extend(
                    str(item)
                    for item in section_insights[:4]
                    if item
                )

        # ---------------------------------------------------------
        # SOURCE-BASED BUSINESS CONTEXT
        # ---------------------------------------------------------
        if not insights and sources:
            insights.append(
                f"{len(sources)} evidence sources were retrieved "
                "for the business request."
            )

        # ---------------------------------------------------------
        # NO EVIDENCE
        # ---------------------------------------------------------
        if not insights:
            insights.append(
                "Business-specific evidence is not available yet."
            )

        return insights