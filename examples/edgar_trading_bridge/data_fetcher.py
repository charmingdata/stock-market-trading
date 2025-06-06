"""
Financial data retrieval module for the SEC EDGAR trading bridge.

This module handles fetching financial data from SEC EDGAR, either through
the actual API or using mock data for testing.
"""

import logging
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Add the project root to the sys.path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

from src.edgar.client.client import EdgarClient
from src.edgar.models import EdgarSearchCriteria, SecFiling, FinancialStatementItems

logger = logging.getLogger(__name__)

async def simulate_financial_data(client: EdgarClient, company: Dict[str, str], year: int) -> Optional[FinancialStatementItems]:
    """
    Generate mock financial data for testing.
    
    Args:
        client: EdgarClient instance (not used but kept for signature compatibility)
        company: Company info dictionary
        year: Year for the financial data
        
    Returns:
        Simulated FinancialStatementItems or None if simulation fails
    """
    print("\n===== Financial Data Simulation =====\n")
    
    try:
        import random
        
        # Generate random but realistic financial data
        revenue = random.uniform(1000000000, 100000000000)
        op_margin = random.uniform(0.05, 0.3)
        net_margin = op_margin * random.uniform(0.5, 0.9)
        operating_income = revenue * op_margin
        net_income = revenue * net_margin
        eps = net_income / random.uniform(500000000, 5000000000)
        cash = random.uniform(5000000000, 50000000000)
        
        # Format as strings that match SEC filing format
        revenue_str = f"{int(revenue):,d}"
        operating_income_str = f"{int(operating_income):,d}"
        net_income_str = f"{int(net_income):,d}"
        eps_basic_str = f"{eps:.2f}"
        eps_diluted_str = f"{eps * 0.98:.2f}"
        cash_str = f"{int(cash):,d}"
        
        # Create a simulated filing
        return FinancialStatementItems(
            cik=company["cik"],
            company_name=company["name"],
            form_type="10-K",
            filing_date=datetime.now(),
            document_url=f"https://www.sec.gov/mock/{company['symbol']}",
            fiscal_year=year,
            fiscal_quarter=None,
            revenue=revenue_str,
            operating_income=operating_income_str,
            net_income=net_income_str,
            eps_basic=eps_basic_str,
            eps_diluted=eps_diluted_str,
            cash_and_equivalents=cash_str
        )
    except Exception as e:
        print(f"❌ Error simulating financial data: {e}")
        return None

async def fetch_company_financial_data(
    client: EdgarClient,
    company: Dict[str, str],
    year: int,
    mock_mode: bool = False
) -> List[FinancialStatementItems]:
    """
    Fetch quarterly and annual financial data for a company for a specific year.
    
    Args:
        client: Configured EdgarClient
        company: Company info dictionary with cik, name, symbol
        year: Year to fetch data for
        mock_mode: Whether to use mock data
        
    Returns:
        List of FinancialStatementItems objects with quarterly and annual data
    """
    results = []
    cik = company["cik"]
    name = company["name"]
    
    try:
        if mock_mode:
            # In mock mode, generate mock financial data
            financial_data = await simulate_financial_data(client, company, year)
            if financial_data:
                results.append(financial_data)
                
                # Generate a few quarterly reports too for more complete testing
                quarters = ["Q1", "Q2", "Q3"]
                for q in quarters:
                    # Clone the annual data but adjust for quarterly
                    q_data = await simulate_financial_data(client, company, year)
                    if q_data:
                        # Modify for quarterly data
                        q_data.form_type = "10-Q"
                        q_data.fiscal_quarter = q
                        # Adjust values (quarterly typically lower)
                        q_data.revenue = str(int(int(q_data.revenue.replace(',', '')) * 0.25))
                        q_data.operating_income = str(int(int(q_data.operating_income.replace(',', '')) * 0.25))
                        q_data.net_income = str(int(int(q_data.net_income.replace(',', '')) * 0.25))
                        results.append(q_data)
        else:
            # Fetch annual report (10-K)
            logger.info(f"Fetching annual report (10-K) for {name} ({year})")
            annual_search = EdgarSearchCriteria.for_fiscal_period(
                cik=cik,
                year=year
            )
            annual_data = await annual_search.get_financial_data()
            if annual_data:
                results.append(annual_data)
            
            # Fetch quarterly reports (10-Q)
            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                logger.info(f"Fetching {quarter} report for {name} ({year})")
                quarterly_search = EdgarSearchCriteria.for_fiscal_period(
                    cik=cik,
                    year=year,
                    quarter=quarter
                )
                quarterly_data = await quarterly_search.get_financial_data()
                if quarterly_data:
                    results.append(quarterly_data)
    
    except Exception as e:
        logger.error(f"Error fetching data for {name}: {e}", exc_info=True)
    
    # Let the user know what we found
    if results:
        logger.info(f"Found {len(results)} financial statements for {name} ({company['symbol']})")
    else:
        logger.warning(f"No financial data found for {name} ({company['symbol']})")
    
    return results