#!/usr/bin/env python3

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import json
from pathlib import Path
import sys

def main():
    try:
        print("Loading data...")
        # Paths
        sat_path = Path("data/processed_inventory.csv")
        gauge_path = Path("data/gauge_levels.csv")
        plot_path = Path("data/correlation_plot.png")
        report_path = Path("data/final_report.json")
        # Ensure data directory exists
        plot_path.parent.mkdir(parents=True, exist_ok=True)

        # Load and parse dates
        df_sat = pd.read_csv(sat_path, parse_dates=["date"])
        df_gauge = pd.read_csv(gauge_path, parse_dates=["date"])

        print("Merging datasets on nearest date...")
        # Sort by date
        df_sat = df_sat.sort_values("date")
        df_gauge = df_gauge.sort_values("date")
        # Merge asof on date
        df = pd.merge_asof(
            df_sat,
            df_gauge,
            on="date",
            direction="nearest"
        )

        # Drop rows with missing values
        df_clean = df.dropna(subset=["surface_area_sqkm", "discharge_cfs"])
        if df_clean.empty:
            print("No overlapping data to compute correlation. Exiting.")
            sys.exit(0)

        x = df_clean["discharge_cfs"].values
        y = df_clean["surface_area_sqkm"].values

        print("Calculating Pearson correlation...")
        corr_coef, p_value = pearsonr(x, y)

        print("Fitting linear regression...")
        slope, intercept = np.polyfit(x, y, 1)

        print("Generating scatter plot with regression line...")
        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, color="blue", label="Data points", alpha=0.7)
        # Regression line
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        plt.plot(x_line, y_line, color="red", label=f"Fit: y={slope:.3f}x+{intercept:.3f}")
        plt.xlabel("Discharge (cfs)")
        plt.ylabel("Surface Area (sq km)")
        plt.title("Surface Water Area vs. Discharge")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved to '{plot_path}'")

        print("Determining confidence flag...")
        confidence_flag = (
            "High Confidence" if abs(corr_coef) >= 0.8 else "Low Confidence"
        )

        print("Writing final report...")
        report = {
            "correlation_coefficient": corr_coef,
            "p_value": p_value,
            "slope": slope,
            "intercept": intercept,
            "confidence_flag": confidence_flag
        }
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to '{report_path}'")
        print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()