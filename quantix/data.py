import yfinance as yf
import pandas as pd
from pathlib import Path


def download_stock_data(
    ticker: str, start: str, end: str, should_save: bool = True, path: str = "../data"
) -> pd.DataFrame:
    """
    This kickass function is going to get stock data from yfinance and return a cleaned DataFrame.
    """
    df = yf.download(ticker, start=start, end=end)
    df.columns = df.columns.droplevel("Ticker")  # if the level is named
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df = df.sort_index()
    print(f"Data fetched successfully for ticker {ticker} from {start} to {end}.")
    # Create a directory to save data if it doesn't exist
    Path(path).mkdir(parents=True, exist_ok=True)
    if should_save:
        print(f"Saving data to {path}/{ticker}.csv")
        # Save the data to a CSV file
        df.to_csv(f"{path}/{ticker}.csv")
        print(f"data saved to {path}/{ticker}.csv")

    return df


def load_stock_data(ticker: str, path: str = "../data") -> pd.DataFrame:
    print(f"loading stock data from {path}/{ticker}.csv")
    df = pd.read_csv(f"{path}/{ticker}.csv", index_col=0, parse_dates=True)
    return df


def add_returns_and_sd(df: pd.DataFrame) -> pd.DataFrame:
    df["Returns"] = df["Close"].pct_change()
    df["SD"] = df["Returns"].rolling(window=20).std()
    return df


if __name__ == "__main__":
    print("Hello I'm a module")
