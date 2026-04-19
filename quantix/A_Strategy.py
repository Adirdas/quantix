import pandas as pd


class PullbackStrategy:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def compute_rsi(self, period: int = 14):
        delta = self.data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.data["RSI"] = rsi

    def generate_signals(self):
        self.data["Return"] = self.data["Close"].pct_change().fillna(0)
        self.data["MA50"] = self.data["Close"].rolling(50).mean()
        self.data["MA200"] = self.data["Close"].rolling(200).mean()

        self.compute_rsi(14)

        self.data["signal"] = 0

        uptrend = self.data["Close"] > self.data["MA200"]
        above_ma50 = self.data["Close"] > self.data["MA50"]
        rsi_cross_above_40 = (self.data["RSI"].shift(1) <= 40) & (self.data["RSI"] > 40)
        
        rsi_overbought = self.data["RSI"] > 70
        below_ma50 = self.data["Close"] < self.data["MA50"]

        buy_condition = uptrend & above_ma50 & rsi_cross_above_40
        sell_condition = rsi_overbought | below_ma50

        self.data.loc[buy_condition, "signal"] = 1
        self.data.loc[sell_condition, "signal"] = -1

        return self.data