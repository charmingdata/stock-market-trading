import pytest
from datetime import datetime
from src.edgar.sec_edgar_extraction.ingest_income_statement import (
    extract_net_sales,
    extract_net_income,
    get_income_statement,
)

class DummyNode:
    def __init__(self, text):
        self.text = text
        self.children = []

def test_extract_net_sales():
    text = "Net sales$95,359"
    assert extract_net_sales(text) == 95359.0

def test_extract_net_income():
    text = "Net income$24,780"
    assert extract_net_income(text) == 24780.0

def test_get_income_statement(monkeypatch):
    income_text = (
        "Net sales$95,359\n"
        "Net income$24,780"
    )
    node = DummyNode("CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)")
    child = DummyNode(income_text)
    node.children = [child]

    def fake_find_income_statement(tree):
        return node

    monkeypatch.setattr(
        "src.edgar.sec_edgar_extraction.ingest_income_statement.find_income_statement",
        fake_find_income_statement,
    )

    result = get_income_statement(
        tree=None,
        cik="0000320193",
        form_type="10-Q",
        filing_date=datetime(2024, 3, 30),
        document_url="http://example.com",
        fiscal_year=2024,
        fiscal_quarter=2,
    )
    assert result.revenue == 95359.0
    assert result.net_income == 24780.0

def test_get_income_statement_no_section(monkeypatch):
    def fake_find_income_statement(tree):
        return None

    monkeypatch.setattr(
        "src.edgar.sec_edgar_extraction.ingest_income_statement.find_income_statement",
        fake_find_income_statement,
    )

    with pytest.raises(ValueError, match="Income Statement section not found."):
        get_income_statement(
            tree=None,
            cik="0000320193",
            form_type="10-Q",
            filing_date=datetime(2024, 3, 30),
            document_url="http://example.com",
            fiscal_year=2024,
            fiscal_quarter=2,
        )