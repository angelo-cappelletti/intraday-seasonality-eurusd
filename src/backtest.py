import pandas as pd
import numpy as np

def run_backtest(data, fee=0.0):
    """
    Run backtest on trading signals, including transaction costs.

    Parameters
    ----------
    data : pd.DataFrame
    
        DataFrame indexed by datetime containing:
            'price' column: asset price series
            'position' column: market exposure

            Examples:
            1   -> long exposure
            0   -> flat
            -1  -> short exposure
        
        The function assumes that the position vector is already precomputed and
        aligned with the price series.

    fee : float, optional
        Transaction cost per trade expressed as a decimal.

        Examples:
        0.001  -> 0.1% per trade
        0.0005 -> 0.05% per trade

        The commission is applied every time the position changes.

    Returns
    -------
    pd.DataFrame
        Original dataframe enriched with:
        returns, trades, costs, pnl, equity, drawdown.
    """

    df = data.copy()

    # Compute asset returns
    df["returns"] = df["price"].pct_change().fillna(0)

    # Detect trades (position changes)
    df["trades"] = df["position"].diff().abs().fillna(0)

    # Compute transaction costs
    df["costs"] = df["trades"] * fee

    # Compute strategy profit and loss after costs.
    #
    # Positions are assumed to be entered immediately after the close of the
    # previous H1 candle (i.e. at the timestamp corresponding to the signal).
    #
    # Therefore, the current position is matched with the current bar return
    # without requiring a position shift.
    df["pnl"] = (df["position"] * df["returns"]) - df["costs"]

    # Compute cumulative equity curve
    df["equity"] = (1 + df["pnl"]).cumprod()

    # Compute drawdown from peak
    df["drawdown"] = (df["equity"] / df["equity"].cummax()) - 1

    return df


def compute_metrics(df):
    """
    Compute performance metrics from hourly (H1) backtest results with appropriate annualization

    Parameters
    ----------
    df : pd.DataFrame
        Backtest output containing at least:
        - pnl
        - equity
        - drawdown

    Returns
    -------
    dict
        Dictionary of performance metrics.
    """

    periods_per_year = 252 * 24
    
    # Returns series
    returns = df["pnl"]
    
    # Annualized return
    total_return = df["equity"].iloc[-1] - 1
    cagr = (1 + total_return) ** (periods_per_year / len(df)) - 1
    annualized_mean_return = returns.mean() * periods_per_year
    
    # Annualized volatility
    volatility = returns.std() * np.sqrt(periods_per_year)
    
    # Max drawdown
    max_drawdown = df["drawdown"].min()
    
    # Calmar ratio
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

    # Annualized Sharpe ratio assuming a 0% risk-free rate
    sharpe = annualized_mean_return / volatility if volatility != 0 else 0

    metrics = {
        "CAGR": cagr,
        "Annualized_Volatility": volatility,
        "Max_Drawdown": max_drawdown,
        "Sharpe_Ratio": sharpe,
        "Calmar_Ratio": calmar
    }

    return metrics

def generate_position(
    df,
    entry_long_hour=None,
    exit_long_hour=None,
    entry_short_hour=None,
    exit_short_hour=None
):
    """
    Generate intraday long/short positions.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'hour' column.

    entry_long_hour : int or None
        Long entry hour.

    exit_long_hour : int or None
        Long exit hour.

    entry_short_hour : int or None
        Short entry hour.

    exit_short_hour : int or None
        Short exit hour.

    Returns
    -------
    pd.DataFrame
        DataFrame with 'position' column.
    """

    df = df.copy()

    # flat by default
    df["position"] = 0

    # ===== LONG WINDOW =====
    if entry_long_hour is not None and exit_long_hour is not None:

        if entry_long_hour < exit_long_hour:
            long_mask = (
                (df["hour"] >= entry_long_hour) &
                (df["hour"] < exit_long_hour)
            )

        else:
            long_mask = (
                (df["hour"] >= entry_long_hour) |
                (df["hour"] < exit_long_hour)
            )

        df.loc[long_mask, "position"] = 1

    # ===== SHORT WINDOW =====
    if entry_short_hour is not None and exit_short_hour is not None:

        if entry_short_hour < exit_short_hour:
            short_mask = (
                (df["hour"] >= entry_short_hour) &
                (df["hour"] < exit_short_hour)
            )

        else:
            short_mask = (
                (df["hour"] >= entry_short_hour) |
                (df["hour"] < exit_short_hour)
            )

        df.loc[short_mask, "position"] = -1

    return df

def backtest_strategies(df, strategies, fee=0.0):
    """
    Runs multiple trading strategies using predefined pipeline functions:
    - generate_position
    - run_backtest
    - compute_metrics

    Parameters
    ----------
    df : pd.DataFrame
        Market data used to generate trading signals.

    strategies : list of dict
        Each strategy must contain:
        {
            "entry_hour": int,
            "exit_hour": int
        }
        
    commission : float, optional
        Transaction cost parameter passed to the backtest engine.

        The same cost assumption is applied consistently across all strategies

    Returns
    -------
    results_df : pd.DataFrame
        Performance metrics for each strategy (indexed by strategy name)

    equity_curves : dict
        Dictionary of DataFrames, each containing the equity curve and drawdown series for a single strategy
    """

    results = []
    equity_curves = {}

    # Loop over all strategy configurations
    for strat in strategies:

        # Extract strategy parameters
        entry_hour = strat["entry_hour"]
        exit_hour = strat["exit_hour"]

        # Generate trading signals
        df_sig = generate_position(
            df,
            entry_long_hour=entry_hour,
            exit_long_hour=exit_hour
        )

        # Run backtest simulation
        df_bt = run_backtest(df_sig, fee)

        # Compute performance metrics
        metrics = compute_metrics(df_bt)

        # Create a human-readable strategy identifier
        strategy_name = f"{entry_hour}-{exit_hour}"

        # Store computed metrics along with hour columns
        results.append({
            "strategy": strategy_name,
            "entry_hour": entry_hour,
            "exit_hour": exit_hour,
            **metrics
        })

        equity_curves[strategy_name] = df_bt[
            [ "equity", "drawdown"]
        ].copy()

    # Convert results list into DataFrame
    results_df = pd.DataFrame(results).set_index("strategy")

    return results_df, equity_curves