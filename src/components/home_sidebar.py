from PIL import Image
import streamlit as st

class HomeSidebar:
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