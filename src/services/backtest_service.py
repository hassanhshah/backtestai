import numpy as np
import pandas as pd
import datetime
from src.database.connection import get_db_connection

class BacktestManager:
    def __init__(self, user_id=None):
        self.db_connection = get_db_connection()
        self.cursor = self.db_connection.cursor()
        self.user_id = user_id

    def get_portfolio_id(self, portfolio_name):
        query = """
            SELECT portfolio_id FROM Portfolio
            WHERE user_id = %s AND portfolio_name = %s;
        """
        self.cursor.execute(query, (self.user_id, portfolio_name))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_simulation_data(self, portfolio_name):
        portfolio_id = self.get_portfolio_id(portfolio_name)
        if not portfolio_id:
            return [], pd.DataFrame()

        query = """
        SELECT sd.stock_name, sd.transaction_date, sd.open_price, sd.high_price, sd.low_price, sd.closing_price, sd.volume, sd.dividends, sd.stock_splits
        FROM StockData sd
        JOIN PortfolioStock ps ON sd.stock_data_id = ps.stock_data_id
        WHERE ps.portfolio_id = %s;
        """
        self.cursor.execute(query, (portfolio_id,))
        rows = self.cursor.fetchall()

        columns = [desc[0] for desc in self.cursor.description]
        sim_data = pd.DataFrame(rows, columns=columns)

        historical_data_list = [group[1] for group in sim_data.groupby('stock_name')]
        sim_data.sort_values(by='transaction_date', inplace=True)

        return historical_data_list, sim_data
    
    def generate_signals(self, stock_data, selected_factors):


        stock_data['closing_price'] = stock_data['closing_price'].astype(float)
        stock_data['Daily_Return'] = stock_data['closing_price'].pct_change()
        stock_data['Log_Return'] = np.log(stock_data['closing_price'] / stock_data['closing_price'].shift(1))
        stock_data['MA_7'] = stock_data['closing_price'].rolling(window=7).mean()
        stock_data['MA_30'] = stock_data['closing_price'].rolling(window=30).mean()
        stock_data['Volatility'] = stock_data['Daily_Return'].rolling(window=30).std()
        delta = stock_data['closing_price'].diff(1)
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        stock_data['RSI'] = 100 - (100 / (1 + rs))

        stock_data['EMA12'] = stock_data['closing_price'].ewm(span=12, adjust=False).mean()
        stock_data['EMA26'] = stock_data['closing_price'].ewm(span=26, adjust=False).mean()
        stock_data['MACD'] = stock_data['EMA12'] - stock_data['EMA26']
        stock_data['MACD_signal'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()

        stock_data['SMA20'] = stock_data['closing_price'].rolling(window=20).mean()
        stock_data['Upper_Band'] = stock_data['SMA20'] + (2 * stock_data['closing_price'].rolling(window=20).std())
        stock_data['Lower_Band'] = stock_data['SMA20'] - (2 * stock_data['closing_price'].rolling(window=20).std())

        stock_data['buy_signal'] = False
        stock_data['sell_signal'] = False
        stock_data['Buy_Votes'] = 0
        stock_data['Sell_Votes'] = 0

        rsi_lower_threshold = 30
        rsi_upper_threshold = 70
        daily_return_avg = stock_data['Daily_Return'].mean()

        threshold = round(len(selected_factors) / 3)
        for i in range(1, len(stock_data)):
            buy_votes = 0
            sell_votes = 0
            if 'Relative Strength Index (RSI)' in selected_factors:
                if stock_data['RSI'].iloc[i] < rsi_lower_threshold: buy_votes += 1
                if stock_data['RSI'].iloc[i] > rsi_upper_threshold: sell_votes += 1
            if 'Moving Average Convergence/Divergence (MACD)' in selected_factors:
                if stock_data['MACD'].iloc[i] > stock_data['MACD_signal'].iloc[i]: buy_votes += 1
                if stock_data['MACD'].iloc[i] < stock_data['MACD_signal'].iloc[i]: sell_votes += 1
            if 'Bollinger Bands' in selected_factors:
                if stock_data['closing_price'].iloc[i] < stock_data['Lower_Band'].iloc[i]: buy_votes += 1
                if stock_data['closing_price'].iloc[i] > stock_data['Upper_Band'].iloc[i]: sell_votes += 1
            if 'Moving Average' in selected_factors:
                if stock_data['MA_7'].iloc[i] < stock_data['MA_30'].iloc[i]: buy_votes += 1
                if stock_data['MA_7'].iloc[i] > stock_data['MA_30'].iloc[i]: sell_votes += 1
            if 'Daily Return' in selected_factors:
                if stock_data['Daily_Return'].iloc[i] > daily_return_avg: buy_votes += 1
                if stock_data['Daily_Return'].iloc[i] < daily_return_avg: sell_votes += 1
            if 'Volatility' in selected_factors:
                if stock_data['Volatility'].iloc[i] < stock_data['Volatility'].rolling(window=30).mean().iloc[i]: buy_votes += 1
                if stock_data['Volatility'].iloc[i] > stock_data['Volatility'].rolling(window=30).mean().iloc[i]: sell_votes += 1
            if 'Exponential Moving Average (EMA)' in selected_factors:
                if stock_data['EMA12'].iloc[i] > stock_data['EMA26'].iloc[i]: buy_votes += 1
                if stock_data['EMA12'].iloc[i] < stock_data['EMA26'].iloc[i]: sell_votes += 1
            if 'Log Return' in selected_factors:
                if stock_data['Log_Return'].iloc[i] > 0: buy_votes += 1
                if stock_data['Log_Return'].iloc[i] < 0: sell_votes += 1

            stock_data.loc[stock_data.index[i], 'Buy_Votes'] = buy_votes
            stock_data.loc[stock_data.index[i], 'Sell_Votes'] = sell_votes

            if buy_votes > sell_votes + threshold:
                stock_data.loc[stock_data.index[i], 'buy_signal'] = True
            if sell_votes > buy_votes + threshold:
                stock_data.loc[stock_data.index[i], 'sell_signal'] = True
        return stock_data

    def simulate_trading(self, portfolio_name, initial_fund=10000.00, start_date=None, end_date=None, selected_factors=None):
        historical_data_list, sim_data = self.get_simulation_data(portfolio_name)
        sim_data.sort_values('transaction_date', inplace=True)

        # Ensure start_date and end_date are datetime.date objects for comparison
        if start_date and end_date:
            sim_data['transaction_date'] = pd.to_datetime(sim_data['transaction_date']).dt.date
            start_date = pd.to_datetime(start_date).date() if not isinstance(start_date, datetime.date) else start_date
            end_date = pd.to_datetime(end_date).date() if not isinstance(end_date, datetime.date) else end_date
            sim_data = sim_data[(sim_data['transaction_date'] >= start_date) & (sim_data['transaction_date'] <= end_date)]

        sim_data_with_signals = pd.concat([self.generate_signals(stock_data, selected_factors) for stock_data in historical_data_list])
        # Convert 'transaction_date' in sim_data_with_signals to datetime.date for consistent comparison
        sim_data_with_signals['transaction_date'] = pd.to_datetime(sim_data_with_signals['transaction_date']).dt.date

        cash_balance = initial_fund
        shares_held = {data['stock_name'].iloc[0]: 0 for data in historical_data_list}
        actions = []
        daily_portfolio_values = []

        unique_dates = sim_data['transaction_date'].unique()  # These are already datetime.date objects
        for date in unique_dates:
            daily_data = sim_data[sim_data['transaction_date'] == date]
            total_buy_signals = 0
            for stock_name, stock_data in daily_data.groupby('stock_name'):
                stock_data_signals = sim_data_with_signals[(sim_data_with_signals['stock_name'] == stock_name) &
                                                            (sim_data_with_signals['transaction_date'] == date)]
                buy_signals = stock_data_signals[stock_data_signals['buy_signal']]
                total_buy_signals += len(buy_signals)

            allocation_per_stock = cash_balance / total_buy_signals if total_buy_signals > 0 else 0

            for stock_name, stock_data in daily_data.groupby('stock_name'):
                stock_data_signals = sim_data_with_signals[(sim_data_with_signals['stock_name'] == stock_name) &
                                                            (sim_data_with_signals['transaction_date'] == date)]
                buy_signals = stock_data_signals[stock_data_signals['buy_signal']]
                sell_signals = stock_data_signals[stock_data_signals['sell_signal']]      
                if not buy_signals.empty:
                    for _, row in buy_signals.iterrows():
                        closing_price = float(row['closing_price'])
                        num_shares_to_buy = int(allocation_per_stock // closing_price) if allocation_per_stock > 0 else 0
                        if num_shares_to_buy > 0:
                            cost = num_shares_to_buy * closing_price
                            cash_balance -= cost
                            shares_held[stock_name] += num_shares_to_buy
                            actions.append(f"{date}: Buy {num_shares_to_buy} shares of {stock_name} at ${closing_price:.2f}, Cost: ${cost:.2f}, Cash Balance: ${cash_balance:.2f}")

                if not sell_signals.empty:
                    for _, row in sell_signals.iterrows():
                        closing_price = float(row['closing_price'])
                        num_shares_to_sell = shares_held[stock_name]
                        if num_shares_to_sell > 0:
                            sale_proceeds = num_shares_to_sell * closing_price
                            cash_balance += sale_proceeds
                            shares_held[stock_name] = 0
                            actions.append(f"{date}: Sell {num_shares_to_sell} shares of {stock_name} at ${closing_price:.2f}, Received: ${sale_proceeds:.2f}, Cash Balance: ${cash_balance:.2f}")

            date_portfolio_value = cash_balance
            for stock, shares in shares_held.items():
                stock_data = sim_data_with_signals[(sim_data_with_signals['stock_name'] == stock) & (sim_data_with_signals['transaction_date'] == date)]
                if not stock_data.empty:
                    closing_price = float(stock_data.iloc[0]['closing_price'])
                    date_portfolio_value += shares * closing_price
            daily_portfolio_values.append(date_portfolio_value)

        days = max(1, len(daily_portfolio_values) - 1)
        final_portfolio_value = daily_portfolio_values[-1]
        annualized_return = ((final_portfolio_value / initial_fund) ** (252 / days)) - 1

        daily_returns = [((daily_portfolio_values[i] - daily_portfolio_values[i - 1]) / daily_portfolio_values[i - 1]) for i in range(1, len(daily_portfolio_values))]
        excess_daily_returns = [r - (0.02 / 252) for r in daily_returns]
        sharpe_ratio = np.mean(excess_daily_returns) / np.std(excess_daily_returns) * np.sqrt(252)

        results = [
            f"Final Portfolio Value: ${final_portfolio_value:.2f}",
            f"Annualized Return: {annualized_return * 100:.2f}%",
            f"Sharpe Ratio: {sharpe_ratio:.2f}",
            ""
        ]
        dates = sim_data['transaction_date'].unique()
        daily_values_df = pd.DataFrame({'Portfolio Value': daily_portfolio_values}, index=pd.to_datetime(dates))

        final_holdings_value = 0
        for stock, shares in shares_held.items():
            if shares > 0:  # Only consider non-zero holdings
                final_price = sim_data_with_signals[sim_data_with_signals['stock_name'] == stock]['closing_price'].iloc[-1]
                stock_value = shares * final_price
                final_holdings_value += stock_value
                actions.append(f"{shares} shares of {stock} worth ${stock_value:.2f}")
        return results, actions, daily_values_df
