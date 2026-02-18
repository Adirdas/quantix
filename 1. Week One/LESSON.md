# Week 1 — Repo, Setup, and First Data Pull

## Goals

* Create the Git repo and project structure
* Set up a virtual environment
* Install `pandas` and `yfinance`
* Download SPY daily data and save to disk

## Folder structure

```
src/trading_platform/data/
data/raw/
```

## Install dependencies

```bash
pip install pandas yfinance
```

## yfinance client (`src/trading_platform/data/yfinance_client.py`)

```python
import yfinance as yf
import pandas as pd


def download_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(symbol, start=start, end=end, interval="1d")
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df
```

## Save to disk

```python
from pathlib import Path


def save_to_csv(df, symbol):
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    df.to_csv(f"data/raw/{symbol}.csv")
```

## Run script

```python
from yfinance_client import download_data, save_to_csv

df = download_data("SPY", "2015-01-01", "2024-01-01")
save_to_csv(df, "SPY")
print(df.head())
```

## Outcome

You can fetch and store market data locally.
