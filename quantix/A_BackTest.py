import pandas as pd
import matplotlib.pyplot as plt


class Backtester:
    """Simple event-driven backtester for daily signal data.

    Assumptions:
    - the strategy has already populated flat ``Open``, ``Close``, ``Return``,
      and ``signal`` columns
    - a buy or sell signal generated on day ``t`` is acted on during day
      ``t + 1``
    - entries are modeled at the next day's open and exits at that day's close

    The backtester records closed trades in ``self.trades`` and appends
    position and cumulative return columns to ``self.data``.
    """

    def __init__(
        self, strategy, initial_capital: float = 10000, percent_per_trade: float = 0.1
    ):
        self.strategy = strategy
        self.data = strategy.data.copy()
        self.initial_capital = initial_capital
        self.percent_per_trade = percent_per_trade
        self.trades = []

    def backtest(self, stop_loss_pct: float = 0.10):
        """Run the backtest over the strategy output.

        Parameters
        ----------
        stop_loss_pct:
            Fractional stop loss threshold measured from the entry price.
        """
        self.trades = []
        required_cols = {"Open", "Close", "Return", "signal"}

        missing = required_cols - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        self.data["position"] = 0
        self.data["strategy_return"] = 0.0

        position = 0
        entry_price = None
        entry_date = None

        for i in range(1, len(self.data)):
            today_close = self.data["Close"].iloc[i]
            today_open = self.data["Open"].iloc[i]
            previous_signal = self.data["signal"].iloc[i - 1]

            if position == 0:
                if previous_signal == 1:
                    position = 1
                    entry_price = today_open
                    entry_date = self.data.index[i]

                    self.trades.append(
                        {
                            "entry_date": entry_date,
                            "entry_price": entry_price,
                            "exit_date": None,
                            "exit_price": None,
                            "return": None,
                            "reason": None,
                        }
                    )

            else:
                stop_price = entry_price * (1 - stop_loss_pct)
                exit_reason = None
                exit_price = None

                if today_close <= stop_price:
                    exit_reason = "stop_loss"
                    exit_price = today_close
                elif previous_signal == -1:
                    exit_reason = "signal_exit"
                    exit_price = today_close
                elif i == len(self.data) - 1:
                    exit_reason = "final_bar"
                    exit_price = today_close

                if exit_reason is not None:
                    trade_return = (exit_price - entry_price) / entry_price

                    self.trades[-1]["exit_date"] = self.data.index[i]
                    self.trades[-1]["exit_price"] = exit_price
                    self.trades[-1]["return"] = trade_return
                    self.trades[-1]["reason"] = exit_reason

                    position = 0
                    entry_price = None
                    entry_date = None

            self.data.loc[self.data.index[i], "position"] = position

        self.data["strategy_return"] = self.data["Return"] * self.data[
            "position"
        ].shift(1).fillna(0)
        self.data["cumulative_strategy_return"] = (
            1 + self.data["strategy_return"]
        ).cumprod() - 1
        self.data["cumulative_buy_and_hold_return"] = (
            1 + self.data["Return"]
        ).cumprod() - 1

        return self.data

    def stats(self):
        """Return aggregate metrics for closed trades and benchmark returns."""
        closed_trades = [t for t in self.trades if t["return"] is not None]
        if not closed_trades:
            return {}

        returns = pd.Series([t["return"] for t in closed_trades])

        return {
            "num_trades": len(closed_trades),
            "win_rate": (returns > 0).mean(),
            "avg_trade_return": returns.mean(),
            "best_trade": returns.max(),
            "worst_trade": returns.min(),
            "total_strategy_return": self.data["cumulative_strategy_return"].iloc[-1],
            "buy_and_hold_return": self.data["cumulative_buy_and_hold_return"].iloc[-1],
        }

    def plot_trades(self):
        """Plot price, indicators, RSI, and executed entry/exit markers."""
        required_cols = {"Close", "MA50", "MA200", "RSI"}
        missing = required_cols - set(self.data.columns)
        if missing:
            raise ValueError(
                f"Missing required columns for plotting: {missing}. "
                "Run the strategy signal generation before plotting."
            )

        closed_trades = [trade for trade in self.trades if trade["exit_date"] is not None]
        entries = pd.DataFrame(
            {
                "date": [trade["entry_date"] for trade in closed_trades],
                "price": [trade["entry_price"] for trade in closed_trades],
            }
        )
        exits = pd.DataFrame(
            {
                "date": [trade["exit_date"] for trade in closed_trades],
                "price": [trade["exit_price"] for trade in closed_trades],
                "reason": [trade["reason"] for trade in closed_trades],
            }
        )

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

        if not entries.empty:
            price_ax.scatter(
                entries["date"],
                entries["price"],
                label="Entry",
                marker="^",
                color="green",
                s=80,
                zorder=3,
            )

        if not exits.empty:
            price_ax.scatter(
                exits["date"],
                exits["price"],
                label="Exit",
                marker="v",
                color="red",
                s=80,
                zorder=3,
            )

        price_ax.set_title("Backtest Executions")
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
