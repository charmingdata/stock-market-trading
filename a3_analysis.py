import plotly.express as px
import pandas as pd
import numpy as np


df = pd.read_csv("standardized-executed-trades.csv")

########################################################################################

# Graph: Opened positions by month and trade type

########################################################################################

# potisions_opened = df[(df['Action'] == 'Initial Buy') | (df['Action'] == 'Initial Short')]

# # Trades per month
# trades_count = potisions_opened.groupby('Month').size().reset_index(name='Trade Count')
# fig_trades_month = px.bar(trades_count, x='Month', y='Trade Count', title='Total Opened Positions per Month')
# fig_trades_month.show()

# # Trades by month and trade type
# trades_count = potisions_opened.groupby(['Month', 'Action']).size().reset_index(name='Trade Count')
# fig_trades_action = px.histogram(trades_count, x='Month', y='Trade Count', color='Action',
#                                  barmode='group', title='Total Opened Positions per Month and Trade Type')
# fig_trades_action.show()
# exit()

########################################################################################

# Graph: closed positions by month and trade type

########################################################################################

# closed_trades_df = df[df['Position_Shares_Remaining_After_Trade'] == 0]

# # Closed positions by month
# closed_trades_count = closed_trades_df.groupby('Month').size().reset_index(name='Trade Count')
# fig_closed = px.bar(closed_trades_count, x='Month', y='Trade Count', title='Total Closed Positions per Month')
# fig_closed.show()

# # Closed positions by month and trade type
# trades_count_action = closed_trades_df.groupby(['Month', 'Action']).size().reset_index(name='Trade Count')
# fig_closed_trades_action = px.histogram(trades_count_action, x='Month', y='Trade Count', color='Action',
#                                         barmode='group', title='Total Closed Positions per Month and Trade Type')
# fig_closed_trades_action.show()
# exit()

########################################################################################

# Profit and Loss - All positions

########################################################################################

# print(f"Profit and Loss - All positions: ${df['Standardized_Trade'].sum()}")
# trades = df.groupby('Month')['Standardized_Trade'].sum().reset_index(name='PL')
# print("Profit and Loss by Month:")
# print(trades)
#
# buy_actions = ['Initial Buy', 'PT1 Buy', 'PT2 Buy', 'PT3 Buy', 'Stop-Loss Buy']
# # sell_actions = ['Initial Short', 'PT1 Sell', 'PT2 Sell', 'PT3 Sell', 'Stop-Loss Sell']
#
# # Total Capital Deployed: absolute sum of all values of Standardized_Trade where Action is in buy_actions
# april_df = df[df['Month'] == 'April']
# april_PL_buy = april_df[april_df['Action'].isin(buy_actions)]['Standardized_Trade'].abs().sum()
# print(f"Total Capital Deployed - April: ${april_PL_buy}")
# print(f"Profit and Loss - April: {round(trades[trades['Month'] == 'April']['PL'][0]/april_PL_buy, 2)*100}%")
# print("---"*30)
# exit()


# may_df = df[df['Month'] == 'May']
# may_PL_buy = may_df[may_df['Action'].isin(buy_actions)]['Standardized_Trade'].abs().sum()
# print(f"Total Capital Deployed - May: ${may_PL_buy}")
# print(f"Profit and Loss - May: {round(trades[trades['Month'] == 'May']['PL'][0]/may_PL_buy, 2)*100}%")
# exit()

########################################################################################

# Profit and Loss - Analysis of all positions opened in April

########################################################################################

april_trades = df[df['Month'] == 'April'].copy()

# 2. Filter for 'Initial Buy' and 'Initial Short' actions
target_actions = ['Initial Buy', 'Initial Short']
filtered_actions = april_trades[april_trades['Action'].isin(target_actions)]

# 3. Group by 'Ticker' and 'Action', then count
action_counts = filtered_actions.groupby(['Ticker', 'Action']).size()

# 4. Unstack the result to have 'Initial Buy' and 'Initial Short' as columns
# and fill NaN with 0 for tickers that might not have both actions.
result_df = action_counts.unstack(fill_value=0)

# Ensure both 'Initial Buy' and 'Initial Short' columns exist, even if one type of action didn't occur
if 'Initial Buy' not in result_df.columns:
    result_df['Initial Buy'] = 0
if 'Initial Short' not in result_df.columns:
    result_df['Initial Short'] = 0

# Reorder columns if desired, though unstack usually orders them alphabetically
result_df = result_df[['Initial Buy', 'Initial Short']]
print(f"Total positions opened in April: {result_df['Initial Short'].sum()+result_df['Initial Buy'].sum()}")
print("---"*30)


df['Date'] = pd.to_datetime(df['Date'])
df_full = df.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)

# Tickers that had an 'Initial Buy' or 'Initial Short' in April
tickers_from_original_result_df = result_df.reset_index()['Ticker'].unique()

# Identify the specific initial April positions for *these tickers* from the *complete dataset*
initial_positions_to_analyze = df_full[
    (df_full['Month'] == 'April') &
    (df_full['Action'].isin(['Initial Buy', 'Initial Short'])) &
    (df_full['Ticker'].isin(tickers_from_original_result_df))
].copy() # .copy() to avoid SettingWithCopyWarning

# List to store outcome details for each analyzed position
outcome_details_list = []

# Iterate through each identified initial position
for _, initial_trade_row in initial_positions_to_analyze.iterrows():
    current_ticker = initial_trade_row['Ticker']
    initial_action_type = initial_trade_row['Action']
    # The .name attribute of the row Series in iterrows() gives its index in the DataFrame it came from.
    initial_trade_original_index = initial_trade_row.name

    # Get all trades for the current_ticker that occur *after* this specific initial_trade instance
    subsequent_trades_for_ticker_all  = df_full[
        (df_full['Ticker'] == current_ticker) &
        (df_full.index > initial_trade_original_index) # Ensures we only look at trades after this one
    ]

    # Find the index of the *next* opening trade for this ticker within the subsequent trades
    next_opening_trade_df_index = -1
    for idx_in_df_full, trade in subsequent_trades_for_ticker_all.iterrows():
        if trade['Action'] in ['Initial Buy', 'Initial Short']:
            next_opening_trade_df_index = idx_in_df_full
            break # Found the first one

    # If a subsequent opening trade for the same ticker was found,
    # limit the relevant_subsequent_trades to only those *before* that new opening.
    if next_opening_trade_df_index != -1:
        # Select rows from subsequent_trades_for_ticker_all whose index in df_full is LESS THAN next_opening_trade_df_index
        relevant_subsequent_trades = subsequent_trades_for_ticker_all[subsequent_trades_for_ticker_all.index < next_opening_trade_df_index]
    else:
        relevant_subsequent_trades = subsequent_trades_for_ticker_all
    # --- END OF CRUCIAL NEW LOGIC ---

    actions_list = relevant_subsequent_trades['Action'].tolist()
    # print(actions_list)
    outcome = 'unknown'  # Default outcome
    outcome_dollar = 0

    # assuming an 9% stop loss and 13% PT1, and 23% PT2, and 38% PT3 on $100 trades of 3 shares ($300)
    if initial_action_type == 'Initial Buy':
        if len(actions_list) >= 1: # Check if there's at least one subsequent action ('PT1 Sell' or 'Stop-Loss Sell')
            action1 = actions_list[0]
            if action1 == 'Stop-Loss Sell':  # sold all 3 shares for a loss of 9% = $27
                outcome = 'failed'
                outcome_dollar = -27
            elif action1 == 'PT1 Sell':  # sold 1 share for a profit of 13% = $13
                if len(actions_list) == 2: # Check for a second subsequent action
                    action2 = actions_list[1]
                    if action2 == 'Stop-Loss Sell':  # sold 2 shares at the same original buy price (broke even)
                        outcome = 'succeeded'        # result: 1 share for profit of $13 and two shares for profit of $0
                        outcome_dollar = 13
                    elif action2 == 'PT2 Sell':      # sold the second share for a profit of 23% = $23
                        outcome = 'succeeded'        # result: 1 share for profit of $13 and another share for profit of $23
                        outcome_dollar = 36
                elif len(actions_list) == 3: # Check for a third subsequent action
                    action3 = actions_list[2]
                    if action3 == 'Stop-Loss Sell':  # sold 1 share at $13 and another share at $23, and third share at $13 (trailing stop loss)
                        outcome = 'succeeded'        # result: 13+23+13 = $49
                        outcome_dollar = 49
                    elif action3 == 'PT3 Sell':      # sold the third share for a profit of 38% = $38
                        outcome = 'succeeded'        # result: 13+23+38 = $74
                        outcome_dollar = 74
                else:  # Only PT1 Sell, no further defined action for this position
                    outcome = 'succeeded'
                    outcome_dollar = 13              # we made at least 13$ for having sold 1 share.

        # If no subsequent actions or actions don't match defined patterns, it remains 'unknown'

    elif initial_action_type == 'Initial Short':
        if len(actions_list) >= 1: # Check if there's at least one subsequent action ('PT1 Buy' or 'Stop-Loss Buy')
            action1 = actions_list[0]
            if action1 == 'Stop-Loss Buy':
                outcome = 'failed'
                outcome_dollar = -27
            elif action1 == 'PT1 Buy':
                if len(actions_list) == 2: # Check for a second subsequent action
                    action2 = actions_list[1]
                    if action2 == 'Stop-Loss Buy':
                        outcome = 'succeeded'
                        outcome_dollar = 13
                    elif action2 == 'PT2 Buy':
                        outcome = 'succeeded'
                        outcome_dollar = 36
                elif len(actions_list) == 3: # Check for a third subsequent action
                    action3 = actions_list[2]
                    if action3 == 'Stop-Loss Buy':  # sold 1 share at $13 and another share at $23, and third share at $13 (trailing stop loss)
                        outcome = 'succeeded'       # result: 13+23+13 = $49
                        outcome_dollar = 49
                    elif action3 == 'PT3 Buy':      # sold the third share for a profit of 38% = $38
                        outcome = 'succeeded'        # result: 13+23+38 = $74
                        outcome_dollar = 74
                else:  # Only PT1 Buy, no further defined action for this position
                    outcome = 'succeeded'
                    outcome_dollar = 13
        # If no subsequent actions or actions don't match defined patterns, it remains 'unknown'

    outcome_details_list.append({
        'Date_of_Initial_Action': initial_trade_row['Date'],
        'Ticker': initial_trade_row['Ticker'],
        'Initial_Action_Type': initial_action_type,
        'Initial_Price': initial_trade_row['Price'], # Including price for context
        'Outcome': outcome,
        'Outcome_dollar': outcome_dollar
    })

# Create a DataFrame from the collected outcome details
final_outcomes_df = pd.DataFrame(outcome_details_list)

# Count the occurrences of each outcome
outcome_counts = final_outcomes_df['Outcome'].value_counts()

# Ensure all defined outcome types are present in the counts, even if count is 0
all_possible_outcomes = ['failed', 'succeeded', 'unknown']
outcome_counts = outcome_counts.reindex(all_possible_outcomes, fill_value=0)


print("--- Outcome for Each Initial April Position (for relevant tickers) ---")
print(final_outcomes_df)
print(f"\nNumber of initial positions analyzed: {len(final_outcomes_df)}")
print("\n--- Summary of Outcomes ---")
print(outcome_counts)
print(f"($){final_outcomes_df['Outcome_dollar'].sum()}")

final_outcomes_df_short = final_outcomes_df[final_outcomes_df['Initial_Action_Type']=='Initial Short']
final_outcomes_df_long = final_outcomes_df[final_outcomes_df['Initial_Action_Type']=='Initial Buy']

print(f"Short outcomes: {final_outcomes_df_short['Outcome_dollar'].sum()}")
print(f"Long outcomes: {final_outcomes_df_long['Outcome_dollar'].sum()}")
