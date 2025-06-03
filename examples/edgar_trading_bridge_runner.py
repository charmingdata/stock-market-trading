#!/usr/bin/env python3
"""
SEC EDGAR and Trading Strategy Integration Bridge Runner

This script demonstrates the integration between SEC EDGAR financial data
extraction and the stock market trading strategies developed by the team.

Purpose:
-------
This script serves as a bridge between:
1. The SEC EDGAR data extraction subsystem (src/edgar/*)
2. The trading strategy framework (a1_simulate_trades.py)
3. The trade standardization system (a2_standardize_executed_trades.py)
4. The performance analysis suite (a3_analysis.py)

Features:
--------
- Extract financial metrics from SEC filings (real or simulated)
- Apply trading strategies based on these metrics
- Generate trading signals for further analysis
- Export results to CSV for use with other project components
- Visualize financial metrics and trading performance

Usage:
-----
Run with mock data (for testing):
    python3 examples/edgar_trading_bridge_runner.py

Run with live SEC EDGAR data:
    python3 examples/edgar_trading_bridge_runner.py --live

Output:
------
- Displays a summary of financial metrics and trading signals
- Saves detailed results to financial_trading_analysis.csv
- Prints integration information for team members

See Also:
--------
- edgar_mock_demo_runner.py: For pure SEC EDGAR data extraction testing
- a1_simulate_trades.py: For trading strategy implementation
- a3_analysis.py: For performance analysis

This script is part of the Stock Market Trading project (May 2025).
"""

import sys
import os

# Add the examples directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from edgar_trading_bridge.main import run_cli
    run_cli()