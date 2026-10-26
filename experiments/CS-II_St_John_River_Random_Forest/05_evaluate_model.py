#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_nse(observed, simulated):
    """
    Compute Nash–Sutcliffe Efficiency (NSE).
    """
    obs = np.array(observed)
    sim = np.array(simulated)
    numerator = np.sum((obs - sim) ** 2)
    denominator = np.sum((obs - np.mean(obs)) ** 2)
    return 1 - (numerator / denominator)

def calculate_rmse(observed, simulated):
    """
    Compute Root Mean Squared Error (RMSE).
    """
    obs = np.array(observed)
    sim = np.array(simulated)
    return np.sqrt(np.mean((obs - sim) ** 2))

def main():
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)

    # Load predictions with proper date parsing and indexing
    preds_path = os.path.join("outputs", "test_predictions.csv")
    df = pd.read_csv(preds_path, parse_dates=['date'], index_col='date')

    # Extract actual and predicted series using lowercase column names
    actual = df['actual']
    predicted = df['predicted']

    # Compute metrics
    nse_value = calculate_nse(actual, predicted)
    rmse_value = calculate_rmse(actual, predicted)

    # Create figure with two subplots
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    # 1) Scatter plot of Predicted vs Actual
    ax0 = axes[0]
    ax0.scatter(actual, predicted, alpha=0.7)
    min_val = min(actual.min(), predicted.min())
    max_val = max(actual.max(), predicted.max())
    ax0.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1)
    ax0.set_xlabel("Actual")
    ax0.set_ylabel("Predicted")
    ax0.set_title("Predicted vs Actual")

    # 2) Hydrograph overlay
    ax1 = axes[1]
    ax1.plot(df.index, actual, label="Actual", linewidth=1.5)
    ax1.plot(df.index, predicted, label="Predicted", linewidth=1.5)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Flow")
    ax1.set_title("Hydrograph: Actual vs Predicted")
    ax1.legend()

    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "hydrograph_eval.png"))

    # Write metrics to file
    metrics_path = os.path.join("outputs", "metrics.txt")
    with open(metrics_path, "w") as f:
        f.write(f"NSE: {nse_value:.4f}\n")
        f.write(f"RMSE: {rmse_value:.4f}\n")

    # Print NSE to console
    print(f"NSE: {nse_value:.4f}")

if __name__ == "__main__":
    main()