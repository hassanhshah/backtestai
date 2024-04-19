import streamlit as st
from ..utils.session_utils import SessionUtils

class PortfolioBuilder:
    def __init__(self, portfolio_manager, ai_manager):
        self.portfolio_manager = portfolio_manager
        self.ai_manager = ai_manager

    def display(self):
        tab1, tab2 = st.tabs(["Manual Portfolio Builder", "AI Portfolio Builder"])
        with tab1:
            self.manual_portfolio_builder()
        
        with tab2:
            self.ai_portfolio_builder()

    def reset_manual_portfolio(self):
        st.session_state["manual_portfolio_name"] = ""
        st.session_state["manual_portfolio_description"] = ""
        st.session_state["manual_number_of_stocks"] = 1

    def manual_portfolio_builder(self):
        if "manual_portfolio_name" not in st.session_state:
            st.session_state["manual_portfolio_name"] = ""
        if "manual_portfolio_description" not in st.session_state:
            st.session_state["manual_portfolio_description"] = ""
        if "manual_number_of_stocks" not in st.session_state:
            st.session_state["manual_number_of_stocks"] = 1
    
        portfolio_name = st.text_input("Portfolio name:", key="manual_portfolio_name")
        portfolio_description = st.text_area("Portfolio description:", key="manual_portfolio_description",
                                             help="Describe the contents of your portfolio. This field is optional.")
        number_of_stocks = st.slider('How many stocks would you like to include in your portfolio?', min_value=1, 
                                     max_value=50, value=1, step=1, key="manual_number_of_stocks")
        stocks = []
        rows_needed = -(-number_of_stocks // 5)

        for row in range(rows_needed):
            cols = st.columns(5)
            for i in range(5):
                index = row * 5 + i
                if index < number_of_stocks:
                    help_text = "Enter the ticker symbol, e.g., 'GOOG' for Alphabet Inc." if index == 0 else None
                    stock_symbol = cols[i].text_input(f'Ticker #{index+1}', key=f'stock_{index+1}_manual', help=help_text)
                    if stock_symbol:
                        stocks.append(stock_symbol.strip())

        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button("Create Portfolio", key="create_manual_portfolio"):
                list_stocks = [stock.strip() for stock in stocks if stock.strip()]
                if portfolio_name and list_stocks:
                    creation_success, creation_message = self.portfolio_manager.add_portfolio(portfolio_name, portfolio_description)
                    if creation_success:
                        st.success(creation_message)
                        # Attempt to add each stock to the newly created portfolio
                        for stock in list_stocks:
                            success, message = self.portfolio_manager.add_stock_to_portfolio(portfolio_name, stock)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                    else:
                        st.error("Failed to create the portfolio.")
                else:
                    st.error("Please enter a valid portfolio name and at least one valid stock.")

        with col2:
            if st.button("Reset", key="reset_manual_portfolio", on_click=self.reset_manual_portfolio):
                pass

    def reset_ai_portfolio(self):
        st.session_state.user_request = ""
        st.session_state.portfolio_generated = False
        st.session_state.portfolio_displayed = False
        st.session_state.save_toggle = False
        st.session_state.portfolio_saved = False

    def ai_portfolio_builder(self):
        if 'user_request' not in st.session_state:
            st.session_state["user_request"] = ""

        user_request = st.text_area(
            "What kind of portfolio are you looking to construct?",
            help="Example: 'I want a portfolio focusing on renewable energy companies expected to grow in the next year.'",
            key="user_request"
        )

        col1, col2 = st.columns([5, 1])
        with col1:
            generate_button = st.button("Generate AI Portfolio", key="generate_portfolio")
            if generate_button:
                with st.spinner('Generating AI portfolio... Please wait.'):
                    ai_response = self.ai_manager.create_ai_portfolio(user_request)
                    success, parsed_data = self.ai_manager.parse_ai_response(ai_response)
                    if success:
                        st.session_state.parsed_data = parsed_data
                        st.session_state.portfolio_generated = True
                        st.success('AI portfolio generated successfully.')
                    else:
                        st.error("Failed to generate AI portfolio. Please reset and try again.")
                        st.session_state.portfolio_generated = False
        
        with col2:
            if st.button("Reset", key="reset_ai_portfolio", on_click=self.reset_ai_portfolio):
                pass

        if 'portfolio_generated' in st.session_state and st.session_state.portfolio_generated:
            parsed_data = st.session_state.parsed_data
            portfolio_name = f"Portfolio Name: {parsed_data['portfolio_name']}"
            stocks = f"Stocks: {', '.join(parsed_data['stock_symbols'])}"
            description = f"Description: {parsed_data['description']}"

            st.info("AI Portfolio Recommendation:")
            if 'portfolio_displayed' not in st.session_state:
                st.write_stream(self.ai_manager.ai_stream(portfolio_name))
                st.write_stream(self.ai_manager.ai_stream(stocks))
                st.write_stream(self.ai_manager.ai_stream(description))
                st.session_state.portfolio_displayed = True
            else:
                st.write(portfolio_name)
                st.write(stocks)
                st.write(description)
            
            st.session_state.save_toggle = False
            st.session_state.save_toggle = st.checkbox('Save Portfolio', value=st.session_state.save_toggle, key='save_portfolio_toggle')
            if st.session_state.save_toggle:
                if 'portfolio_saved' not in st.session_state or not st.session_state.portfolio_saved:
                    creation_success, creation_message = self.portfolio_manager.add_portfolio(parsed_data['portfolio_name'], parsed_data['description'])
                    if creation_success:
                        st.success(f"AI-generated portfolio '{parsed_data['portfolio_name']}' saved successfully.")
                        for stock in parsed_data['stock_symbols']:
                            success, message = self.portfolio_manager.add_stock_to_portfolio(parsed_data['portfolio_name'], stock)
                            if success:
                                st.success(f"Added stock {stock} to '{parsed_data['portfolio_name']}' portfolio.")
                            else:
                                st.error(f"Failed to add stock {stock} to '{parsed_data['portfolio_name']}' portfolio: {message}")
                        st.session_state.portfolio_saved = True 
                    else:
                        st.error(f"Failed to save the portfolio '{parsed_data['portfolio_name']}': {creation_message}")
                        st.session_state.portfolio_saved = False
