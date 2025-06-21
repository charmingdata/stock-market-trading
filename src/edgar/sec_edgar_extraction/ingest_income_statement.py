import re
from datetime import datetime
from src.edgar.models.financial_statement_items import IncomeStatementItems

def extract_net_sales(text):
    match = re.search(r"Net sales\$(\d{1,3}(?:,\d{3})*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def extract_net_income(text):
    match = re.search(r"Net income\$(\d{1,3}(?:,\d{3})*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def get_income_statement(tree, cik, form_type, filing_date, document_url, fiscal_year, fiscal_quarter=None):
    """
    Extracts income statement data from the parsed tree and returns an IncomeStatementItems model.
    """
    node = find_income_statement(tree)
    if not node:
        raise ValueError("Income Statement section not found.")
    income_text = ""
    for child in getattr(node, "children", []):
        if hasattr(child, "text") and "net sales" in child.text.lower():
            income_text = child.text
            break
    if not income_text and getattr(node, "children", []):
        income_text = getattr(node.children[0], "text", "")
    if not income_text:
        raise ValueError("No income statement text found.")

    return IncomeStatementItems(
        cik=cik,
        form_type=form_type,
        filing_date=filing_date,
        document_url=document_url,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
        revenue=extract_net_sales(income_text),
        net_income=extract_net_income(income_text),
        # Add more fields as needed
    )

def find_income_statement(tree):
    pattern = r"statements?.*(operations|income)"
    def _search(node):
        if hasattr(node, "text") and re.search(pattern, node.text, re.IGNORECASE):
            return node
        for child in getattr(node, "nodes", []):
            result = _search(child)
            if result:
                return result
        return None
    return _search(tree)