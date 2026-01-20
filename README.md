# Quantix

a work in progress trading engine.

## Ground rules for the project

- Start with **research + backtesting + paper trading** first. No live orders until you have tests, logging, and risk limits.
- Treat it like engineering: **reproducible results, versioned data, automated tests**, and clear documentation.
- Keep “strategy logic” separate from “broker/exchange plumbing” so you can swap parts later.

## Milestone 0: Set up the Git repo like a real product

**Goal:** You can both collaborate smoothly and track progress.

**Repo structure (simple, scalable)**

- `README.md` (what it does, how to run)
- `pyproject.toml` (or `requirements.txt`)
- `src/trading_platform/`
  - `data/` (fetch + storage interfaces)
  - `features/` (indicators, signals)
  - `strategy/` (strategies)
  - `backtest/` (engine)
  - `execution/` (paper broker, later real broker)
  - `risk/` (position sizing, limits)
  - `portfolio/` (positions, PnL)
  - `utils/` (logging, config)

- `tests/`
- `notebooks/` (optional, for exploration)
- `.github/workflows/ci.yml` (lint + tests)

**Team habits**

- Branch per feature, PRs, simple code review checklist
- Issues for tasks, labels like `good-first-issue`, `bug`, `enhancement`

## Milestone 1: Data pipeline that you trust

**Goal:** One command fetches data and stores it consistently.

Build:

- A `DataClient` interface (so you can switch providers later)
- A storage layer (CSV first, then SQLite/Parquet)
- Basic validation (no missing dates without explanation, no duplicates)

Deliverables:

- Script: `python -m trading_platform.data.fetch --symbol AAPL --start 2018-01-01`
- Unit tests: parsing dates, handling missing values

## Milestone 2: A backtesting engine (small but correct)

**Goal:** Given bars (OHLCV), a strategy, and cost assumptions, you can simulate trades.

Core components:

- **Event loop** over time (each bar triggers strategy evaluation)
- **Order model** (market order is enough to start)
- **Fill model** (assume next-bar open, add slippage + fees)
- **Portfolio accounting** (cash, positions, equity curve)

Deliverables:

- A backtest report: total return, max drawdown, Sharpe (basic versions are fine)
- Plot: equity curve + drawdowns
- Tests for “known scenario” where outcome is deterministic

## Milestone 3: Strategy API and a first strategy

**Goal:** Add strategies without touching the engine.

Define a strategy interface like:

- `on_bar(data_slice) -> desired_orders` or `signal -> execution`

Start with 1 to 2 classic baselines:

- Moving average crossover
- Mean reversion with z-score on returns

Deliverables:

- Strategies live in `strategy/`
- A config file (YAML/JSON) to run backtests with parameters

Teaching angle:

- Show him why baselines matter: “beat buy-and-hold after costs” is harder than it looks.

## Milestone 4: Research hygiene and avoiding common traps

**Goal:** Make results less likely to be accidentally misleading.

Add:

- Train/test split by time (walk-forward or rolling windows)
- Parameter search with strict separation (no peeking)
- Transaction costs always on
- Survivorship bias and lookahead bias checklist in the README

Deliverables:

- A notebook or script that runs a walk-forward evaluation
- A “strategy scorecard” output format that’s consistent across runs

## Milestone 5: Paper trading system (real-time loop, fake money)

**Goal:** Same code path as live trading, but orders go to a simulator.

Build:

- A scheduler loop (every minute/hour/day depending on strategy)
- A `PaperBroker` that accepts orders and simulates fills from live quotes/bars
- Logging + persistence (every decision and every order saved)

Must-haves:

- Position limits, max daily loss, kill switch
- Idempotency: if the program restarts, it doesn’t double-trade

Deliverables:

- Command: `python -m trading_platform.run --mode paper --strategy ma_cross --symbols SPY`
- Daily summary report (PnL, positions, trades)

## Milestone 6: Execution adapter for a real broker (only after the above)

**Goal:** Swap `PaperBroker` for `RealBroker` with minimal changes.

Build:

- Broker interface: `place_order`, `cancel_order`, `get_positions`, `get_cash`, `get_fills`
- Secrets management (env vars, never commit keys)
- Paper account first if the broker supports it

Deliverables:

- “Broker integration” module behind the interface
- Integration tests using sandbox endpoints if available

## Milestone 7: Operational maturity

**Goal:** It runs reliably and you can trust what it’s doing.

Add:

- Structured logs + alerts (email/Slack later)
- Dashboards (simple HTML report or a small web UI)
- Containerization (Docker) if you want portability
- Performance monitoring (latency, error rates)

## A good “definition of done” for each milestone

- Reproducible run command
- Tests pass in CI
- Short documentation update
- One plot or report artifact saved to `reports/`
