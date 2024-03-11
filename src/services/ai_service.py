import openai
import time
import streamlit as st

openai.api_key = st.secrets["open_api_key"]

class AIManager:
    def create_ai_portfolio(self, user_request):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "\"Given a user's request for a stock portfolio, your task is to recommend a suitable set of stocks, ensuring that all recommended tickers are valid, existing on stock exchanges, and can be used to retrieve data from financial databases like Yahoo Finance. Use the following examples to guide your recommendations:\n\nExample 1:\nUser Request: 'I want a portfolio focusing on renewable energy companies that are expected to grow in the next year.'\nOutput:\nPortfolio_Name:Renewable Energy\nStocks: ['NEE', 'ENPH', 'SEDG', 'RUN', 'TSLA']\nDescription: This portfolio focuses on high-growth renewable energy companies, selected for their innovative technology and potential market expansion in the upcoming year.\n\nExample 2:\nUser Request: 'Give me a portfolio of the Magnificent 7 tech stocks.'\nOutput:\nPortfolio_Name:Magnificent 7\nStocks: ['AMZN', 'AAPL', 'META', 'TSLA', 'MSFT', 'NVDA', 'GOOG']\nDescription: \"This portfolio comprises the 'Magnificent 7' of the tech industry, known for their robust market presence and innovative contributions to technology. These companies have consistently demonstrated strong performance and are considered leaders in their respective fields, offering a blend of growth, stability, and innovation potential.\""
                },
                {
                    "role": "user",
                    "content": user_request
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[-1].message['content']
    
    def parse_ai_response(self, response):
        parsed_data = {}
        lines = response.split('\n')
        try:
            parsed_data['portfolio_name'] = lines[0].split(':')[1].strip()
            stock_symbols_str = lines[1].split(':')[1].strip().strip('[]')
            parsed_data['stock_symbols'] = [sym.strip().strip("'").strip('"') for sym in stock_symbols_str.split(',')]
            parsed_data['description'] = lines[2].split(':')[1].strip()
            if not parsed_data['portfolio_name'] or not parsed_data['stock_symbols']or not parsed_data['description']:
                return False, {}
            return True, parsed_data
        except Exception as e:
            print(f"Error parsing AI portfolio creation: {e}")
            return False, {}
    
    def ai_stream(self, input_string):
        for char in input_string:
            time.sleep(0.01)
            yield char