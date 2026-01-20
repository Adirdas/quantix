# Milestone 1: “Get reliable data from yfinance”

import yfinance as yf
import pandas as pd
import pprint

# Define the ticker symbol for Apple Inc.
ticker_symbol = "AAPL"

# Fetch historical market data for Apple Inc. from yfinance
ticker = yf.Ticker(ticker_symbol)

print("Ticker properties available for inspection:")
print("_" * 50)
# pprint.pprint(ticker.info)  # Display general information about the ticker
print()

print(ticker.info["sectorDisp"])
