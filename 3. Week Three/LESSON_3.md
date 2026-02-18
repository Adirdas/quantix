# Week 3.5 — Classes and Interfaces

## Goals

- Learn classes through trading examples
- Understand a common strategy interface

## Simple strategy class

```python
class BuyAndHoldStrategy:
    def generate_signal(self, row):
        return "BUY"
```

## Another strategy with same method

```python
class DummyStrategy:
    def generate_signal(self, row):
        return "SELL"
```

## Key rule

Any strategy must implement `generate_signal(row)`.

## Outcome

Understands classes because the system needs them.
