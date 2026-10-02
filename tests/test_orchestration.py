from pathlib import Path
import pandas as pd

from core.intent_router import classify
from analytics.visualizer import build_charts


def test_unified_command_creates_execution_plan():
    intent = classify("Analyze sales, show graphs, research the market, verify evidence and prepare a report")
    assert "data_analysis" in intent.operations
    assert "visualization" in intent.operations
    assert "external_research" in intent.operations
    assert "evidence_verification" in intent.operations
    assert "report_generation" in intent.operations


def test_visualization_uses_real_columns():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-02-01", "2026-03-01"],
        "revenue": [100, 140, 120],
        "product": ["A", "B", "A"],
    })
    charts = build_charts(df, "show revenue trend and compare products")
    titles = [c["title"] for c in charts]
    assert any("Monthly trend" in t for t in titles)
    assert any("Top product" in t for t in titles)

from agents.business_advisor import BusinessAdvisor


def test_business_advisor_is_grounded_in_uploaded_data():
    df = pd.DataFrame({
        "month": ["2026-01", "2026-02", "2026-03"],
        "product": ["A", "A", "B"],
        "revenue": [1000, 1400, 600],
        "unit_cost": [500, 700, 400],
    })
    result = BusinessAdvisor().run([{"dataframe": df, "insights": []}], "improve revenue and advise us")
    assert result["opportunities"]
    assert result["alternatives"]
    assert any("A" in item["action"] or "A" in item["title"] for item in result["opportunities"])


def test_advice_intent_for_revenue_improvement():
    intent = classify("How can we improve revenue and give us different business strategies?")
    assert intent.data
    assert intent.advice
    assert "business_advice" in intent.operations
