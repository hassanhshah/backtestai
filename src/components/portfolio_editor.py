import streamlit as st

class EditBuilder:
    def __init__(self, portfolio_manager):
        self.portfolio_manager = portfolio_manager

    def display(self):
        stocks_to_add = []
        stocks_to_remove = []
        portfolio_names = self.portfolio_manager.fetch_portfolio_names()  # Fetch portfolio names
        
        if portfolio_names:
            portfolio_name = st.selectbox("Select a portfolio:", portfolio_names)
            action = st.radio("Select operation:", ["Add Stocks", "Remove Stocks", "Delete Portfolio"])

            if action == "Add Stocks":
                number_of_stocks_to_add = st.slider('How many stocks would you like to add?', min_value=1, max_value=50, value=1, step=1)
                rows_needed = -(-number_of_stocks_to_add // 5)  # Ceiling division to determine number of rows

                for row in range(rows_needed):
                    cols = st.columns(5)  # Create 5 columns
                    for i in range(5):
                        index = row * 5 + i
                        if index < number_of_stocks_to_add:
                            help_text = "Enter the ticker symbol, e.g., 'GOOG' for Alphabet Inc." if index == 0 else None
                            stock_symbol = cols[i].text_input(f'Ticker #{index+1}', key=f'add_stock_{index+1}', help=help_text)
                            if stock_symbol:
                                stocks_to_add.append(stock_symbol.strip())

                if st.button("Add Stock(s)"):
                    for stock_symbol in stocks_to_add:
                        success, message = self.portfolio_manager.add_stock_to_portfolio(portfolio_name, stock_symbol)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

            elif action == "Remove Stocks":
                current_stocks = self.portfolio_manager.fetch_all_stocks(portfolio_name)
                stocks_to_remove = st.multiselect('Select stocks to remove:', current_stocks, help="Select the stocks you want to remove from the portfolio.")
                if st.button("Remove Stock(s)"):
                    for stock_symbol in stocks_to_remove:
                        success, message = self.portfolio_manager.remove_stock_from_portfolio(portfolio_name, stock_symbol)
                        if success:
                            st.success(f"Removed {stock_symbol} from {portfolio_name}")
                        else:
                            st.error(message)

            elif action == "Delete Portfolio":
                if st.button(f"Delete {portfolio_name}?"):
                    success, message = self.portfolio_manager.remove_portfolio(portfolio_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        else:
            st.write("No portfolios found.")
