import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def format_results_table(df):
    """
    Formats a strategy performance DataFrame for better readability.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing performance metrics.

    Returns
    -------
    Styler
        Formatted pandas Styler object for display in notebooks.
    """

    return df.style.format({
        "CAGR": "{:.2%}",
        "Annualized_Volatility": "{:.2%}",
        "Calmar_Ratio": "{:.2f}", 
        "Sharpe_Ratio": "{:.2f}",
        "Max_Drawdown": "{:.2%}"
    })
    

def plot_equity_drawdown_grid(equity_curves):
    """
    Plots equity curves and drawdowns for 4 strategies in a 2x2 grid.

    Parameters
    ----------
    equity_curves : dict
        Dictionary of DataFrames, each containing:
        - 'equity'
        - 'drawdown'
        indexed by strategy name

    Returns
    -------
    None
        Displays matplotlib figure.
    """

    # Select strategies to plot
    selected_strategies = list(equity_curves.keys())[:4]

    # Create 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    # Loop over strategies
    for i, strategy in enumerate(selected_strategies):

        df_plot = equity_curves[strategy]
        ax = axes[i]

        # EQUITY CURVE
        ax.plot(df_plot["equity"], label="Equity", color="blue")
        ax.set_xlabel("Time")
        ax.set_ylabel("Equity")

        # DRAWDOWN
        ax2 = ax.twinx()

        ax2.fill_between(
            df_plot.index,
            df_plot["drawdown"],
            0,
            color="red",
            alpha=0.3,
            label="Drawdown"
        )

        # Format drawdown as percentage
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
        ax2.set_ylabel("Drawdown")

        # Title
        ax.set_title(f"Strategy {strategy}")

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # Improve layout spacing
    plt.tight_layout()
    plt.show()

def plot_heatmap(results_df, metric="Sharpe_Ratio"):
    """
    Plot a heatmap for a selected metric using entry/exit hours.
    
    Parameters
    ----------
    results_df : pd.DataFrame
        DataFrame containing the columns:
        - "entry_hour"
        - "exit_hour"
        - the metric column to plot
    
    metric : str
        Name of the column to visualize
        (example: "Sharpe_Ratio" or "Max_Drawdown")
    """

    # Create pivot table:
    # rows = entry hours
    # columns = exit hours
    # values = selected metric
    heatmap = results_df.pivot(
        index="entry_hour",
        columns="exit_hour",
        values=metric
    )

    # Create figure    
    plt.figure(figsize=(8, 6))

    # Plot heatmap matrix
    im = plt.imshow(
        heatmap,
        aspect="auto",
        origin="lower",
    )

    # Title and axis labels
    plt.title(metric)
    plt.xlabel("Exit Hour")
    plt.ylabel("Entry Hour")

    # Set axis ticks to match actual hour values
    plt.xticks(range(len(heatmap.columns)), heatmap.columns)
    plt.yticks(range(len(heatmap.index)), heatmap.index)

    # Add colorbar to interpret values
    plt.colorbar(im)

    # Improve layout spacing
    plt.tight_layout()
    plt.show()