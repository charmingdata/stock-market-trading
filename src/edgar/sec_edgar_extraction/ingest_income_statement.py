import re
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from edgar.models.financial_statement_items import IncomeStatementItems

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
    Extracts income statement data from a parsed SEC filing tree.

    Args:
        tree: The parsed document tree (from sec_parser).
        cik: The Central Index Key of the company.
        form_type: The SEC form type (e.g., "10-Q").
        filing_date: The filing date.
        document_url: URL to the primary document.
        fiscal_year: Fiscal year of the statement.
        fiscal_quarter: Fiscal quarter of the statement (optional).

    Returns:
        IncomeStatementItems: An object containing extracted income statement fields.

    Raises:
        ValueError: If the income statement section or text cannot be found.
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
    """
    Recursively searches a parsed document tree for the income statement section node.

    Args:
        tree: The parsed document tree (from sec_parser).

    Returns:
        The node corresponding to the income statement section if found, otherwise None.
    """
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
