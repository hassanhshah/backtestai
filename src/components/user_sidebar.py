from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import time

from ..utils.session_utils import SessionUtils

class UserSidebar:
    def __init__(self, logo_path="src/assets/logo.jpg"):
        self.logo_path = logo_path
    
    def add_logo(self):
        """Read and return a resized logo."""
        logo = Image.open(self.logo_path)
        # Potentially resize or modify the logo here as needed
        return logo
    
    def create_sidebar(self):
        menu_option = None  # Initialize menu_option to None
        
        st.sidebar.image(self.add_logo()) 

        if 'user_id' in st.session_state and st.session_state['user_id'] is not None:
            with st.sidebar:
                menu_option = option_menu(
                    menu_title="Main Menu",
                    options=["New Portfolio", "Portfolio Overview", "Edit Portfolios", "Trading Simulator"],
                    icons=["plus", "bar-chart-line", "pencil-square", "play-circle"],
                    menu_icon="bi bi-graph-up",
                    default_index=0,
                    styles={
                        "container": {"padding": "5px", "background-color": "#FFFFFF"},
                        "icon": {"color": "#1a2d3d", "font-size": "16px"},
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#ecddc0", "color": "#1a2d3d"},
                        "nav-link-selected": {"background-color": "#ecddc0"}

                    }
                )    
                if st.sidebar.button("Logout"):
                    st.session_state['user_id'] = None
                    SessionUtils.reset_session_state() 
                    st.success("You have been logged out.")
                    with st.spinner('Logging out... Please wait.'):
                        time.sleep(2)
                    st.rerun()

        st.sidebar.markdown("""
        ### Welcome to **Backtest AI**! 🚀

        This platform empowers you to create and refine investment portfolios with ease. Test your investment strategies in simulated environments, leveraging your own insights and AI-driven recommendations.
                            
        ***Key Features***:

        **Manual Portfolio Builder**: Handpick your assets to assemble a portfolio that matches your investment goals.  
        **AI Portfolio Builder**: Leverage AI to assemble a customized collection of stocks for your targeted portfolios.  
        **Portfolio Overview**: Monitor and analyze the performance of your portfolios over time.    
        **Trading Simulator**: Backtest your investment strategies to gauge potential returns and refine your approach based on historical data.

        **Please Note**: Insights and simulations provided by Backtest AI are for educational purposes only and not to be taken as investment advice.

        **What's Coming?** Stay tuned for more updates and features to enhance your investment decision-making process!
                            
        ***Coming Soon: Customize your backtesting strategies using AI!***
        """, unsafe_allow_html=True)

        return menu_option