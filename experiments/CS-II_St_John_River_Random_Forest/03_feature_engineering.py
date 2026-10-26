#!/usr/bin/env python3
import pandas as pd

def main():
    # Load the cleaned pivoted flow data
    df = pd.read_csv(
        "data/clean_pivoted_flow.csv",
        parse_dates=["date"],
        index_col="date"
    )

    # Ensure correct chronological order
    df.sort_index(inplace=True)

    # Ensure the upstream flow column is float
    df["Flow_Upstream"] = df["Flow_Upstream"].astype(float)

    # Create lagged features for the upstream gauge (t-1, t-2, t-3)
    df["Upstream_Lag1"] = df["Flow_Upstream"].shift(1)
    df["Upstream_Lag2"] = df["Flow_Upstream"].shift(2)
    df["Upstream_Lag3"] = df["Flow_Upstream"].shift(3)

    # Drop rows with NaN values resulting from lagging
    df.dropna(inplace=True)

    # Remove the index name so it's not written to CSV
    df.index.name = None

    # Save the ML-ready dataset
    df.to_csv("data/ml_ready_features.csv", index=True)

if __name__ == "__main__":
    main()