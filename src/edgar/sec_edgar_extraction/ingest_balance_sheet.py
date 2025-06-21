import re
from datetime import datetime
from src.edgar.models.financial_statement_items import BalanceSheetItems

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

def get_balance_sheet(tree, cik, form_type, filing_date, document_url, fiscal_year, fiscal_quarter=None):
    """
    Extracts balance sheet data from the parsed tree and returns a BalanceSheetItems model.
    """
    # ...find the balance sheet node and extract text as before...
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