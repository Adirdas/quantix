import pandas as pd
import matplotlib.pyplot as plt


class PullbackStrategy:
    """Long-only pullback strategy built on daily OHLCV data.

    Expected input is a DataFrame with flat, single-level columns that include
    at least ``Close``. The strategy adds indicator and signal columns in place
    on a defensive copy of the provided data.

    Entry logic:
    - price is above the 200-day moving average
    - price is above the 50-day moving average
    - RSI crosses above 40 from the prior bar

    Exit logic:
    - RSI rises above 70, or
    - price falls below the 50-day moving average
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def compute_rsi(self, period: int = 14):
        """Compute a simple rolling RSI and store it in ``self.data['RSI']``."""
        delta = self.data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.data["RSI"] = rsi

    def generate_signals(self):
        """Populate indicator, return, and signal columns for the strategy.

        The method assumes a daily bar series with a flat ``Close`` column.
        Signals are generated on the current bar and are intended to be acted on
        by the backtester on the next trading day.
        """
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

    def plot_signals(self):
        """Plot price, moving averages, RSI, and buy/sell markers.

        Returns
        -------
        tuple
            Matplotlib ``(fig, axes)`` for further customization by the caller.
        """
        required_cols = {"Close", "MA50", "MA200", "RSI", "signal"}
        missing = required_cols - set(self.data.columns)
        if missing:
            raise ValueError(
                f"Missing required columns for plotting: {missing}. "
                "Run generate_signals() before plot_signals()."
            )

        buy_points = self.data[self.data["signal"] == 1]
        sell_points = self.data[self.data["signal"] == -1]

        fig, axes = plt.subplots(
            2,
            1,
            figsize=(14, 9),
            sharex=True,
            gridspec_kw={"height_ratios": [3, 1]},
        )

        price_ax, rsi_ax = axes

        price_ax.plot(self.data.index, self.data["Close"], label="Close", linewidth=1.8)
        price_ax.plot(self.data.index, self.data["MA50"], label="MA50", linewidth=1.2)
        price_ax.plot(self.data.index, self.data["MA200"], label="MA200", linewidth=1.2)
        price_ax.scatter(
            buy_points.index,
            buy_points["Close"],
            label="Buy Signal",
            marker="^",
            color="green",
            s=70,
            zorder=3,
        )
        price_ax.scatter(
            sell_points.index,
            sell_points["Close"],
            label="Sell Signal",
            marker="v",
            color="red",
            s=70,
            zorder=3,
        )
        price_ax.set_title("Pullback Strategy Signals")
        price_ax.set_ylabel("Price")
        price_ax.grid(True, alpha=0.3)
        price_ax.legend()

        rsi_ax.plot(self.data.index, self.data["RSI"], label="RSI", color="darkorange")
        rsi_ax.axhline(40, color="green", linestyle="--", linewidth=1, label="RSI 40")
        rsi_ax.axhline(70, color="red", linestyle="--", linewidth=1, label="RSI 70")
        rsi_ax.set_ylabel("RSI")
        rsi_ax.set_xlabel("Date")
        rsi_ax.set_ylim(0, 100)
        rsi_ax.grid(True, alpha=0.3)
        rsi_ax.legend()

        fig.tight_layout()
        return fig, axes
