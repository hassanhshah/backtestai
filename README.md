# BacktestAI

Welcome to Backtest AI, the  platform for simulating and refining investment strategies. With an intuitive interface and powerful tools, Backtest AI provides a comprehensive suite of features for both novice and experienced investors looking to test their investment strategies in a simulated environment.

https://github.com/hassanhshah/backtestai/assets/98497536/cc378395-3a5c-452d-b9aa-8c128d4644ab



## Features

Backtest AI offers a range of features designed to help you create, monitor, and refine your investment portfolios:

Manual Portfolio Builder: Handpick your assets to assemble a portfolio that matches your investment goals.
![Manual](/images/add_portfolios.png)
AI Portfolio Builder: Leverage AI to assemble a customized collection of stocks for your targeted portfolios.
![AI](/images/ai_portfolio.png)
Portfolio Overview: Monitor and analyze the performance of your portfolios over time.
![Overview](/images/portfolio_overview.png)
Trading Simulator: Backtest your investment strategies to gauge potential returns and refine your approach based on historical data.
![Trading](/images/trading_simulator.png)

### Getting Started

### 1. Clone the repository:
```bash
git clone https://github.com/hassanhshah/backtestai.git
cd backtestai
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Setup:
Ensure your MySQL database is up and running. Execute the SQL commands found in 'src/database/schema.sql' to create the necessary database and tables:
```sql
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS backtestdb;
USE backtestdb;

-- SQL statements for creating tables...
```
This step prepares the database structure for storing users, portfolios, and stock data.

### 4. Configure Application Secrets:
Within the '.streamlit' subdirectory in the root directory, locate the 'secrets.toml' file. Fill in the following fields with your specific details:
```python
open_api_key = "<YOUR_API_KEY>"

[mysql]
host = "<YOUR_DATABASE_HOST>"
user = "<YOUR_DATABASE_USER>"
password = "<YOUR_DATABASE_PASSWORD>"
database = "<YOUR_DATABASE_NAME>"
```
These settings are crucial for connecting to OpenAI and the database.

### Launching the Application

### 1. Start the App:
```bash
streamlit run app.py
```

### 2. Access the Platform:
Open the URL provided in the command line output in your web browser to interact with Backtest AI locally.

Running Backtest AI locally allows you to utilize your own database and hardware resources, offering a quicker response time and a more fluid user experience.

## Please Note

* The insights and simulations provided by Backtest AI are for educational purposes only and should not be construed as investment advice.
* Always conduct your own research or consult with a financial advisor before making investment decisions.

## What's Coming?

* Stay tuned for upcoming features, including customizable backtesting strategies using AI, to further enhance your investment decision-making process.
