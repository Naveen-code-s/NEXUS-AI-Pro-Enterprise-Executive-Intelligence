from agents.business_advisor import BusinessAdvisor
import pandas as pd
from rag.chunker import chunk_pages
from search.global_search import dedup
def test_chunk_page_metadata(): assert chunk_pages([{"page":4,"text":"x"*1000}],300,20)[0]["metadata"]["page"]==4
def test_dedup(): assert len(dedup([{"title":"A"},{"title":"A"}]))==1


def test_business_advisor_has_decision_metadata():
    df = pd.DataFrame({
        "month": ["2026-01", "2026-02", "2026-03"],
        "product": ["A", "A", "B"],
        "region": ["North", "North", "South"],
        "revenue": [1000, 1400, 600],
        "cost": [500, 700, 400],
    })
    result = BusinessAdvisor().run([{"dataframe": df, "insights": []}], "improve revenue")
    assert result["kpis"]
    assert result["opportunities"]
    assert all("confidence" in x and "validation" in x for x in result["opportunities"])
