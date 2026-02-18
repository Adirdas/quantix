# Week 2 — Understanding Market Data

## Goals

- Load saved data
- Explore structure
- Plot price
- Compute daily returns

## Load data

```python
import pandas as pd

df = pd.read_csv("data/raw/SPY.csv", index_col=0, parse_dates=True)
print(df.head())
```

## Plot closing price

```python
import matplotlib.pyplot as plt

df["Close"].plot(title="SPY Close Price")
plt.show()
```

## Daily returns

```python
df["Return"] = df["Close"].pct_change()
print(df[["Close", "Return"]].head())
```

## Outcome

He understands what prices and returns look like in real data.
