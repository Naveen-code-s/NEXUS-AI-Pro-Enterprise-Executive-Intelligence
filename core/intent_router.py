from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class Intent:
    answer: bool = True
    search: bool = True
    data: bool = False
    charts: bool = False
    research: bool = False
    external: bool = False
    evidence: bool = False
    report: bool = False
    business: bool = False
    compare: bool = False
    risks: bool = False
    opportunities: bool = False
    advice: bool = False
    summary: bool = False
    operations: list[str] = field(default_factory=list)


def classify(query: str) -> Intent:
    q = re.sub(r"\s+", " ", (query or "").lower()).strip()
    research = any(w in q for w in ("research", "paper", "literature", "academic", "study", "doi", "scholar", "market research"))
    external = any(w in q for w in ("latest", "current", "external", "online", "web", "market", "competitor", "industry"))
    data = any(w in q for w in ("dataset", "csv", "xlsx", "data", "sales", "revenue", "profit", "margin", "customer", "orders", "inventory", "growth", "trend", "performance", "kpi", "forecast"))
    charts = any(w in q for w in ("chart", "graph", "visualize", "visualise", "plot", "trend", "distribution", "compare", "dashboard")) or data
    report = any(w in q for w in ("report", "executive summary", "board", "briefing", "presentation", "export"))
    evidence = any(w in q for w in ("citation", "cite", "source", "evidence", "verify", "verified", "proof", "page", "support"))
    business = any(w in q for w in ("business", "company", "strategy", "operation", "operations", "management", "decision", "revenue", "profit", "customer", "market", "competitor", "risk", "opportunity"))
    compare = any(w in q for w in ("compare", "comparison", "versus", "vs", "difference", "benchmark"))
    risks = any(w in q for w in ("risk", "risks", "threat", "problem", "weakness", "concern"))
    opportunities = any(w in q for w in ("opportunity", "opportunities", "potential", "upside", "growth"))
    advice = any(w in q for w in ("advice", "advise", "suggest", "suggestion", "recommend", "recommendation", "improve", "improvement", "increase revenue", "grow revenue", "boost revenue", "strategy", "strategies", "what should we do", "how can we improve"))
    # Business/data analysis automatically receives decision-support recommendations.
    advice = advice or (business and data)
    summary = any(w in q for w in ("summarize", "summary", "overview", "key findings", "insights"))

    ops = ["search"]
    if data: ops.append("data_analysis")
    if charts: ops.append("visualization")
    if research or external: ops.append("external_research")
    if evidence: ops.append("evidence_verification")
    if business: ops.append("business_intelligence")
    if compare: ops.append("comparison")
    if risks: ops.append("risk_analysis")
    if opportunities: ops.append("opportunity_analysis")
    if advice: ops.append("business_advice")
    if report: ops.append("report_generation")

    return Intent(
        data=data, charts=charts, research=research, external=external,
        evidence=evidence, report=report, business=business, compare=compare,
        risks=risks, opportunities=opportunities, advice=advice, summary=summary, operations=ops,
    )
