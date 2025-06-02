import plotly.express as px
import pandas as pd
import numpy as np

df = pd.read_csv("executed-trades.csv")
df['Date'] = pd.to_datetime(df['Date'])

########################################################################################

# Standardize the dataset's trades to assume a consistent $50 position sizing
# Stop loss ($) = ( $ per position opened * Risk per trade[1%] * Number of positions ) / percent of total capital invested
# Stop loss (%) = Stop loss ($) / $ per position opened

# e.g.: ($50 * 0.01 * 10) / 1 = $5 that is, is Stop loss
# e.g.: $5 / 50 = 0.1 that is, 10% stop loss per position

########################################################################################

# Initialize new columns
df['Standardized_Multiplier'] = np.nan
df['Standardized_Trade'] = np.nan

# Identify initial action rows and calculate multiplier
initial_action_mask = df['Action'].isin(['Initial Buy', 'Initial Short'])
df.loc[initial_action_mask, 'Standardized_Multiplier'] = 50 / df.loc[initial_action_mask, 'Price']

# Propagate Standardized_Multiplier within each Ticker group
# Sort by Ticker and then by an implicit order (like original index or a date if available and sorted)
# to ensure ffill works correctly if there are multiple initial buys for the same ticker later on.
# For this specific dataset, groupby().ffill() is sufficient.
df['Standardized_Multiplier'] = df.groupby('Ticker')['Standardized_Multiplier'].ffill()

df_sorted = df.sort_values(by=['Ticker', 'Date'])
# print("\nDataFrame after calculating and forward-filling Standardized_Multiplier:")
# print(df_sorted)
# print("-" * 30)

# Calculate Standardized_Trade
for index, row in df.iterrows():
    if pd.isna(row['Standardized_Multiplier']):
        # This case should not happen if every Ticker has an initial action
        # and ffill worked correctly.
        df.loc[index, 'Standardized_Trade'] = np.nan
        continue

    base_standardized_value = row['Standardized_Multiplier'] * row['Price']

    if row['Action'] in ['Initial Buy', 'Initial Short']:
        df.loc[index, 'Standardized_Trade'] = base_standardized_value # This should be ~50
    else:
        share_factor = np.nan # Default to NaN if Shares_Traded is unexpected
        if row['Shares_Traded'] == 1:
            share_factor = 1/3  # Use 1/3 for better precision than 0.3333
        elif row['Shares_Traded'] == 2:
            share_factor = 2/3  # Use 2/3 for better precision than 0.6666
        elif row['Shares_Traded'] == 3:
            share_factor = 1.0

        if pd.notna(share_factor):
            df.loc[index, 'Standardized_Trade'] = base_standardized_value * share_factor
        else:
            # Handle unexpected Shares_Traded for non-initial actions if necessary
            df.loc[index, 'Standardized_Trade'] = np.nan

# Add Month column to dataset
month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

df['Month'] = pd.to_datetime(df['Date']).dt.month
df['Month'] = df['Month'].map(month_names)


# Apply a positive or negative sign to Standardized_Trade based on Action type
# If we buy we lose money (negative), if we sell we make money (positive)
buy_actions = ['Initial Buy', 'PT1 Buy', 'PT2 Buy', 'PT3 Buy', 'Stop-Loss Buy']
sell_actions = ['Initial Short', 'PT1 Sell', 'PT2 Sell', 'PT3 Sell', 'Stop-Loss Sell']


df['Standardized_Trade'] = df.apply(
    lambda row: row['Standardized_Trade'] * (-1 if row['Action'] in buy_actions else 1 if row['Action'] in sell_actions else row['Standardized_Trade']),
    axis=1
)


print("\nFinal Updated DataFrame:")
print(df)
df.to_csv("standardized-executed-trades.csv", index=False)
