import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output

# --- 1. Load and preprocess the data ---

df = pd.read_csv("standardized-executed-trades.csv")
df['Date'] = pd.to_datetime(df['Date'])
df_full = df.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)

# --- 2. Function to generate final_outcomes_df for a given month ---

def analyze_month(selected_month):
    month_trades = df[df['Month'] == selected_month].copy()
    target_actions = ['Initial Buy', 'Initial Short']
    filtered_actions = month_trades[month_trades['Action'].isin(target_actions)]
    action_counts = filtered_actions.groupby(['Ticker', 'Action']).size()
    result_df = action_counts.unstack(fill_value=0)
    if 'Initial Buy' not in result_df.columns:
        result_df['Initial Buy'] = 0
    if 'Initial Short' not in result_df.columns:
        result_df['Initial Short'] = 0
    result_df = result_df[['Initial Buy', 'Initial Short']]
    tickers_from_original_result_df = result_df.reset_index()['Ticker'].unique()
    initial_positions_to_analyze = df_full[
        (df_full['Month'] == selected_month) &
        (df_full['Action'].isin(['Initial Buy', 'Initial Short'])) &
        (df_full['Ticker'].isin(tickers_from_original_result_df))
    ].copy()
    outcome_details_list = []
    for _, initial_trade_row in initial_positions_to_analyze.iterrows():
        current_ticker = initial_trade_row['Ticker']
        initial_action_type = initial_trade_row['Action']
        initial_trade_original_index = initial_trade_row.name
        subsequent_trades_for_ticker_all = df_full[
            (df_full['Ticker'] == current_ticker) &
            (df_full.index > initial_trade_original_index)
        ]
        next_opening_trade_df_index = -1
        for idx_in_df_full, trade in subsequent_trades_for_ticker_all.iterrows():
            if trade['Action'] in ['Initial Buy', 'Initial Short']:
                next_opening_trade_df_index = idx_in_df_full
                break
        if next_opening_trade_df_index != -1:
            relevant_subsequent_trades = subsequent_trades_for_ticker_all[
                subsequent_trades_for_ticker_all.index < next_opening_trade_df_index
            ]
        else:
            relevant_subsequent_trades = subsequent_trades_for_ticker_all
        actions_list = relevant_subsequent_trades['Action'].tolist()
        outcome = 'unknown'
        outcome_dollar = 0
        if initial_action_type == 'Initial Buy':
            if len(actions_list) >= 1:
                action1 = actions_list[0]
                if action1 == 'Stop-Loss Sell':
                    outcome = 'failed'
                    outcome_dollar = -27
                elif action1 == 'PT1 Sell':
                    if len(actions_list) == 2:
                        action2 = actions_list[1]
                        if action2 == 'Stop-Loss Sell':
                            outcome = 'succeeded'
                            outcome_dollar = 13
                        elif action2 == 'PT2 Sell':
                            outcome = 'succeeded'
                            outcome_dollar = 36
                    elif len(actions_list) == 3:
                        action3 = actions_list[2]
                        if action3 == 'Stop-Loss Sell':
                            outcome = 'succeeded'
                            outcome_dollar = 49
                        elif action3 == 'PT3 Sell':
                            outcome = 'succeeded'
                            outcome_dollar = 74
                    else:
                        outcome = 'succeeded'
                        outcome_dollar = 13
        elif initial_action_type == 'Initial Short':
            if len(actions_list) >= 1:
                action1 = actions_list[0]
                if action1 == 'Stop-Loss Buy':
                    outcome = 'failed'
                    outcome_dollar = -27
                elif action1 == 'PT1 Buy':
                    if len(actions_list) == 2:
                        action2 = actions_list[1]
                        if action2 == 'Stop-Loss Buy':
                            outcome = 'succeeded'
                            outcome_dollar = 13
                        elif action2 == 'PT2 Buy':
                            outcome = 'succeeded'
                            outcome_dollar = 36
                    elif len(actions_list) == 3:
                        action3 = actions_list[2]
                        if action3 == 'Stop-Loss Buy':
                            outcome = 'succeeded'
                            outcome_dollar = 49
                        elif action3 == 'PT3 Buy':
                            outcome = 'succeeded'
                            outcome_dollar = 74
                    else:
                        outcome = 'succeeded'
                        outcome_dollar = 13
        outcome_details_list.append({
            'Date_of_Initial_Action': initial_trade_row['Date'],
            'Ticker': initial_trade_row['Ticker'],
            'Initial_Action_Type': initial_action_type,
            'Initial_Price': initial_trade_row['Price'],
            'Outcome': outcome,
            'Outcome_dollar': outcome_dollar
        })
    final_outcomes_df = pd.DataFrame(outcome_details_list)
    return final_outcomes_df

# --- 3. Dash app setup ---

app = Dash()
available_months = df['Month'].unique()
default_month = available_months[0] if len(available_months) > 0 else None

# Custom color palette for outcomes and types
outcome_colors = {
    'succeeded': '#2ecc71',  # green
    'failed': '#e74c3c',     # red
    'unknown': '#95a5a6'     # gray
}
type_colors = {
    'Initial Buy': '#3498db',    # blue
    'Initial Short': '#f39c12'   # orange
}

app.layout = html.Div([
    html.H1("Position Outcome Analysis by Month", style={'textAlign': 'center', 'color': '#222'}),
    html.Div([
        html.Label("Select Month:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': m, 'value': m} for m in available_months],
            value=default_month,
            clearable=False,
            style={'width': '200px'}
        ),
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginBottom': 20}),
    html.Div([
        dcc.Graph(id='pie-chart', style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='bar-chart', style={'display': 'inline-block', 'width': '48%'})
    ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'space-between'}),
    dcc.Graph(id='long-short-chart', style={'marginTop': 30}),
    html.H2("Detailed Position Outcomes", style={'marginTop': 40, 'textAlign': 'center'}),
    dash_table.DataTable(
        id='details-table',
        columns=[
            {"name": "Date", "id": "Date_of_Initial_Action"},
            {"name": "Ticker", "id": "Ticker"},
            {"name": "Type", "id": "Initial_Action_Type"},
            {"name": "Price", "id": "Initial_Price"},
            {"name": "Outcome", "id": "Outcome"},
            {"name": "P&L ($)", "id": "Outcome_dollar"},
        ],
        page_size=10,
        style_table={'overflowX': 'auto', 'margin': 'auto', 'maxWidth': '900px'},
        style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial'},
        style_header={
            'backgroundColor': '#e3e6ea',
            'fontWeight': 'bold',
            'fontSize': 16
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            },
            {
                'if': {'column_id': 'Outcome', 'filter_query': '{Outcome} = "succeeded"'},
                'color': outcome_colors['succeeded'],
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'Outcome', 'filter_query': '{Outcome} = "failed"'},
                'color': outcome_colors['failed'],
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'Outcome', 'filter_query': '{Outcome} = "unknown"'},
                'color': outcome_colors['unknown'],
                'fontWeight': 'bold'
            },
        ],
    )
], style={'backgroundColor': '#f4f6fb', 'minHeight': '100vh', 'paddingBottom': 40})

# --- 4. Callbacks for interactivity ---

@app.callback(
    [
        Output('pie-chart', 'figure'),
        Output('bar-chart', 'figure'),
        Output('long-short-chart', 'figure'),
        Output('details-table', 'data')
    ],
    [Input('month-dropdown', 'value')]
)
def update_dashboard(selected_month):
    if not selected_month:
        return dash.no_update, dash.no_update, dash.no_update, []
    final_outcomes_df = analyze_month(selected_month)
    # Pie chart
    fig_pie = px.pie(
        final_outcomes_df,
        names='Outcome',
        title=f'{selected_month} Initial Positions Outcomes',
        color='Outcome',
        color_discrete_map=outcome_colors,
        hole=0.4
    )
    fig_pie.update_traces(textinfo='percent+label', pull=[0.05, 0.05, 0.05])
    fig_pie.update_layout(
        paper_bgcolor='#f4f6fb',
        plot_bgcolor='#f4f6fb',
        font=dict(family='Arial', size=15)
    )
    # Bar chart: Outcome P&L
    fig_bar = px.bar(
        final_outcomes_df.groupby('Outcome')['Outcome_dollar'].sum().reset_index(),
        x='Outcome',
        y='Outcome_dollar',
        color='Outcome',
        title=f'Total P&L by Outcome ({selected_month})',
        color_discrete_map=outcome_colors
    )
    fig_bar.update_layout(
        paper_bgcolor='#f4f6fb',
        plot_bgcolor='#f4f6fb',
        font=dict(family='Arial', size=15)
    )
    # Bar chart: Long vs Short
    fig_long_short = px.bar(
        final_outcomes_df.groupby('Initial_Action_Type')['Outcome_dollar'].sum().reset_index(),
        x='Initial_Action_Type',
        y='Outcome_dollar',
        color='Initial_Action_Type',
        title=f'Total P&L: Long vs Short ({selected_month})',
        color_discrete_map=type_colors
    )
    fig_long_short.update_layout(
        paper_bgcolor='#f4f6fb',
        plot_bgcolor='#f4f6fb',
        font=dict(family='Arial', size=15)
    )
    # Table data
    table_data = final_outcomes_df.to_dict('records')
    return fig_pie, fig_bar, fig_long_short, table_data

if __name__ == '__main__':
    app.run(port=8000)