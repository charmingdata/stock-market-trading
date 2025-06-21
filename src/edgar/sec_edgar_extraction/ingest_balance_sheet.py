import re   
from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
import sec_parser as sp

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from edgar.models.financial_statement_items import BalanceSheetItems

def extract_total_assets(text):
    """
    Extract the total assets from text.
    """
    match = re.search(r"Total assets\$(\d{1,3}(?:,\d{3})*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def extract_cash_and_equivalents(text):
    """
    Extract cash-and-equivalents from text.
    """
    match = re.search(r"Cash and cash equivalents\$(\d{1,3}(?:,\d{3})*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def find_balance_sheet(tree):
    """
    Recursively searches a parsed document tree for the balance sheet section node.

    Args:
        tree: The parsed document tree (from sec_parser).

    Returns:
        The node corresponding to the balance sheet section if found, otherwise None.
    """
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
    """
    Extracts balance sheet data from a parsed SEC filing tree.

    Args:
        tree: The parsed document tree (from sec_parser).
        cik: The Central Index Key of the company.
        form_type: The SEC form type (e.g., "10-Q").
        filing_date: The filing date.
        document_url: URL to the primary document.
        fiscal_year: Fiscal year of the statement.
        fiscal_quarter: Fiscal quarter of the statement (optional).

    Returns:
        BalanceSheetItems: An object containing extracted balance sheet fields.

    Raises:
        ValueError: If the balance sheet section or text cannot be found.
    """    
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
    Downloads, parses, and extracts a company's balance sheet from the SEC EDGAR system.

    This function handles the entire workflow:
    - Downloads the latest SEC filing for the given ticker and form type.
    - Parses the filing to extract the document tree.
    - Locates and extracts the balance sheet section.
    - Parses out key financial fields (e.g., total assets, cash and equivalents).
    - Returns a BalanceSheetItems object with the extracted data.

    Args:
        ticker (str): The company's ticker symbol or CIK.
        form_type (str): The SEC form type to retrieve (default: "10-Q").
        year (int, optional): Fiscal year of the statement.
        quarter (int, optional): Fiscal quarter of the statement.
        user_agent (str): User agent string for SEC requests.

    Returns:
        BalanceSheetItems: An object containing extracted balance sheet fields.

    Raises:
        ValueError: If no filings are found or if the balance sheet section cannot be extracted.
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