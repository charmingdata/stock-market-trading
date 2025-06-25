from dash import Dash, dcc, html, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

order_months={'Month': ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']}

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dcc.Markdown("# Stock Market Trading Dashboard"),
    dbc.Row([
        dbc.Col(dbc.Button("Past Ticker Prices", id="historical-pricing", color="primary", className="mb-3"), width=3),
        dbc.Col(dbc.Button("Most Recent Ticker Prices", id="recent-pricing", color="primary", className="mb-3"), width=3)
    ], justify="center"),
    dbc.Alert(id="alert-pricing", duration=5000, is_open=False),
    dbc.Row([
        dbc.Col([
            dbc.Stack(
                [
                    dbc.Label("Timeframe to open new position (business days)"),
                    dbc.Input(type="number", min=1, max=10, step=1, value=2, id="business-days")
                ]
            )], width=4),
        dbc.Col([
            dbc.Stack(
                [
                    dbc.Label("Position size (USD)"),
                    dbc.Input(type="number", min=50, max=1000, step=50, value=500, id="position-size")
                ]
            )], width=2),
        dbc.Col([
            dbc.Stack(
                [
                    dbc.Label("Ticker setup month"),
                    dcc.Dropdown(options=["All"]+order_months['Month'], value='All',
                                 clearable=False, id="ticker-setup-month")
                ]
            )], width=2),
        dbc.Col([
            dbc.Stack(
                [
                    dbc.Label(" "),
                    dbc.Button("Simulate Trading", id="simulate-trading", color="success")
                ], gap=4
            )], width=2),
    ]),
    dbc.Row([
    ], id='cards-row', justify="center", className="my-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="profit_n_loss"), width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                id="position-type",
                options=["All", "Long", "Short"],
                value="All",
                inline=True
            ),
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="trades-open"), width=6),
        dbc.Col(dcc.Graph(id="open-by-action"), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="trades-closed"), width=6),
        dbc.Col(dcc.Graph(id="closed-by-action"), width=6)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="table-space"), width=12),
    ]),
    dcc.Store(id="store-sim-trades")
])


# Get historical prices for all tickers in setup ticker data from April 1, which is when we started the setup data
@callback(
    Output("alert-pricing", "children"),
    Output("alert-pricing", "is_open"),
    Input("historical-pricing", "n_clicks"),
    running=[(Output("historical-pricing", "disabled"), True, False)],
    prevent_initial_call=True
)
def get_past_ticker_prices(_):
    ticker_df = pd.read_csv('trading-setups.csv')

    # Calculate dates from April 1 which is when the trading setup list started
    end_date = datetime.now()
    end_str = end_date.strftime('%Y-%m-%d')
    start_str = '2025-04-01'

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

    # Optionally save to CSV
    all_data.to_csv('ticker-prices.csv', index=False)

    return f"Saved historical ticker prices to ticker-prices.csv", True


# Get most recent prices for all tickers
@callback(
    Output("alert-pricing", "children", allow_duplicate=True),
    Output("alert-pricing", "is_open", allow_duplicate=True),
    Input("recent-pricing", "n_clicks"),
    running=[(Output("recent-pricing", "disabled"), True, False)],
    prevent_initial_call=True
)
def get_most_recent_ticker_prices(_):
    # Get unique tickers
    ticker_df = pd.read_csv('trading-setups.csv')
    unique_tickers = ticker_df['ticker'].unique()
    # unique_tickers = ['ABM','MCD']

    # Find most recent business day and next normal day for extraction range
    most_recent_bday = pd.bdate_range(end=pd.Timestamp.today(), periods=1)[0]
    next_day = most_recent_bday + pd.Timedelta(days=1)

    # Loop through the tickers and fetch data
    all_data = pd.DataFrame()
    for ticker in unique_tickers:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(start=most_recent_bday, end=next_day)

        # Add a column to identify the ticker
        stock_data['Ticker'] = ticker

        # Append to the combined DataFrame
        all_data = pd.concat([all_data, stock_data])

    # Reset index to make Date a column and maintain the ticker association
    all_data = all_data.reset_index()
    all_data.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits', 'Capital Gains'], axis=1, inplace=True)
    all_data.to_csv('ticker-prices-today.csv', index=False)

    return f"Saved most recent ticker prices to ticker-prices-today.csv", True


##### ----------------------------------------------------------------------------------------------------------- #####
#####                                     Simulate Trades                                                         #####
##### ----------------------------------------------------------------------------------------------------------- #####

@callback(
    Output("table-space", "children"),
    Output("store-sim-trades", "data"),
    Input("simulate-trading", "n_clicks"),
    State("business-days", "value"),
    State("ticker-setup-month", "value"),
    State("position-size", "value"),
    running=[(Output("simulate-trading", "disabled"), True, False)],
    prevent_initial_call=False
)
def trading_simulation(_, business_days, setup_month, position_size):
    # --- 1. Data Preparation ---

    # Trade Setup Data
    trade_setup_df = pd.read_csv('trading-setups.csv')

    # Convert date columns in setup_df to datetime.date objects
    trade_setup_df['e_report'] = pd.to_datetime(trade_setup_df['e_report'], format='%m/%d/%Y', errors='coerce').dt.date
    trade_setup_df['observation'] = pd.to_datetime(trade_setup_df['observation'], format='%m/%d/%Y').dt.date

    # Filter setup dates by month
    trade_setup_df['month_name'] = pd.to_datetime(trade_setup_df['observation']).dt.strftime('%B')
    if setup_month == "All":
        # Keep trade_setup_df as is and drop month_name column
        trade_setup_df.drop(columns='month_name', inplace=True)
    else:
        trade_setup_df = trade_setup_df[trade_setup_df['month_name'] == setup_month]
        trade_setup_df.drop(columns='month_name', inplace=True)
        trade_setup_df = trade_setup_df.reset_index(drop=True)
    # print(trade_setup_df)

    # convert numerical columns to floats
    numeric_cols_setup = ['enter_from', 'enter_to', 'stoploss', 'pt1', 'pt2', 'pt3']
    for col in numeric_cols_setup:
        trade_setup_df[col] = pd.to_numeric(trade_setup_df[col], errors='coerce')

    # Ticker Prices Data
    ticker_prices_df = pd.read_csv('ticker-prices.csv')

    ticker_prices_df['Date'] = pd.to_datetime(ticker_prices_df['Date']).dt.date
    numeric_cols_prices = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols_prices:
        ticker_prices_df[col] = pd.to_numeric(ticker_prices_df[col])
    ticker_prices_df.sort_values(by=['Date', 'Ticker'], inplace=True)

    # --- 2. Initialization for Trading Logic ---
    executed_trades_log = []
    open_positions = {}

    # --- 3. Core Trading Logic ---
    unique_dates = sorted(ticker_prices_df['Date'].unique())

    for current_date in unique_dates:
        # Stores tickers closed on the current_date so we don't initiate a new position with same ticker on the same day it closed
        closed_today_tickers = set()
        daily_prices_for_date = ticker_prices_df[ticker_prices_df['Date'] == current_date]

        # --- Part 1: Manage existing open positions ---
        tickers_with_open_positions = list(open_positions.keys())  # Iterate over a copy
        for ticker in tickers_with_open_positions:
            # Check if position was closed by a previous iteration because stoploss was met or PT3 was reached
            if ticker not in open_positions:
                continue

            position_details = open_positions[ticker]
            setup_row = trade_setup_df.iloc[position_details['setup_index']]

            ticker_price_data_today = daily_prices_for_date[daily_prices_for_date['Ticker'] == ticker]
            if ticker_price_data_today.empty:
                continue

            current_high_price = ticker_price_data_today['High'].iloc[0]
            current_low_price = ticker_price_data_today['Low'].iloc[0]

            pos_trade_type = position_details['trade_type']
            pos_shares_open = position_details['shares_open']

            # Get the current stop-loss for this position
            current_dynamic_stoploss = position_details['current_stoploss']

            stop_loss_triggered_today = False

            # Stop-Loss Check
            if pos_trade_type == 'short': # and not position_details['pt1_reached']:
                if current_high_price >= current_dynamic_stoploss:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'Stop-Loss Buy',
                        'Price': current_dynamic_stoploss,
                        'Shares_Traded': pos_shares_open,
                        'Position_Shares_Remaining_After_Trade': 0
                    })
                    del open_positions[ticker]
                    closed_today_tickers.add(ticker)
                    stop_loss_triggered_today = True
                # add condition for closing position if it has been open for over X days
                # elif (current_date - position_details['entry_date']) > 20 business days:
                #     executed_trades_log.append({
                #         'Date': current_date, 'Ticker': ticker, 'Action': 'Stop-Loss Buy',
                #         'Price': ticker_price_data_today['Close'].iloc[0],
                #         'Shares_Traded': pos_shares_open,
                #         'Position_Shares_Remaining_After_Trade': 0
                #     })
                #     del open_positions[ticker]
                #     closed_today_tickers.add(ticker)
                #     stop_loss_triggered_today = True

            elif pos_trade_type == 'buy':
                if current_low_price <= current_dynamic_stoploss:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'Stop-Loss Sell',
                        'Price': current_dynamic_stoploss,
                        'Shares_Traded': pos_shares_open,
                        'Position_Shares_Remaining_After_Trade': 0
                    })
                    del open_positions[ticker]
                    closed_today_tickers.add(ticker)
                    stop_loss_triggered_today = True

            if stop_loss_triggered_today:
                continue

            # Profit-Taking Checks
            if pos_trade_type == 'short':
                if not position_details['pt1_reached'] and pos_shares_open == 3 and current_low_price <= setup_row['pt1']:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'PT1 Buy',
                        'Price': setup_row['pt1'], 'Shares_Traded': 1,
                        'Position_Shares_Remaining_After_Trade': 2
                    })
                    position_details['shares_open'] = 2
                    position_details['pt1_reached'] = True
                    position_details['current_stoploss'] = position_details['initial_entry_price']
                    pos_shares_open = 2  # Update for next check within same day
                if not position_details['pt2_reached'] and pos_shares_open == 2 and current_low_price <= setup_row['pt2']:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'PT2 Buy',
                        'Price': setup_row['pt2'], 'Shares_Traded': 1,
                        'Position_Shares_Remaining_After_Trade': 1
                    })
                    position_details['shares_open'] = 1
                    position_details['pt2_reached'] = True
                    position_details['current_stoploss'] = setup_row['pt1']
                    pos_shares_open = 1  # Update for next check
                if not position_details['pt3_reached'] and pos_shares_open == 1 and current_low_price <= setup_row['pt3']:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'PT3 Buy',
                        'Price': setup_row['pt3'], 'Shares_Traded': 1,
                        'Position_Shares_Remaining_After_Trade': 0
                    })
                    del open_positions[ticker]
                    closed_today_tickers.add(ticker)
            elif pos_trade_type == 'buy':
                if not position_details['pt1_reached'] and pos_shares_open == 3 and current_high_price >= setup_row['pt1']:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'PT1 Sell',
                        'Price': setup_row['pt1'], 'Shares_Traded': 1,
                        'Position_Shares_Remaining_After_Trade': 2
                    })
                    position_details['shares_open'] = 2
                    position_details['pt1_reached'] = True
                    position_details['current_stoploss'] = position_details['initial_entry_price']
                    pos_shares_open = 2
                if not position_details['pt2_reached'] and pos_shares_open == 2 and current_high_price >= setup_row['pt2']:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'PT2 Sell',
                        'Price': setup_row['pt2'], 'Shares_Traded': 1,
                        'Position_Shares_Remaining_After_Trade': 1
                    })
                    position_details['shares_open'] = 1
                    position_details['pt2_reached'] = True
                    position_details['current_stoploss'] = setup_row['pt1']
                    pos_shares_open = 1
                if not position_details['pt3_reached'] and pos_shares_open == 1 and current_high_price >= setup_row['pt3']:
                    executed_trades_log.append({
                        'Date': current_date, 'Ticker': ticker, 'Action': 'PT3 Sell',
                        'Price': setup_row['pt3'], 'Shares_Traded': 1,
                        'Position_Shares_Remaining_After_Trade': 0
                    })
                    del open_positions[ticker]
                    closed_today_tickers.add(ticker)

        # --- Part 2: Check for new trade entries ---
        for idx, setup_row in trade_setup_df.iterrows():
            ticker = setup_row['ticker']

            # If ticker was closed today, do not re-open on the same day.
            if ticker in closed_today_tickers:
                continue

            if ticker in open_positions:  # If still open (e.g. from previous day, or PT1/PT2 hit but not closed)
                continue

            if current_date < setup_row['observation']:  # current date is before observation setup date, skip
                continue

            # New position entry trade must be within 2 business days since observation date
            observation_timestamp = pd.Timestamp(setup_row['observation'])
            current_timestamp = pd.Timestamp(current_date)

            num_business_days_since_observation = 0
            # Only calculate if current_date is strictly after or equal to observation_date
            if current_timestamp > observation_timestamp:
                # Calculate the next business day strictly after the observation_timestamp
                start_count_timestamp = observation_timestamp + pd.offsets.BDay()  # Default is 1 BDay offset

                # Ensure start_count_timestamp is not after current_timestamp before creating range
                if start_count_timestamp <= current_timestamp:
                    # The pd.bdate_range function generates a DatetimeIndex containing a sequence of business dates
                    num_business_days_since_observation = len(
                        pd.bdate_range(start=start_count_timestamp,
                                       end=current_timestamp))

            if num_business_days_since_observation > business_days:
                continue  # Skip if more than x business days have passed since observation

            ticker_price_data_today = daily_prices_for_date[daily_prices_for_date['Ticker'] == ticker]
            if ticker_price_data_today.empty:
                continue

            current_close_price = ticker_price_data_today['Close'].iloc[0]

            trade_can_be_initiated = False
            actual_entry_price = 0.0  # This will be the close price if trade is initiated
            initial_action_type = ""

            if setup_row['trade'] == 'buy':
                entry_low_bound = setup_row['enter_from']
                entry_high_bound = setup_row['enter_to']
                # Check if Close price is within the entry range for buy
                if entry_low_bound <= current_close_price <= entry_high_bound:
                    actual_entry_price = current_close_price  # Entry price is the Close price because I only open positions at end of day
                    trade_can_be_initiated = True
                    initial_action_type = "Initial Buy"

            elif setup_row['trade'] == 'short':
                entry_low_bound = setup_row['enter_to']  # for short, 'to' is the lower numerical value
                entry_high_bound = setup_row['enter_from']  # for short, 'from' is the higher numerical value
                # Check if Close price is within the entry range for short
                if entry_low_bound <= current_close_price <= entry_high_bound:
                    actual_entry_price = current_close_price  # Entry price is the Close price
                    trade_can_be_initiated = True
                    initial_action_type = "Initial Short"

            if trade_can_be_initiated:
                executed_trades_log.append({
                    'Date': current_date, 'Ticker': ticker, 'Action': initial_action_type,
                    'Price': actual_entry_price,
                    'Shares_Traded': 3,
                    'Position_Shares_Remaining_After_Trade': 3
                })
                open_positions[ticker] = {
                    'setup_index': idx,
                    'trade_type': setup_row['trade'],
                    'shares_open': 3,
                    'pt1_reached': False, 'pt2_reached': False, 'pt3_reached': False,
                    'initial_entry_price': actual_entry_price,
                    'current_stoploss': setup_row['stoploss']
                }

    # --- 4. Final Output ---
    executed_trades_df = pd.DataFrame(executed_trades_log)
    if not executed_trades_df.empty:
        executed_trades_df = executed_trades_df[[
            'Date', 'Ticker', 'Action', 'Price',
            'Shares_Traded', 'Position_Shares_Remaining_After_Trade'
        ]]
        executed_trades_df.sort_values(by=['Date', 'Ticker'], inplace=True)
        executed_trades_df.reset_index(drop=True, inplace=True)

    #####------------------------------------------------------------------------------------------------------#####
    #####-----------------------------------          Standardize Trades       --------------------------------#####
    #####------------------------------------------------------------------------------------------------------#####

    executed_trades_df['Standardized_Multiplier'] = np.nan
    executed_trades_df['Standardized_Trade'] = np.nan

    # Identify initial action rows and calculate multiplier ($500 position sizing)
    initial_action_mask = executed_trades_df['Action'].isin(['Initial Buy', 'Initial Short'])
    executed_trades_df.loc[initial_action_mask, 'Standardized_Multiplier'] = position_size / executed_trades_df.loc[initial_action_mask, 'Price']

    executed_trades_df['Standardized_Multiplier'] = executed_trades_df.groupby('Ticker')['Standardized_Multiplier'].ffill()

    # Calculate Standardized_Trade
    for index, row in executed_trades_df.iterrows():
        if pd.isna(row['Standardized_Multiplier']):
            # This case should not happen if every Ticker has an initial action
            # and ffill worked correctly.
            executed_trades_df.loc[index, 'Standardized_Trade'] = np.nan
            continue

        base_standardized_value = row['Standardized_Multiplier'] * row['Price']

        if row['Action'] in ['Initial Buy', 'Initial Short']:
            executed_trades_df.loc[index, 'Standardized_Trade'] = base_standardized_value
        else:
            share_factor = np.nan  # Default to NaN if Shares_Traded is unexpected
            if row['Shares_Traded'] == 1:
                share_factor = 1 / 3  # Use 1/3 for better precision than 0.3333
            elif row['Shares_Traded'] == 2:
                share_factor = 2 / 3  # Use 2/3 for better precision than 0.6666
            elif row['Shares_Traded'] == 3:
                share_factor = 1.0

            if pd.notna(share_factor):
                executed_trades_df.loc[index, 'Standardized_Trade'] = base_standardized_value * share_factor
            else:
                # Handle unexpected Shares_Traded for non-initial actions if necessary
                executed_trades_df.loc[index, 'Standardized_Trade'] = np.nan

    # Add Month column to dataset
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    executed_trades_df['Month'] = pd.to_datetime(executed_trades_df['Date']).dt.month
    executed_trades_df['Month'] = executed_trades_df['Month'].map(month_names)

    # Apply a positive or negative sign to Standardized_Trade based on Action type
    # If we buy we lose money (negative), if we sell we make money (positive)
    buy_actions = ['Initial Buy', 'PT1 Buy', 'PT2 Buy', 'PT3 Buy', 'Stop-Loss Buy']
    sell_actions = ['Initial Short', 'PT1 Sell', 'PT2 Sell', 'PT3 Sell', 'Stop-Loss Sell']

    executed_trades_df['Standardized_Trade'] = executed_trades_df.apply(
        lambda row: row['Standardized_Trade'] * (
            -1 if row['Action'] in buy_actions else 1 if row['Action'] in sell_actions else row['Standardized_Trade']),
        axis=1
    )

    print("\nFinal Updated DataFrame:")
    print(executed_trades_df.head())
    executed_trades_df.to_csv("standardized-executed-trades.csv", index=False)

    grid = dag.AgGrid(
        rowData=executed_trades_df.to_dict("records"),
        columnDefs=[{"field": i, 'filter': True, 'sortable': True} for i in executed_trades_df.columns],
        dashGridOptions={"pagination": True},
        columnSize="sizeToFit"
    )

    return grid, executed_trades_df.to_dict('records')


##### ----------------------------------------------------------------------------------------------------------- #####
#####                                     Build Visualizations                                                    #####
##### ----------------------------------------------------------------------------------------------------------- #####

@callback(
    Output("trades-open", "figure"),
    Output("open-by-action", "figure"),
    Output("trades-closed", "figure"),
    Output("closed-by-action", "figure"),
    Output("profit_n_loss", "figure"),
    Output("cards-row", "children"),
    Input("store-sim-trades", "data"),
    Input("position-type", "value"),
    State("position-size", "value"),
)
def build_graphs(stored_data, position_type, position_size):
    if stored_data is None:
        return no_update
    df = pd.DataFrame(stored_data) # df = pd.read_csv("standardized-executed-trades.csv")
    positions_opened = df[(df['Action'] == 'Initial Buy') | (df['Action'] == 'Initial Short')]

    # Trades per month
    trades_count = positions_opened.groupby('Month').size().reset_index(name='Trade Count')
    fig_trades_month = px.bar(trades_count, x='Month', y='Trade Count', title='Positions Opened by Month',
                              category_orders=order_months)
    # Trades by month and trade type
    trades_count = positions_opened.groupby(['Month', 'Action']).size().reset_index(name='Trade Count')
    fig_trades_action = px.histogram(trades_count, x='Month', y='Trade Count', color='Action',
                                     barmode='group', title='Positions Opened by Month AND Trade',
                                     category_orders=order_months)


    closed_trades_df = df[df['Position_Shares_Remaining_After_Trade'] == 0]

    # Closed positions by month
    closed_trades_count = closed_trades_df.groupby('Month').size().reset_index(name='Trade Count')
    fig_closed = px.bar(closed_trades_count, x='Month', y='Trade Count', title='Positions Closed by Month',
                        category_orders=order_months)

    # Closed positions by month and trade type
    trades_count_action = closed_trades_df.groupby(['Month', 'Action']).size().reset_index(name='Trade Count')
    fig_closed_trades_action = px.histogram(trades_count_action, x='Month', y='Trade Count', color='Action',
                                            barmode='group', title='Positions Closed by Trade',
                                            category_orders=order_months)

    #####------------------------------------------------------------------------------------------------------#####
    #####---------------------------------     Profit & Loss Summary         ----------------------------------#####
    #####------------------------------------------------------------------------------------------------------#####

    if position_type == 'Long':
        position_chosen_df = df[df['Action'] == 'Initial Buy']
    elif position_type == 'Short':
        position_chosen_df = df[df['Action'] == 'Initial Short']
    else:
        position_chosen_df = df[(df['Action'] == 'Initial Buy') | (df['Action'] == 'Initial Short')]

    current_prices_df = pd.read_csv('ticker-prices-today.csv')
    current_prices_df['Date'] = pd.to_datetime(current_prices_df['Date']).dt.date

    # Convert the DataFrame to a Series for fast lookups. Ticker becomes the index.
    price_lookup_series = current_prices_df.set_index('Ticker')['Close']

    # List of closed positions (tickers) - does not account for duplicate tickers that might have been closed at different times
    closed_trades_tickers = position_chosen_df[position_chosen_df['Position_Shares_Remaining_After_Trade'] == 0]['Ticker'].unique()

    pnl_summary = []

    # Group by ticker to analyze each position
    for ticker, group in df.groupby('Ticker'):
        group = group.sort_values(by='Date')  # Ensure chronological order

        # Identify the initial transaction(s) to get the basis
        if position_type == 'Long':
            initial_trades = group[group['Action'].str.contains('Initial Buy')]
        elif position_type == 'Short':
            initial_trades = group[group['Action'].str.contains('Initial Short')]
        else:
            initial_trades = group[group['Action'].str.contains('Initial')]

        if initial_trades.empty:
            print(f"Warning: No 'Initial' trade found for {ticker}. Skipping.")
            continue

        # Calculate the average standardized entry price per share
        total_initial_shares = initial_trades['Shares_Traded'].sum()
        total_initial_std_value = initial_trades['Standardized_Trade'].sum()
        avg_entry_std_price_per_share = total_initial_std_value / total_initial_shares

        # Identify if the initial position was long or short
        is_short = 'Short' in initial_trades.iloc[0]['Action']

        # --- Calculate Realized P&L ---
        realized_pnl = 0
        closing_trades = group[~group['Action'].str.contains('Initial')]

        for _, row in closing_trades.iterrows():
            shares_closed = row['Shares_Traded']
            exit_std_price_per_share = abs(row['Standardized_Trade']) / shares_closed

            if is_short:  # Profit = entry - exit
                pnl_per_share = avg_entry_std_price_per_share - exit_std_price_per_share
            else:  # Profit = exit - entry
                pnl_per_share = exit_std_price_per_share + avg_entry_std_price_per_share
            realized_pnl += pnl_per_share * shares_closed

        # --- Calculate Unrealized P&L ---
        unrealized_pnl = 0
        shares_remaining = group.iloc[-1]['Position_Shares_Remaining_After_Trade']

        if shares_remaining > 0:
            current_market_price = price_lookup_series.get(ticker)
            if current_market_price is None:
                print(f"Warning: No current price for open position '{ticker}'. Unrealized P&L is 0.")
            else:
                # Get the anchor price from the first initial trade
                initial_anchor_price = initial_trades.iloc[0]['Price']

                if is_short:
                    current_std_price_per_share = (current_market_price / initial_anchor_price) * avg_entry_std_price_per_share
                    unrealized_pnl_per_share = avg_entry_std_price_per_share - current_std_price_per_share
                    unrealized_pnl = unrealized_pnl_per_share * shares_remaining
                else:
                    current_std_price_per_share = (current_market_price / initial_anchor_price) * avg_entry_std_price_per_share
                    unrealized_pnl_per_share = current_std_price_per_share - avg_entry_std_price_per_share
                    unrealized_pnl = unrealized_pnl_per_share * -shares_remaining

        # --- Store results ---
        pnl_summary.append({
            'Ticker': ticker,
            'Status': 'Open' if shares_remaining > 0 else 'Closed',
            'Shares Open': shares_remaining,
            'Realized P&L($)': realized_pnl,
            'Unrealized P&L($)': unrealized_pnl,
            'Total P&L($)': realized_pnl + unrealized_pnl
        })

    # Final Reporting ---
    summary_df = pd.DataFrame(pnl_summary)
    total_realized_pnl = summary_df['Realized P&L($)'].sum()
    total_unrealized_pnl = summary_df['Unrealized P&L($)'].sum()
    total_pnl = summary_df['Total P&L($)'].sum()

    total_capital_deployed = len(position_chosen_df) * position_size

    # print("--- P&L Breakdown by Ticker (Standardized $) ---")
    # print(summary_df.round(6))
    # print("\n" + "=" * 40)
    # print("Portfolio P&L Summary (Standardized $)")
    # print("=" * 40)
    # print(f"Total Realized P&L:   ${total_realized_pnl:,.4f}")
    # print(f"Total Unrealized P&L: ${total_unrealized_pnl:,.4f}")
    # print("----------------------------------------")
    # print(f"Total Net P&L($)      ${total_pnl:,.4f}")
    # print("----------------------------------------")
    # print(f"Total Net P&L(%):    {(total_pnl / total_capital_deployed) * 100:.2f}%")
    # print("=" * 40)

    c_cap_deplyd = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Capital Deployed", className="card-title"),
                    html.Hr(),
                    html.P(f"${total_capital_deployed}", className="card-text"),
                ]
            ),
        ],
    )
    c_unrlzd_prft = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Unrealized P&L", className="card-title"),
                    html.Hr(),
                    html.P(f"${total_unrealized_pnl:.2f}", className="card-text"),
                ]
            ),
        ],
    )
    c_rlzd_prft = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Realized P&L", className="card-title"),
                    html.Hr(),
                    html.P(f"${total_realized_pnl:.2f}", className="card-text"),
                ]
            ),
        ],
    )
    c_proft_dlr = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Total Net P&L", className="card-title"),
                    html.Hr(),
                    html.P(f"${total_pnl:.2f}", className="card-text"),
                ]
            ),
        ],
    )
    c_proft_pct = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Total Net P&L (%)", className="card-title"),
                    html.Hr(),
                    html.P(f"{(total_pnl / total_capital_deployed) * 100:.2f}%", className="card-text"),
                ]
            ),
        ],
    )

    cards = [
        dbc.Col(c_cap_deplyd, width=2),
        dbc.Col(c_unrlzd_prft, width=2),
        dbc.Col(c_rlzd_prft, width=2),
        dbc.Col(c_proft_dlr, width=2),
        dbc.Col(c_proft_pct, width=2),
    ]


    fig_pnl = px.bar(summary_df, x='Ticker', y=['Realized P&L($)', 'Unrealized P&L($)'])
    fig_pnl.update_layout(margin=dict(l=20, r=20, t=20, b=20))

    return fig_trades_month, fig_trades_action, fig_closed, fig_closed_trades_action, fig_pnl, cards



if __name__ == '__main__':
    app.run(debug=True)
