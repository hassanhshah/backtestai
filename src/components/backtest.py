import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

class BacktestBuilder:
    def __init__(self, portfolio_manager, backtest_manager):
        self.portfolio_manager = portfolio_manager
        self.backtest_manager = backtest_manager
        self.initial_fund = 0 

    def display(self):
        portfolio_names = self.portfolio_manager.fetch_portfolio_names()  # Fetch portfolio names

        self.initial_fund = st.number_input("Enter initial investment amount:", value=10000.00, format="%.2f", step=100.00)
        if portfolio_names:
            portfolio_name = st.selectbox("Select a portfolio to simulate:", portfolio_names)

            signal_factors = ['Relative Strength Index (RSI)', 'Moving Average Convergence/Divergence (MACD)', 'Bollinger Bands', 'Moving Average',
                            'Daily Return', 'Volatility', 'Exponential Moving Average (EMA)',  'Log Return']
            
            selected_factors = st.multiselect(
            "Select technical indicators to use:", 
            signal_factors, 
            default=signal_factors,
            help="Choose one or more indicators to generate buy and sell actions based on historical data."
            )

            start_date = st.date_input("Start Date", value=pd.to_datetime('2024-01-01').date(), min_value=pd.to_datetime("2020-01-01").date(), max_value=datetime.now().date())
            end_date = st.date_input("End Date", value=datetime.now().date(), min_value=pd.to_datetime("2020-01-01").date(), max_value=datetime.now().date())
            if st.button("Simulate"):
                historical_data_list = self.backtest_manager.get_simulation_data(portfolio_name)

                if not historical_data_list:  # Check if the list is empty
                    st.error("The selected portfolio has no stocks. Please add stocks to the portfolio before simulation.")
                else:
                    results, actions, daily_values_df = self.backtest_manager.simulate_trading(portfolio_name, self.initial_fund, start_date, end_date, selected_factors)

                    # Visualization and metrics display
                    self.display_results(results, actions, daily_values_df)

        else:
            st.write("No portfolios available for simulation.")

    def display_results(self, results, actions, daily_values_df):
        # Visualization using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_values_df.index, y=daily_values_df['Portfolio Value'],
                                 mode='lines',
                                 name='Portfolio Value',
                                 hoverinfo='x+y',
                                 hovertemplate='<b>Date</b>: %{x}<br>' + '<b>Value</b>: $%{y:.2f}<extra></extra>'))
        fig.update_layout(title='Portfolio Value Over Time',
                          xaxis_title='Date',
                          yaxis_title='Portfolio Value',
                          legend_title='Metric')
        st.plotly_chart(fig)

        # Metrics display
        final_portfolio_value_str = results[0].split(": $")[1].replace(',', '')
        final_portfolio_value = float(final_portfolio_value_str)
        delta_value = final_portfolio_value - self.initial_fund
        delta_percentage = (delta_value / self.initial_fund) * 100

        annualized_return = results[1].split(": ")[1]
        sharpe_ratio = results[2].split(": ")[1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Final Portfolio Value", f"${final_portfolio_value:,.2f}", f"{delta_value:+,.2f} ({delta_percentage:+.2f}%)")
        col2.metric("Annualized Return", annualized_return)
        col3.metric("Sharpe Ratio", sharpe_ratio)

        # Displaying actions taken
        with st.container():
            for action in actions:
                st.text(action)