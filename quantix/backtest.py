import yfinance as yf
import pandas as pd
from pathlib import Path
from numpy import cumprod



class Backtester:
    def __init__(self, strategy, initial_capital: float = 10000, percent_per_trade: float = 0.1):
        self.strategy = strategy
        self.data = strategy.data
        self.initial_capital = initial_capital
        self.percent_per_trade = percent_per_trade

    def backtest(self):
        # fields we need: strategy_return, cumulative_strategy_return, cumulative_buy_and_hold_return
        # loop through each period.
        # if the period before has a buy signal, and we are not long then we buy at the open of the current period and hold
        # if the period before has a sell and we are holding shares we sell at the close of the current period. no short sale for now.

        # lets start by looping through each period and calculating the strategy return based on the signal and the return of the stock
        self.data["strategy_return"] = 0.0
        position = 0  # 1 for long, 0 for no position
        trades = [] # will be a list of objects {"long_price": price, "shares": shares, "long_date": date, "capital_invested": capital_invested, "sale_price": price, "sale_date": date, "capital_gained": capital_gained, "return": return}
        for i in range(1, len(self.data)):
            if self.data["signal"].iloc[i-1] == 1 and position == 0:  # buy signal and not currently long
                position = 1
                # record purchase price of the stock at the open of the current period and calculate the number of shares we can buy with our initial capital and percent per trade
                purchase_price = self.data["Open"].iloc[i]
                shares_to_buy = (self.initial_capital * self.percent_per_trade) // purchase_price
                # add a row to trades list with the details of the trade (buy/sell, price, shares, date)
                trades.append({"long_price": purchase_price, "shares": shares_to_buy, "long_date": self.data.index[i], "capital_invested": purchase_price * shares_to_buy})

            elif (self.data["signal"].iloc[i-1] == -1 and position == 1) or (i == len(self.data) - 1):  # sell signal and currently long
                position = 0
                # record sale price of the stock at the close of the current period and calculate the number of shares we can sell
                sale_price = self.data["Close"].iloc[i]
                # get last row of trades and update it with the sale details (sale price, date, capital gained/lost, return)
                trades[-1].update({"sale_price": sale_price, "sale_date": self.data.index[i], "capital_gained": (sale_price - trades[-1]["long_price"]) * trades[-1]["shares"], "return": (sale_price - trades[-1]["long_price"]) / trades[-1]["long_price"]})

            # add a long flag to data to indicate we are long for the next periods until we sell
            self.data.loc[self.data.index[i], "long"] = 1 if (position == 1) else 0

        self.trades = trades

        # calculate strategy return for each period based on the trades we made
        for trade in trades:
            # loop over the data from the long date to the sale date and set strategy return for those periods based on the return of the trade
            long_index = self.data.index.get_loc(trade["long_date"])
            sale_index = self.data.index.get_loc(trade["sale_date"])
            self.data.loc[self.data.index[long_index:sale_index], "strategy_return"] += trade["return"] / (sale_index - long_index)  # distribute return evenly across the holding period
        # calculate cumulative returns
        self.data["cumulative_strategy_return"] = (1 + self.data["strategy_return"]).cumprod() - 1
        self.data["cumulative_buy_and_hold_return"] = (1 + self.data["Return"]).cumprod() - 1
