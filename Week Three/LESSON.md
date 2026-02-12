# Week 3 — Indicators and Features

## Goals

- Rolling mean and standard deviation
- Prepare for z score

## Add features

```python
window = 20

df["roll_mean"] = df["Return"].rolling(window).mean()
df["roll_std"] = df["Return"].rolling(window).std()
```

## Visualize

```python
df[["Return", "roll_mean"]].plot()
plt.show()
```

## Outcome

Raw prices become features for modelling.
