"""
Data processing module for the SEC EDGAR trading bridge.

This module handles transforming financial statement data into formats suitable
for trading analysis and strategy application.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional

from src.edgar.models import FinancialStatementItems

from .project_helper import COMPANY_WATCHLIST

logger = logging.getLogger(__name__)

def financial_metrics_to_df(financial_data: List[FinancialStatementItems]) -> pd.DataFrame:
    """
    Convert financial statement items to a pandas DataFrame.
    
    Args:
        financial_data: List of FinancialStatementItems
        
    Returns:
        DataFrame with financial metrics
    """
    records = []
    
    for item in financial_data:
        try:
            # Convert string values to numeric
            revenue = float(item.revenue.replace(',', ''))
            operating_income = float(item.operating_income.replace(',', ''))
            net_income = float(item.net_income.replace(',', ''))
            eps_basic = float(item.eps_basic)
            eps_diluted = float(item.eps_diluted)
            cash = float(item.cash_and_equivalents.replace(',', ''))
            
            # Calculate some derived metrics
            operating_margin = operating_income / revenue if revenue else 0
            net_margin = net_income / revenue if revenue else 0
            
            records.append({
                'symbol': next((c['symbol'] for c in COMPANY_WATCHLIST 
                              if c['cik'] == item.cik), None),
                'company_name': item.company_name,
                'cik': item.cik,
                'form_type': item.form_type,
                'fiscal_year': item.fiscal_year,
                'fiscal_quarter': item.fiscal_quarter,
                'period': item.fiscal_period_display,
                'filing_date': item.filing_date,
                'revenue': revenue,
                'operating_income': operating_income,
                'net_income': net_income,
                'eps_basic': eps_basic,
                'eps_diluted': eps_diluted,
                'cash': cash,
                'operating_margin': operating_margin,
                'net_margin': net_margin
            })
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error processing financial data: {e}")
    
    return pd.DataFrame(records)

# Add to data_processor.py

def save_financial_data_csv(financial_df: pd.DataFrame, output_path: str = "financial_statements.csv") -> None:
    """Save financial data with additional metadata for debugging."""
    # Add extraction timestamp
    financial_df['extraction_time'] = datetime.now().isoformat()
    
    # Add data quality indicators
    financial_df['data_quality'] = financial_df.apply(
        lambda row: 'mock' if abs(float(row['revenue'])) < 1001 else 'extracted', 
        axis=1
    )
    
    # Save with more detailed headers
    with open(output_path, 'w') as f:
        f.write("# SEC EDGAR Financial Statement Extract\n")
        f.write(f"# Generated: {datetime.now()}\n")
        f.write(f"# Companies: {', '.join(financial_df['symbol'].unique())}\n")
        f.write(f"# Years: {', '.join(map(str, financial_df['fiscal_year'].unique()))}\n\n")
    
    financial_df.to_csv(output_path, mode='a', index=False)
    
    print(f"Financial data saved to {output_path}")
