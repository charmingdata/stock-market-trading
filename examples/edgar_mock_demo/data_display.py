"""Display utilities for financial data."""
import json
from pathlib import Path
from typing import Dict, Any

def display_financial_data(data: Dict[str, Any]) -> None:
    """Display the extracted financial data in a formatted way."""
    print("\n===== Tesla Financial Data Summary =====\n")
    
    print(f"Company: {data['company']} ({data['ticker']})")
    print(f"Period Ending: {data['period_end']}")
    
    if data.get('source') == "mock":
        print("(Using mock data for demonstration)")
    
    print("\nIncome Statement:")
    print("─" * 50)
    for item, value in data.get('income_statement', {}).items():
        print(f"{item.ljust(30)} {value.rjust(18)}")
    
    print("\nBalance Sheet:")
    print("─" * 50)
    for item, value in data.get('balance_sheet', {}).items():
        print(f"{item.ljust(30)} {value.rjust(18)}")
    
    if data.get('source') == "mock":
        print("\nNote: These values are mock data based on Tesla's actual financials.")
        print("In production, these values would be extracted from the filing content.")

def save_financial_data(data: Dict[str, Any], current_dir: Path) -> str:
    """Save financial data to a JSON file and return the path."""
    output_file = current_dir / "tesla_financial_data.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    return str(output_file)
