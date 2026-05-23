# Intraday Seasonality Analysis — EUR/USD (H1)

## Overview

This project explores whether a **systematic intraday bias** exists in the EUR/USD market using historical H1 data from 2018 to April 2026.

The core idea is simple:  
> do certain hours of the day consistently offer better long/short opportunities than others?

To answer this, we perform a full pipeline that includes:

- Intraday seasonality analysis
- Systematic grid search over entry/exit hour combinations
- In-sample strategy selection based on risk-adjusted performance
- Out-of-sample validation
- Realistic execution backtesting including transaction costs

---

## Key Result

A persistent intraday pattern appears to exist in-sample and remains partially present out-of-sample.

However, once realistic trading frictions are included (spread, commissions, slippage), the edge largely disappears.

This highlights an important conclusion:

> **intraday statistical patterns do not automatically translate into tradable strategies**

---

## Important Context (Read This)

This project is intentionally designed as a **simplified research prototype**, not a production-ready trading system.

The goal is to test whether a basic time-based market inefficiency exists, not to build a fully deployable strategy.

As such, the framework is deliberately minimal and has several structural limitations:

- The signal is **purely time-based** (fixed entry and exit hours)
- No market regime detection is used
- No volatility filtering is applied
- No trend or mean-reversion confirmation signals are included
- No position sizing model is implemented
- No portfolio or capital allocation logic is considered
- No adaptive or dynamic risk management is present

Because of this, the resulting strategies should be interpreted as:

> **a first-order exploration of intraday effects, not a complete trading system**

---

## Why the Strategies Fail After Costs

The deterioration of performance in realistic conditions is expected and driven by multiple factors:

- Excessive number of trades due to naive time-based signals  
- Low average trade size on EUR/USD H1  
- Transaction costs (spread, commissions, slippage) fully eroding edge  
- Strategy selection based only on Sharpe ratio (not multi-objective optimization)

---

## What This Project Demonstrates

Despite its simplicity, the project shows that:

- Intraday structure in FX markets may exist statistically  
- Patterns can survive out-of-sample under ideal conditions  
- However, **robust profitability requires additional layers of modeling**

---

## Potential Improvements

To move from a research prototype to a tradable system, the following extensions would be necessary:

- Volatility-based trade filtering  
- Market regime classification (risk-on / risk-off, trending vs mean-reverting)  
- Simple technical confirmation signals  
- Stop-loss and take-profit mechanisms  
- Position sizing based on volatility or risk budget  
- Multi-metric strategy selection (not only Sharpe ratio)

---

## Repository Structure

- `data/` — Historical EUR/USD H1 dataset  
- `src/` — Core backtesting engine and metrics  
- `notebooks/` — Research workflow and analysis steps:
  - Intraday seasonality exploration
  - Parameter search (grid search)
  - In-sample evaluation
  - Out-of-sample validation
  - Realistic execution with costs  

---

## Final Note

This project should be seen as a **research-driven demonstration of systematic trading thinking**, showing the full pipeline from hypothesis generation to robustness testing and realistic evaluation.

The main takeaway is not the strategy itself, but the process:

> from apparent statistical edge → to validation → to realistic failure under execution constraints