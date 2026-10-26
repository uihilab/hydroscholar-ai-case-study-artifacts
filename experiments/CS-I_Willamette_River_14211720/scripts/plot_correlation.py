import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path
import json

def main():
    # Paths
    data_path = Path("data/merged_hydro.csv")
    results_dir = Path("results")
    plots_dir = Path("plots")
    print(f"Ensuring directories exist: {results_dir}, {plots_dir}")
    results_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"Loading data from {data_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found at {data_path}")
    header_cols = pd.read_csv(data_path, nrows=0).columns.tolist()
    if "date" in header_cols:
        print("Detected 'date' column. Parsing dates.")
        df = pd.read_csv(data_path, parse_dates=["date"])
        df.set_index("date", inplace=True)
    else:
        print("No 'date' column found. Loading without date parsing.")
        df = pd.read_csv(data_path)
    print(f"Data loaded. Shape: {df.shape}")

    # Select two numeric columns for analysis
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"Numeric columns found for analysis: {num_cols}")
    if len(num_cols) < 2:
        raise ValueError("Need at least two numeric columns in the data for correlation and plotting.")
    x_col, y_col = num_cols[0], num_cols[1]
    print(f"Using columns '{x_col}' and '{y_col}' for analysis")

    x = df[x_col].dropna()
    y = df[y_col].dropna()
    common_idx = x.index.intersection(y.index)
    x = x.loc[common_idx]
    y = y.loc[common_idx]
    print(f"Aligned data length: {len(x)}")

    # Compute correlations
    print("Computing Pearson and Spearman correlations")
    pearson_corr, pearson_p = stats.pearsonr(x, y)
    spearman_corr, spearman_p = stats.spearmanr(x, y)
    print(f"Pearson r={pearson_corr:.4f}, p-value={pearson_p:.4g}")
    print(f"Spearman rho={spearman_corr:.4f}, p-value={spearman_p:.4g}")

    metrics = {
        "pearson": {
            "correlation": float(pearson_corr),
            "p_value": float(pearson_p)
        },
        "spearman": {
            "correlation": float(spearman_corr),
            "p_value": float(spearman_p)
        },
        "x_column": x_col,
        "y_column": y_col
    }

    # Save metrics to JSON
    metrics_path = results_dir / "corr_metrics.json"
    print(f"Saving correlation metrics to {metrics_path}")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    # Scatter plot with regression line
    print("Creating scatter plot with regression line")
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, s=40, alpha=0.6, label="Data")
    x_vals = np.array([x.min(), x.max()])
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, color="red", label="Fit")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"Scatter Plot with Regression Line\nPearson r={pearson_corr:.2f}, Spearman ρ={spearman_corr:.2f}")
    plt.legend()
    plt.tight_layout()
    scatter_path = plots_dir / "scatter.png"
    plt.savefig(scatter_path, dpi=300)
    plt.close()
    print(f"Scatter plot saved to {scatter_path}")

    # Dual-axis time series plot
    print("Creating dual-axis time series plot")
    if df.index.dtype.kind in ("M", "M8"):
        idx = df.index
        xlabel = "Time"
    else:
        idx = np.arange(len(df))
        xlabel = "Index"
    fig, ax1 = plt.subplots(figsize=(10, 6))
    color1 = "tab:blue"
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(x_col, color=color1)
    ax1.plot(idx, df[x_col], color=color1, label=x_col)
    ax1.tick_params(axis="y", labelcolor=color1)

    ax2 = ax1.twinx()
    color2 = "tab:red"
    ax2.set_ylabel(y_col, color=color2)
    ax2.plot(idx, df[y_col], color=color2, label=y_col)
    ax2.tick_params(axis="y", labelcolor=color2)

    plt.title("Dual-axis Time Series Plot")
    fig.tight_layout()
    ts_path = plots_dir / "time_series.png"
    plt.savefig(ts_path, dpi=300)
    plt.close()
    print(f"Time series plot saved to {ts_path}")

    print("All tasks completed successfully.")

if __name__ == "__main__":
    main()