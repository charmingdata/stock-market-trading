import pytest
from datetime import datetime
from src.edgar.sec_edgar_extraction.ingest_balance_sheet import (
    extract_total_assets,
    extract_cash_and_equivalents,
    get_balance_sheet,
)

class DummyNode:
    def __init__(self, text):
        self.text = text
        self.children = []

def test_extract_total_assets():
    text = "Total assets$331,233"
    assert extract_total_assets(text) == 331233.0

def test_extract_cash_and_equivalents():
    text = "Cash and cash equivalents$28,162"
    assert extract_cash_and_equivalents(text) == 28162.0

def test_get_balance_sheet(monkeypatch):
    balance_text = (
        "Total assets$331,233\n"
        "Cash and cash equivalents$28,162"
    )
    node = DummyNode("CONDENSED CONSOLIDATED BALANCE SHEETS (Unaudited)")
    child = DummyNode(balance_text)
    node.children = [child]

    def fake_find_balance_sheet(tree):
        return node

    monkeypatch.setattr(
        "src.edgar.sec_edgar_extraction.ingest_balance_sheet.find_balance_sheet",
        fake_find_balance_sheet,
    )

    result = get_balance_sheet(
        tree=None,
        cik="0000320193",
        form_type="10-Q",
        filing_date=datetime(2024, 3, 30),
        document_url="http://example.com",
        fiscal_year=2024,
        fiscal_quarter=2,
    )
    assert result.total_assets == 331233.0
    assert result.cash_and_equivalents == 28162.0

def test_get_balance_sheet_no_section(monkeypatch):
    def fake_find_balance_sheet(tree):
        return None

    monkeypatch.setattr(
        "src.edgar.sec_edgar_extraction.ingest_balance_sheet.find_balance_sheet",
        fake_find_balance_sheet,
    )

    with pytest.raises(ValueError, match="Balance Sheet section not found."):
        get_balance_sheet(
            tree=None,
            cik="0000320193",
            form_type="10-Q",
            filing_date=datetime(2024, 3, 30),
            document_url="http://example.com",
            fiscal_year=2024,
            fiscal_quarter=2,
        )