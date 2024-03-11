-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS backtestdb;
USE backtestdb;

-- Create the User table
CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login DATETIME NULL
);

-- Create the Portfolio table
CREATE TABLE IF NOT EXISTS Portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    portfolio_name VARCHAR(255),
    creation_date DATETIME NOT NULL,
    description TEXT,
    UNIQUE (user_id, portfolio_name),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- Create the StockData table
CREATE TABLE IF NOT EXISTS StockData (
    stock_data_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_name VARCHAR(255),
    transaction_date DATE,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    closing_price DECIMAL(10, 2),
    volume BIGINT,
    dividends DECIMAL(10, 2),
    stock_splits INT
);

-- Create the PortfolioStock table
CREATE TABLE IF NOT EXISTS PortfolioStock (
    portfolio_id INT,
    stock_data_id INT,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_data_id) REFERENCES StockData(stock_data_id) ON DELETE CASCADE,
    PRIMARY KEY (portfolio_id, stock_data_id)
);
