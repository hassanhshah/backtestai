from src.database.connection import get_db_connection
import streamlit as st

class LiveStatistics:
    def __init__(self):
        self.db_connection = get_db_connection()
        self.cursor = self.db_connection.cursor(buffered=True)

    def count_all_portfolios(self):
        query = "SELECT COUNT(*) FROM Portfolio"
        self.cursor.execute(query)
        (count,) = self.cursor.fetchone()
        return count

    def count_all_stocks(self):
        query = """
        SELECT COUNT(DISTINCT stock_name)
        FROM StockData
        """
        self.cursor.execute(query)
        (count,) = self.cursor.fetchone()
        return count

    @staticmethod
    def display_live_counts():
        stats = LiveStatistics()
        portfolio_count = stats.count_all_portfolios()
        stock_count = stats.count_all_stocks()
        st.markdown("---")
        st.markdown("### Live Counts")
        st.write(f"Total Portfolios: **{portfolio_count}**")
        st.write(f"Total Stocks: **{stock_count}**")