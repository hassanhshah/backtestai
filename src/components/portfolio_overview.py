import streamlit as st
import pandas as pd
import plotly
import plotly.graph_objects as go

class OverviewBuilder:
    def __init__(self, portfolio_manager, backtest_manager):
        self.portfolio_manager = portfolio_manager
        self.backtest_manager = backtest_manager

    def display(self):
        with st.spinner('Waiting for Portfolios to load...'):
            portfolios_info = self.portfolio_manager.fetch_all_portfolios()
            self.portfolio_manager.update_stock_data()
        
        if portfolios_info:
            for portfolio_name, creation_date, stocks, portfolio_description in portfolios_info:
                with st.container():
                    with st.expander(f"{portfolio_name}"):
                        st.write(f"**Creation Date:** {creation_date}")
                        if portfolio_description:  # Check if the description is not empty
                            st.write(f"**Description:** {portfolio_description}")
                        if stocks:
                            st.write(f"**Stocks:** {', '.join(stocks)}")
                            historical_data_list, sim_data = self.backtest_manager.get_simulation_data(portfolio_name)
                            sim_data['transaction_date'] = pd.to_datetime(sim_data['transaction_date'])
                            fig = go.Figure()
                            for stock in stocks:
                                stock_data = sim_data[sim_data['stock_name'] == stock]
                                fig.add_trace(go.Scatter(x=stock_data['transaction_date'], y=stock_data['closing_price'], mode='lines', name=stock))
                            fig.update_layout(title=f'{portfolio_name} - Stock Prices Over Time', xaxis_title='Date', yaxis_title='Price', legend_title='Stock', colorway=plotly.colors.qualitative.D3)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.write("*No stocks in portfolio*")
        else:
            st.write("No portfolios found.")
