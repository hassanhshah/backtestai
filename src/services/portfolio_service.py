import numpy as np
import yfinance as yf
import mysql.connector

from datetime import datetime, timedelta
from src.database.connection import get_db_connection

class PortfolioManager:
    def __init__(self, user_id=None):
        self.db_connection = get_db_connection()
        self.cursor = self.db_connection.cursor()
        self.user_id = user_id

    def get_stock_data(self, stock_name, start_date="2024-01-01", end_date=datetime.now().date()):
        stock = yf.Ticker(stock_name)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            return df
        df.ffill(inplace=True)
        df.bfill(inplace=True)
        return df
    
    def is_valid_ticker(self, ticker_symbol):
        stock = yf.Ticker(ticker_symbol)
        # Check if the ticker symbol returns any historical data
        try:
            return not stock.history(period="5d").empty
        except:
            return False
    
    def get_portfolio_id(self, portfolio_name):
        query = """
            SELECT portfolio_id FROM Portfolio
            WHERE user_id = %s AND portfolio_name = %s;
        """
        self.cursor.execute(query, (self.user_id, portfolio_name))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def add_portfolio(self, portfolio_name, description=None):
        creation_date = datetime.now()
        self.cursor.execute("SELECT COUNT(*) FROM Portfolio WHERE user_id = %s AND portfolio_name = %s", (self.user_id, portfolio_name,))
        if self.cursor.fetchone()[0] > 0:
            return False, f"Portfolio '{portfolio_name}' already exists."
        try:
            self.cursor.execute(
                "INSERT INTO Portfolio (user_id, portfolio_name, creation_date, description) VALUES (%s, %s, %s, %s)",
                (self.user_id, portfolio_name, creation_date, description)
            )
            self.db_connection.commit()
            return True, f"Portfolio '{portfolio_name}' successfully created."
        except mysql.connector.Error as err:
            return False, f"Failed to create portfolio '{portfolio_name}': {str(err)}"
    
    def remove_portfolio(self, portfolio_name):
        try:
            portfolio_id = self.get_portfolio_id(portfolio_name)
            if portfolio_id:
                delete_query = "DELETE FROM Portfolio WHERE user_id = %s AND portfolio_id = %s"
                self.cursor.execute(delete_query, (self.user_id, portfolio_id,))
                self.db_connection.commit()
                return True, f"Portfolio '{portfolio_name}' and all associated stocks have been removed successfully."
            else:
                return False, f"Portfolio '{portfolio_name}' does not exist."
        except Exception as e:
            return False, f"Failed to remove portfolio '{portfolio_name}': {str(e)}"

    def add_stock_to_portfolio(self, portfolio_name, stock_symbol):
        portfolio_id = self.get_portfolio_id(portfolio_name)
        if not portfolio_id:
            return False, f"Portfolio '{portfolio_name}' does not exist."
        if not self.is_valid_ticker(stock_symbol):
            return False, f"Invalid stock: '{stock_symbol}'."
        
        existing_stocks = self.fetch_all_stocks(portfolio_id)
        if stock_symbol in existing_stocks:
            return False, f"Stock '{stock_symbol}' is already in the portfolio '{portfolio_name}'."
        stock_data = self.get_stock_data(stock_symbol)
        if stock_data.empty:
            return False, "No data available for '{stock_symbol}'."

        for index, row in stock_data.iterrows():
            stock_splits = row['Stock Splits'] if 'Stock Splits' in row else 0
            # Insert stock data into StockData table
            self.cursor.execute("""
                INSERT INTO StockData (stock_name, transaction_date, open_price, high_price, low_price, closing_price, volume, dividends, stock_splits)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                open_price = VALUES(open_price), high_price = VALUES(high_price),
                low_price = VALUES(low_price), closing_price = VALUES(closing_price),
                volume = VALUES(volume), dividends = VALUES(dividends), stock_splits = VALUES(stock_splits)
            """, (stock_symbol, index.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['Dividends'], stock_splits))
            self.db_connection.commit()

            # Link the latest stock_data_id with the portfolio
            stock_data_id = self.cursor.lastrowid
            self.cursor.execute("""
                INSERT INTO PortfolioStock (portfolio_id, stock_data_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE stock_data_id = VALUES(stock_data_id)
            """, (portfolio_id, stock_data_id))
            self.db_connection.commit()
        return True, f"Stock '{stock_symbol}' data added and linked to portfolio '{portfolio_name}'."
        
    def remove_stock_from_portfolio(self, portfolio_name, stock_symbol):
    # Fetch the portfolio_id
        portfolio_id = self.get_portfolio_id(portfolio_name)
        if not portfolio_id:
            return False, f"Portfolio '{portfolio_name}' does not exist."

        try:
            # Fetch stock_data_ids associated with this stock_name
            self.cursor.execute("""
                SELECT sd.stock_data_id 
                FROM StockData sd
                JOIN PortfolioStock ps ON sd.stock_data_id = ps.stock_data_id
                WHERE sd.stock_name = %s AND ps.portfolio_id = %s
            """, (stock_symbol, portfolio_id))

            stock_data_ids = [row[0] for row in self.cursor.fetchall()]

            if not stock_data_ids:
                return False, f"No data for stock '{stock_symbol}' in portfolio '{portfolio_name}'."

            # Remove associations from PortfolioStock
            for stock_data_id in stock_data_ids:
                self.cursor.execute("""
                    DELETE FROM PortfolioStock 
                    WHERE portfolio_id = %s AND stock_data_id = %s
                """, (portfolio_id, stock_data_id))
                self.db_connection.commit()

            return True, f"Stock '{stock_symbol}' removed from portfolio '{portfolio_name}'."
        except Exception as e:
            return False, str(e)
        
    def get_last_login_date(self, user_id):
        """Retrieve the last login date of a user."""
        query = "SELECT last_login FROM User WHERE user_id = %s"
        try:
            self.cursor.execute(query, (user_id,))
            last_login = self.cursor.fetchone()[0]
            return last_login
        except mysql.connector.Error as err:
            return None

    def update_stock_data(self):
        today = datetime.now().date()
        last_login = self.get_last_login_date(self.user_id)  # You need to implement this method

        # Check if last login is more than two days before today
        if last_login and (today - last_login.date()).days > 2:
            self.cursor.execute("SELECT DISTINCT ps.portfolio_id FROM PortfolioStock ps JOIN Portfolio p ON ps.portfolio_id = p.portfolio_id WHERE p.user_id = %s", (self.user_id,))
            portfolio_ids = [item[0] for item in self.cursor.fetchall()]

            for portfolio_id in portfolio_ids:
                self.cursor.execute("""
                    SELECT DISTINCT sd.stock_name, MAX(sd.transaction_date) as last_transaction_date
                    FROM StockData sd
                    JOIN PortfolioStock ps ON sd.stock_data_id = ps.stock_data_id
                    WHERE ps.portfolio_id = %s
                    GROUP BY sd.stock_name
                """, (portfolio_id,))
                
                stocks_data = self.cursor.fetchall()

                for stock_name, last_transaction_date in stocks_data:
                    if last_transaction_date is not None:
                        # Only update from the day after the last transaction date to today
                        start_date = (last_transaction_date + timedelta(days=1)).strftime('%Y-%m-%d')
                    else:
                        # If there's no transaction data, use a default start date
                        start_date = "2024-01-01"
                    
                    stock_data = self.get_stock_data(stock_name, start_date, today.strftime('%Y-%m-%d'))
                    if not stock_data.empty:
                        for index, row in stock_data.iterrows():
                            self.cursor.execute("""
                                INSERT INTO StockData (stock_name, transaction_date, open_price, high_price, low_price, closing_price, volume, dividends, stock_splits)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE 
                                open_price = VALUES(open_price), high_price = VALUES(high_price),
                                low_price = VALUES(low_price), closing_price = VALUES(closing_price),
                                volume = VALUES(volume), dividends = VALUES(dividends), stock_splits = VALUES(stock_splits)
                            """, (stock_name, index.strftime('%Y-%m-%d'), row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row.get('Dividends', 0), row.get('Stock Splits', 0)))
                            self.db_connection.commit()

    def fetch_portfolio_names(self):
        query = "SELECT portfolio_name FROM Portfolio WHERE user_id = %s"
        self.cursor.execute(query, (self.user_id,))
        portfolio_names = [item[0] for item in self.cursor.fetchall()]
        return portfolio_names
    
    
    def fetch_all_portfolios(self):
        query = "SELECT portfolio_id, portfolio_name, creation_date, description FROM Portfolio WHERE user_id = %s"
        self.cursor.execute(query, (self.user_id,))
        portfolios_data = self.cursor.fetchall()
        
        portfolios_info = [] 
        
        for portfolio_id, portfolio_name, creation_date, description in portfolios_data:
            stocks = self.fetch_all_stocks(portfolio_id)
            portfolios_info.append((portfolio_name, creation_date, stocks, description))
        
        return portfolios_info

    def fetch_all_stocks(self, portfolio_id):
        try:
            # Adjusted to fetch stock names via the StockData association in PortfolioStock
            self.cursor.execute("""
                SELECT DISTINCT sd.stock_name
                FROM StockData sd
                JOIN PortfolioStock ps ON sd.stock_data_id = ps.stock_data_id
                WHERE ps.portfolio_id = %s
            """, (portfolio_id,))
            stocks_data = self.cursor.fetchall()
            return [stock[0] for stock in stocks_data]
        except Exception as e:
            return []

