import streamlit as st
from src.config.settings import CUSTOM_STYLES

from src.services.user_service import UserManager
from src.services.portfolio_service import PortfolioManager
from src.services.ai_service import AIManager
from src.services.backtest_service import BacktestManager

from src.components.auth import Auth
from src.components.home_sidebar import HomeSidebar
from src.components.user_sidebar import UserSidebar
from src.components.portfolio_builder import PortfolioBuilder
from src.components.portfolio_overview import OverviewBuilder
from src.components.portfolio_editor import EditBuilder
from src.components.backtest import BacktestBuilder

def main():
    st.markdown(CUSTOM_STYLES, unsafe_allow_html=True)

    user = UserManager()
    auth = Auth(user)

    if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
        home_sidebar = HomeSidebar()
        home_sidebar.create_sidebar()

        auth.display_forms()

    else:
        user_sidebar = UserSidebar()
        menu_option = user_sidebar.create_sidebar()

        portfolio_manager = PortfolioManager(user_id=st.session_state['user_id'])
        ai_manager = AIManager()
        backtest_manager = BacktestManager(user_id=st.session_state['user_id'])

        st.subheader(menu_option, divider="grey")

        if menu_option == "New Portfolio":
            PortfolioBuilder(portfolio_manager, ai_manager).display()
        elif menu_option == "Portfolio Overview":
            OverviewBuilder(portfolio_manager, backtest_manager).display()
        elif menu_option == "Edit Portfolios":
            EditBuilder(portfolio_manager).display()
        elif menu_option == "Trading Simulator":
            BacktestBuilder(portfolio_manager, backtest_manager).display()

if __name__ == "__main__":
    main()

