"""
SIMULATION MODULE: This module simulates financial data extraction.

NOTE: This currently uses predefined mock data rather than actual parsing 
of EDGAR filing contents. The mock data is based on Tesla's actual financials
for demonstration purposes.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

async def simulate_financial_data(client, filing: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate financial data extraction from SEC filings.
    
    This function simulates the extraction of all three primary financial statements:
    1. Income Statement
    2. Balance Sheet
    3. Cash Flow Statement
    
    Args:
        client: The client used to access the filing content
        filing: Information about the filing to extract data from
        
    Returns:
        Dictionary containing simulated financial data for all statements
    """
    print("\n===== Financial Data Simulation =====\n")
    
    try:
        print(f"🔍 Analyzing {filing['form_type']} filing for {filing['company']}...")
        
        # For real implementation, we would parse HTML content
        if not filing.get('mock', False) and not (hasattr(client, 'mock_mode') and client.mock_mode):
            try:
                content = await client.get_page_content()
                print(f"📄 Retrieved {len(content)} bytes of filing content")
                print("🔍 Contents would be parsed in a real implementation...")
            except Exception as e:
                print(f"⚠️ Could not retrieve content: {e}")
                print("📄 Using mock financial data...")
        else:
            print("📄 Using mock financial data...")
            
        print("🔍 Simulating extraction of financial statements...")
        
        # Get mock data for all three financial statements
        income_statement = get_tesla_income_statement_mock()
        balance_sheet = get_tesla_balance_sheet_mock()
        cash_flow = get_tesla_cash_flow_mock()
        
        # Format results
        results = {
            "company": filing["company"],
            "ticker": filing["ticker"],
            "period_end": filing["period_end"],
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow_statement": cash_flow,
            "source": "mock" if filing.get('mock', False) else "simulated"
        }
        
        print("✅ Successfully prepared financial data for all statements")
        return results
    except Exception as e:
        print(f"❌ Error simulating financial data: {e}")
        return {
            "company": filing["company"],
            "error": str(e),
            "source": "error"
        }

def get_tesla_income_statement_mock():
    """Get mock income statement data for Tesla."""
    return {
        "Revenue": "$81,462,000,000",
        "Cost of Revenue": "$63,493,000,000",
        "Gross Profit": "$17,969,000,000", 
        "Operating Income": "$13,656,000,000",
        "Research and Development": "$3,075,000,000",
        "Selling, General & Administrative": "$4,984,000,000",
        "Net Income": "$12,556,000,000",
        "Earnings Per Share (Basic)": "$3.99",
        "Earnings Per Share (Diluted)": "$3.62"
    }

def get_tesla_balance_sheet_mock():
    """Get mock balance sheet data for Tesla."""
    return {
        "Cash and Cash Equivalents": "$22,185,000,000",
        "Accounts Receivable": "$2,583,000,000",
        "Inventory": "$12,842,000,000",
        "Total Current Assets": "$41,230,000,000",
        "Property, Plant and Equipment": "$28,558,000,000",
        "Total Assets": "$82,338,000,000",
        "Accounts Payable": "$11,113,000,000",
        "Total Current Liabilities": "$18,138,000,000",
        "Long-term Debt": "$2,102,000,000",
        "Total Liabilities": "$29,262,000,000",
        "Total Equity": "$53,076,000,000"
    }

def get_tesla_cash_flow_mock():
    """Get mock cash flow statement data for Tesla."""
    return {
        "Net Income": "$12,556,000,000",
        "Depreciation and Amortization": "$5,084,000,000",
        "Changes in Working Capital": "$(3,138,000,000)",
        "Net Cash Provided by Operating Activities": "$14,724,000,000",
        "Capital Expenditures": "$(7,163,000,000)",
        "Net Cash Used in Investing Activities": "$(6,336,000,000)",
        "Net Cash Used in Financing Activities": "$(475,000,000)",
        "Net Change in Cash": "$7,913,000,000"
    }
