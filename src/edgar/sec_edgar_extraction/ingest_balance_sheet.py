import re   
from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
import sec_parser as sp
from edgar.models.financial_statement_items import BalanceSheetItems

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from edgar.models.financial_statement_items import BalanceSheetItems

def extract_total_assets(text):
    match = re.search(r"Total assets\$(\d{1,3}(?:,\d{3})*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def extract_cash_and_equivalents(text):
    match = re.search(r"Cash and cash equivalents\$(\d{1,3}(?:,\d{3})*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def find_balance_sheet(tree):
    pattern = r"balance\s*sheets?"
    def _search(node):
        if hasattr(node, "text") and re.search(pattern, node.text, re.IGNORECASE):
            return node
        for child in getattr(node, "nodes", []):
            result = _search(child)
            if result:
                return result
        return None
    return _search(tree)

def get_balance_sheet(tree, cik, form_type, filing_date, document_url, fiscal_year, fiscal_quarter=None):
    node = find_balance_sheet(tree)
    if not node:
        raise ValueError("Balance Sheet section not found.")
    balance_text = ""
    for child in getattr(node, "children", []):
        if hasattr(child, "text") and "total assets" in child.text.lower():
            balance_text = child.text
            break
    if not balance_text and getattr(node, "children", []):
        balance_text = getattr(node.children[0], "text", "")
    if not balance_text:
        raise ValueError("No balance sheet text found.")

    return BalanceSheetItems(
        cik=cik,
        form_type=form_type,
        filing_date=filing_date,
        document_url=document_url,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
        total_assets=extract_total_assets(balance_text),
        cash_and_equivalents=extract_cash_and_equivalents(balance_text),
        # Add more fields as needed
    )

def get_company_balance_sheet(
    ticker: str,
    form_type: str = "10-Q",
    year: int = None,
    quarter: int = None,
    user_agent: str = "YourCompany your.email@example.com"
) -> BalanceSheetItems:
    """
    Fetch and extract a company's balance sheet from SEC EDGAR.
    """
    dl = Downloader("YourCompany", user_agent)
    filings = dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=ticker, form_type=form_type, limit=1))
    if not filings:
        raise ValueError(f"No filings found for {ticker} ({form_type})")
    meta = filings[0]
    cik = meta.cik
    filing_date = meta.filing_date
    document_url = meta.primary_doc_url

    html = dl.download_filing(url=document_url).decode()
    elements = sp.Edgar10QParser().parse(html)
    tree = sp.TreeBuilder().build(elements)

    return get_balance_sheet(
        tree=tree,
        cik=cik,
        form_type=form_type,
        filing_date=filing_date,
        document_url=document_url,
        fiscal_year=year,
        fiscal_quarter=quarter,
    )

if __name__ == "__main__":
    bs = get_company_balance_sheet("AAPL", form_type="10-Q", year=2024, quarter=2)
    print(bs)