from dash import Dash, html, dcc, callback, Output, Input, no_update
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate

import plotly.express as px
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


ticker_df = pd.read_csv('trading-data.csv')

##### ---------------------------------------------------------------------------------------- #####
#####                          Get Ticker Prices                                               #####
##### ---------------------------------------------------------------------------------------- #####

# Calculate dates (60 days ago from today)
end_date = datetime.now()
end_str = end_date.strftime('%Y-%m-%d')
start_str = '2025-04-01'
# start_date = end_date - timedelta(days=60)

# Create an empty DataFrame to store all data
all_data = pd.DataFrame()

# Get unique tickers
ticker_df.dropna(subset=['ticker'], inplace=True)  # Drop rows where 'ticker' is NaN
unique_tickers = ticker_df['ticker'].unique()

# Loop through the tickers and fetch data
for ticker in unique_tickers:
    # Fetch data
    stock = yf.Ticker(ticker)
    stock_data = stock.history(start=start_str, end=end_str)

    # Add a column to identify the ticker
    stock_data['Ticker'] = ticker

    # Append to the combined DataFrame
    all_data = pd.concat([all_data, stock_data])

# Reset index to make Date a column and maintain the ticker association
all_data = all_data.reset_index()
all_data.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)

# Print sample of the data
print(f"Stock prices from {start_str} to {end_str}:")
print(all_data.head())

# Optionally save to CSV
all_data.to_csv('ticker-prices.csv', index=False)
print("Data saved to multiple_stocks.csv")
exit()


##### ---------------------------------------------------------------------------------------- #####
#####                          Simulate Trades                                                 #####
##### ---------------------------------------------------------------------------------------- #####

# def simulate_trades():
#     # --- 1. Data Preparation ---
#
#     # Trade Setup Data
#     trade_setup_df = pd.read_csv('trading-data.csv')
#
#     # Convert date columns in setup_df to datetime.date objects
#     trade_setup_df['observation'] = pd.to_datetime(trade_setup_df['observation'], format='%m/%d/%Y').dt.date
#     trade_setup_df['e_report'] = pd.to_datetime(trade_setup_df['e_report'], format='%m/%d/%Y', errors='coerce').dt.date
#
#     numeric_cols_setup = ['enter_from', 'enter_to', 'stoploss', 'pt1', 'pt2', 'pt3', 'pt4']
#     for col in numeric_cols_setup:
#         trade_setup_df[col] = pd.to_numeric(trade_setup_df[col], errors='coerce')
#
#     # Ticker Prices Data
#     ticker_prices_df = pd.read_csv('ticker-prices.csv')
#
#     ticker_prices_df['Date'] = pd.to_datetime(ticker_prices_df['Date']).dt.date
#     numeric_cols_prices = ['Open', 'High', 'Low', 'Close', 'Volume']
#     for col in numeric_cols_prices:
#         ticker_prices_df[col] = pd.to_numeric(ticker_prices_df[col])
#     ticker_prices_df.sort_values(by=['Date', 'Ticker'], inplace=True)
#
#     # --- 2. Initialization for Trading Logic ---
#     executed_trades_log = []
#     open_positions = {}
#
#     # --- 3. Core Trading Logic ---
#     unique_dates = sorted(ticker_prices_df['Date'].unique())
#
#     for current_date in unique_dates:
#         # Stores tickers closed on the current_date so we don't initiate a new position with same ticker on the same day
#         closed_today_tickers = set()
#         daily_prices_for_date = ticker_prices_df[ticker_prices_df['Date'] == current_date]
#
#         # --- Part 1: Manage existing open positions ---
#         tickers_with_open_positions = list(open_positions.keys())  # Iterate over a copy
#         for ticker in tickers_with_open_positions:
#             # Check if position was closed by a previous iteration because stoploss was met or PT3 was reached
#             if ticker not in open_positions:
#                 continue
#
#             position_details = open_positions[ticker]
#             setup_row = trade_setup_df.iloc[position_details['setup_index']]
#
#             ticker_price_data_today = daily_prices_for_date[daily_prices_for_date['Ticker'] == ticker]
#             if ticker_price_data_today.empty:
#                 continue
#
#             current_high_price = ticker_price_data_today['High'].iloc[0]
#             current_low_price = ticker_price_data_today['Low'].iloc[0]
#
#             pos_trade_type = position_details['trade_type']
#             pos_shares_open = position_details['shares_open']
#
#             stop_loss_triggered_today = False
#             # Stop-Loss Check
#             if pos_trade_type == 'short':
#                 if current_high_price >= setup_row['stoploss']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'Stop-Loss Buy',
#                         'Price': setup_row['stoploss'],
#                         'Shares_Traded': pos_shares_open,
#                         'Position_Shares_Remaining_After_Trade': 0
#                     })
#                     del open_positions[ticker]
#                     closed_today_tickers.add(ticker)
#                     stop_loss_triggered_today = True
#             elif pos_trade_type == 'buy':
#                 if current_low_price <= setup_row['stoploss']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'Stop-Loss Sell',
#                         'Price': setup_row['stoploss'],
#                         'Shares_Traded': pos_shares_open,
#                         'Position_Shares_Remaining_After_Trade': 0
#                     })
#                     del open_positions[ticker]
#                     closed_today_tickers.add(ticker)
#                     stop_loss_triggered_today = True
#
#             if stop_loss_triggered_today:
#                 continue
#
#             # Profit-Taking Checks
#             if pos_trade_type == 'short':
#                 if not position_details['pt1_reached'] and pos_shares_open == 3 and current_low_price <= setup_row['pt1']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'PT1 Buy',
#                         'Price': setup_row['pt1'], 'Shares_Traded': 1,
#                         'Position_Shares_Remaining_After_Trade': 2
#                     })
#                     position_details['shares_open'] = 2
#                     position_details['pt1_reached'] = True
#                     pos_shares_open = 2  # Update for next check within same day
#                 if not position_details['pt2_reached'] and pos_shares_open == 2 and current_low_price <= setup_row['pt2']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'PT2 Buy',
#                         'Price': setup_row['pt2'], 'Shares_Traded': 1,
#                         'Position_Shares_Remaining_After_Trade': 1
#                     })
#                     position_details['shares_open'] = 1
#                     position_details['pt2_reached'] = True
#                     pos_shares_open = 1  # Update for next check
#                 if not position_details['pt3_reached'] and pos_shares_open == 1 and current_low_price <= setup_row['pt3']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'PT3 Buy',
#                         'Price': setup_row['pt3'], 'Shares_Traded': 1,
#                         'Position_Shares_Remaining_After_Trade': 0
#                     })
#                     del open_positions[ticker]
#                     closed_today_tickers.add(ticker)
#             elif pos_trade_type == 'buy':
#                 if not position_details['pt1_reached'] and pos_shares_open == 3 and current_high_price >= setup_row['pt1']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'PT1 Sell',
#                         'Price': setup_row['pt1'], 'Shares_Traded': 1,
#                         'Position_Shares_Remaining_After_Trade': 2
#                     })
#                     position_details['shares_open'] = 2
#                     position_details['pt1_reached'] = True
#                     pos_shares_open = 2
#                 if not position_details['pt2_reached'] and pos_shares_open == 2 and current_high_price >= setup_row['pt2']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'PT2 Sell',
#                         'Price': setup_row['pt2'], 'Shares_Traded': 1,
#                         'Position_Shares_Remaining_After_Trade': 1
#                     })
#                     position_details['shares_open'] = 1
#                     position_details['pt2_reached'] = True
#                     pos_shares_open = 1
#                 if not position_details['pt3_reached'] and pos_shares_open == 1 and current_high_price >= setup_row['pt3']:
#                     executed_trades_log.append({
#                         'Date': current_date, 'Ticker': ticker, 'Action': 'PT3 Sell',
#                         'Price': setup_row['pt3'], 'Shares_Traded': 1,
#                         'Position_Shares_Remaining_After_Trade': 0
#                     })
#                     del open_positions[ticker]
#                     closed_today_tickers.add(ticker)
#
#         # --- Part 2: Check for new trade entries ---
#         for idx, setup_row in trade_setup_df.iterrows():
#             ticker = setup_row['ticker']
#
#             # If ticker was closed today, do not re-open on the same day.
#             if ticker in closed_today_tickers:
#                 continue
#
#             if ticker in open_positions:  # If still open (e.g. from previous day, or PT1/PT2 hit but not closed)
#                 continue
#
#             if current_date <= setup_row['observation']:
#                 continue
#
#             # Trade must be within 5 business days since observation date
#             observation_timestamp = pd.Timestamp(setup_row['observation'])
#             current_timestamp = pd.Timestamp(current_date)
#
#             num_business_days_since_observation = 0
#             # Only calculate if current_date is strictly after observation_date
#             if current_timestamp > observation_timestamp:
#                 # Calculate the next business day strictly after the observation_timestamp
#                 start_count_timestamp = observation_timestamp + pd.offsets.BDay()  # Default is 1 BDay offset
#
#                 # Ensure start_count_timestamp is not after current_timestamp before creating range
#                 if start_count_timestamp <= current_timestamp:
#                     # The pd.bdate_range function generates a DatetimeIndex containing a sequence of business dates
#                     num_business_days_since_observation = len(
#                         pd.bdate_range(start=start_count_timestamp,
#                                        end=current_timestamp))
#
#             if num_business_days_since_observation > 5:
#                 continue  # ADDED: Skip if more than 5 business days have passed since observation
#
#             ticker_price_data_today = daily_prices_for_date[daily_prices_for_date['Ticker'] == ticker]
#             if ticker_price_data_today.empty:
#                 continue
#
#             current_close_price = ticker_price_data_today['Close'].iloc[0]
#
#             trade_can_be_initiated = False
#             actual_entry_price = 0.0  # This will be the close price if trade is initiated
#             initial_action_type = ""
#
#             if setup_row['trade'] == 'buy':
#                 entry_low_bound = setup_row['enter_from']
#                 entry_high_bound = setup_row['enter_to']
#                 # Check if Close price is within the entry range for buy
#                 if entry_low_bound <= current_close_price <= entry_high_bound:
#                     actual_entry_price = current_close_price  # Entry price is the Close price because I only open positions at end of day
#                     trade_can_be_initiated = True
#                     initial_action_type = "Initial Buy"
#
#             elif setup_row['trade'] == 'short':
#                 entry_low_bound = setup_row['enter_to']  # for short, 'to' is the lower numerical value
#                 entry_high_bound = setup_row['enter_from']  # for short, 'from' is the higher numerical value
#                 # Check if Close price is within the entry range for short
#                 if entry_low_bound <= current_close_price <= entry_high_bound:
#                     actual_entry_price = current_close_price  # Entry price is the Close price
#                     trade_can_be_initiated = True
#                     initial_action_type = "Initial Short"
#
#             if trade_can_be_initiated:
#                 executed_trades_log.append({
#                     'Date': current_date, 'Ticker': ticker, 'Action': initial_action_type,
#                     'Price': actual_entry_price,
#                     'Shares_Traded': 3,
#                     'Position_Shares_Remaining_After_Trade': 3
#                 })
#                 open_positions[ticker] = {
#                     'setup_index': idx,
#                     'trade_type': setup_row['trade'],
#                     'shares_open': 3,
#                     'pt1_reached': False, 'pt2_reached': False, 'pt3_reached': False,
#                     'entry_price': actual_entry_price
#                 }
#
#     # --- 4. Final Output ---
#     executed_trades_df = pd.DataFrame(executed_trades_log)
#     if not executed_trades_df.empty:
#         executed_trades_df = executed_trades_df[[
#             'Date', 'Ticker', 'Action', 'Price',
#             'Shares_Traded', 'Position_Shares_Remaining_After_Trade'
#         ]]
#         executed_trades_df.sort_values(by=['Date', 'Ticker'], inplace=True)
#         executed_trades_df.reset_index(drop=True, inplace=True)
#
#     return executed_trades_df
#
#
# if __name__ == '__main__':
#     trades_df = simulate_trades()
#     trades_df.to_csv("executed-trades.csv", index=False)
