from __future__ import annotations

from typing import Any
import pandas as pd


class BusinessAdvisor:
    """Create grounded, decision-oriented business advice from observed data.

    Every recommendation includes evidence basis, expected business impact,
    implementation effort, confidence, and an explicit validation step. The
    advisor never invents revenue forecasts or guaranteed outcomes.
    """

    name = "Business Advisor"

    def run(self, data_sections: list[dict[str, Any]], query: str = "") -> dict[str, Any]:
        opportunities: list[dict[str, Any]] = []
        risks: list[dict[str, Any]] = []
        alternatives: list[dict[str, Any]] = []
        next_steps: list[dict[str, Any]] = []
        kpis: list[dict[str, Any]] = []

        for section in data_sections:
            df = section.get("dataframe")
            if isinstance(df, pd.DataFrame) and not df.empty:
                self._analyze_dataframe(df, opportunities, risks, alternatives, next_steps, kpis)
            else:
                self._use_existing_insights(section, opportunities, risks)

        if not opportunities:
            opportunities.append(self._item(
                "Improve decision visibility",
                "Establish a consistent KPI baseline before changing strategy.",
                "The available data is not detailed enough for a grounded growth recommendation.",
                "Medium", "Low", "Low", "Add revenue, cost, customer, product and time-period fields where available.",
            ))
        if not risks:
            risks.append(self._item(
                "No material risk signal detected from available fields",
                "Treat this as an absence of detected evidence, not proof that the business has no risks.",
                "The current dataset did not trigger a specific risk rule.",
                "Medium", "Low", "Low", "Run the analysis again with customer, cost, retention and operational fields.",
            ))
        if not alternatives:
            alternatives = [
                self._item("Optimize existing business", "Improve the strongest observed segments before adding major new spend.", "General decision framework; validate against company constraints.", "Medium", "Medium", "Low", "Run a controlled optimization test."),
                self._item("Expand selectively", "Pilot one promising segment, offer or region with a measurable target before scaling.", "General decision framework.", "Medium", "Medium", "Medium", "Define a pilot and baseline KPI."),
                self._item("Protect profitability", "Evaluate pricing and unit economics alongside revenue growth.", "General decision framework.", "Medium", "High", "Medium", "Track revenue, cost and margin together."),
            ]
        if not next_steps:
            next_steps = [
                {"step": 1, "action": "Validate the strongest finding against current business constraints and customer feedback.", "owner": "Business / Operations", "kpi": "Decision baseline"},
                {"step": 2, "action": "Choose one measurable experiment rather than changing multiple variables at once.", "owner": "Growth / Product", "kpi": "Experiment KPI"},
                {"step": 3, "action": "Review the result against the baseline and scale only if the evidence supports it.", "owner": "Management", "kpi": "Target vs actual"},
            ]

        return {
            "type": "business_advice",
            "title": "NEXUS Business Advisor",
            "summary": self._summary(opportunities, risks),
            "kpis": kpis[:8],
            "opportunities": opportunities[:8],
            "risks": risks[:8],
            "alternatives": alternatives[:6],
            "next_steps": next_steps[:6],
            "decision_note": "Use these as evidence-grounded options. They are not guaranteed revenue forecasts or financial advice.",
            "disclaimer": "Recommendations are derived from available workspace data and explicit decision rules; validate before implementation.",
        }

    @staticmethod
    def _item(title, action, basis, confidence="Medium", impact="Medium", effort="Medium", validation="Validate with a defined KPI"):
        return {
            "title": title,
            "action": action,
            "basis": basis,
            "confidence": confidence,
            "impact": impact,
            "effort": effort,
            "validation": validation,
        }

    @staticmethod
    def _summary(opportunities, risks):
        if opportunities and risks:
            return f"NEXUS identified {len(opportunities)} actionable opportunity signals and {len(risks)} risk signals from the available business evidence."
        return "NEXUS generated decision-support guidance from the available evidence."

    @staticmethod
    def _analyze_dataframe(df, opportunities, risks, alternatives, next_steps, kpis):
        cols = {str(c).lower(): c for c in df.columns}
        revenue_col = next((cols[k] for k in cols if any(x in k for x in ("revenue", "sales", "amount"))), None)
        cost_col = next((cols[k] for k in cols if any(x in k for x in ("cost", "expense"))), None)
        profit_col = next((cols[k] for k in cols if "profit" in k), None)
        product_col = next((cols[k] for k in cols if any(x in k for x in ("product", "item", "sku"))), None)
        region_col = next((cols[k] for k in cols if any(x in k for x in ("region", "territory", "market"))), None)

        if revenue_col:
            rev = pd.to_numeric(df[revenue_col], errors="coerce").dropna()
            if not rev.empty:
                total_revenue = float(rev.sum())
                kpis.append({"label": "Observed revenue", "value": total_revenue, "format": "currency", "basis": f"Sum of '{revenue_col}'."})
                if product_col:
                    grouped = df[[product_col, revenue_col]].copy()
                    grouped[revenue_col] = pd.to_numeric(grouped[revenue_col], errors="coerce")
                    grouped = grouped.dropna().groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
                    if len(grouped) >= 2 and grouped.sum() != 0:
                        top = str(grouped.index[0])
                        share = float(grouped.iloc[0] / grouped.sum() * 100)
                        kpis.append({"label": "Top product share", "value": share, "format": "percent", "basis": f"'{top}' share of observed revenue."})
                        opportunities.append(BusinessAdvisor._item(
                            f"Protect and grow the leading product: {top}",
                            f"Review availability, pricing, retention and acquisition around {top}; avoid assuming that current leadership will persist without validation.",
                            f"'{top}' represents approximately {share:.1f}% of observed revenue.",
                            "High", "High", "Medium",
                            "Track product revenue, margin, stock/availability and retention during the next review period.",
                        ))
                        alternatives.append(BusinessAdvisor._item(
                            "Diversify concentration",
                            "Use the leading product as a growth engine while testing the next two viable products or segments.",
                            f"Revenue concentration is approximately {share:.1f}% in '{top}'.",
                            "High", "Medium", "Medium",
                            "Measure the share of revenue outside the leading product over time.",
                        ))

                dates = _date_column(df)
                if dates:
                    trend = _monthly_sum(df, dates, revenue_col)
                    if len(trend) >= 2:
                        first = float(trend.iloc[0]["value"])
                        last = float(trend.iloc[-1]["value"])
                        change = ((last - first) / abs(first) * 100) if first else 0
                        kpis.append({"label": "First-to-last trend", "value": change, "format": "percent", "basis": "First vs last observed month."})
                        if change > 0:
                            opportunities.append(BusinessAdvisor._item(
                                "Investigate the observed growth pattern",
                                "Decompose the increase by product and region, then repeat the strongest observed driver in a controlled test instead of scaling everything equally.",
                                f"Observed revenue changed {change:+.1f}% from the first to the last available period.",
                                "High", "High", "Medium",
                                "Compare product and regional contribution in the next period.",
                            ))
                        elif change < 0:
                            risks.append(BusinessAdvisor._item(
                                "Investigate the observed revenue decline",
                                "Break the decline down by product and region before changing pricing, staffing or marketing spend.",
                                f"Observed revenue changed {change:+.1f}% from the first to the last available period.",
                                "High", "High", "Medium",
                                "Identify the top contributors to the decline and set a recovery KPI.",
                            ))

        if profit_col:
            profit = pd.to_numeric(df[profit_col], errors="coerce").dropna()
            if not profit.empty:
                kpis.append({"label": "Observed profit", "value": float(profit.sum()), "format": "currency", "basis": f"Sum of '{profit_col}'."})
                if (profit < 0).any():
                    risks.append(BusinessAdvisor._item(
                        "Loss-making records require review",
                        "Inspect pricing, discounts, unit cost and fulfillment costs for negative-profit records before pursuing volume growth.",
                        f"{int((profit < 0).sum())} records have negative '{profit_col}'.",
                        "High", "High", "Medium",
                        "Set a minimum acceptable margin and track the share of negative-profit records.",
                    ))

        if revenue_col and cost_col:
            rev = pd.to_numeric(df[revenue_col], errors="coerce")
            cost = pd.to_numeric(df[cost_col], errors="coerce")
            margin = ((rev - cost) / rev.replace(0, pd.NA) * 100).dropna()
            if not margin.empty:
                median_margin = float(margin.median())
                kpis.append({"label": "Median margin proxy", "value": median_margin, "format": "percent", "basis": f"Derived from '{revenue_col}' and '{cost_col}'."})
                opportunities.append(BusinessAdvisor._item(
                    "Use unit economics with revenue",
                    "Prioritize growth experiments that preserve healthy unit economics instead of optimizing revenue alone.",
                    f"Median observed margin proxy is {median_margin:.1f}%.",
                    "High", "High", "Medium",
                    "Track revenue, cost and margin together by product and region.",
                ))

        if region_col and revenue_col:
            grouped = df[[region_col, revenue_col]].copy()
            grouped[revenue_col] = pd.to_numeric(grouped[revenue_col], errors="coerce")
            grouped = grouped.dropna().groupby(region_col)[revenue_col].sum().sort_values(ascending=False)
            if len(grouped) >= 2:
                lead = str(grouped.index[0])
                alternatives.append(BusinessAdvisor._item(
                    "Regional resource allocation",
                    f"Compare the leading region ({lead}) with weaker regions before reallocating sales or marketing resources.",
                    f"Regional revenue distribution was calculated from '{revenue_col}'.",
                    "High", "Medium", "Medium",
                    "Compare growth rate and margin by region, not revenue alone.",
                ))

        next_steps.extend([
            {"step": 1, "action": "Validate the strongest finding against current business constraints and customer feedback.", "owner": "Business / Operations", "kpi": "Decision baseline"},
            {"step": 2, "action": "Run one measurable experiment on the highest-impact opportunity.", "owner": "Growth / Product", "kpi": "Experiment KPI"},
            {"step": 3, "action": "Compare actual results with the baseline before scaling the change.", "owner": "Management", "kpi": "Target vs actual"},
        ])

    @staticmethod
    def _use_existing_insights(section, opportunities, risks):
        for insight in section.get("insights", [])[:3]:
            text = str(insight)
            target = risks if any(w in text.lower() for w in ("risk", "missing", "decline", "negative")) else opportunities
            target.append(BusinessAdvisor._item("Data-driven observation", text, "Generated from uploaded dataset analysis.", "Medium", "Medium", "Low", "Validate the observation against source data."))


def _date_column(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
        if df[col].dtype == object:
            parsed = pd.to_datetime(df[col], format="mixed", errors="coerce")
            if parsed.notna().mean() >= 0.8 and parsed.nunique() > 2:
                return col
    return None


def _monthly_sum(df, date_col, value_col):
    tmp = pd.DataFrame({
        "date": pd.to_datetime(df[date_col], errors="coerce"),
        "value": pd.to_numeric(df[value_col], errors="coerce"),
    }).dropna()
    if tmp.empty:
        return pd.DataFrame(columns=["period", "value"])
    tmp["period"] = tmp["date"].dt.to_period("M").astype(str)
    return tmp.groupby("period", as_index=False)["value"].sum()
