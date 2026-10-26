#!/usr/bin/env python3
import argparse
import pandas as pd
from scipy.stats import pearsonr, spearmanr

def calc_pearson_correlation(precip, streamflow):
    """
    Calculate Pearson correlation coefficient and p-value
    between two arrays.
    Returns:
        tuple: (correlation_coefficient, p_value)
    """
    corr, pvalue = pearsonr(precip, streamflow)
    return corr, pvalue

def calc_spearman_correlation(precip, streamflow):
    """
    Calculate Spearman rank-order correlation coefficient and p-value
    between two arrays.
    Returns:
        tuple: (correlation_coefficient, p_value)
    """
    corr, pvalue = spearmanr(precip, streamflow)
    return corr, pvalue

def main():
    parser = argparse.ArgumentParser(
        description="Calculate Pearson and Spearman correlations between "
                    "'precip_mm' and 'streamflow_cfs' in a CSV file."
    )
    parser.add_argument(
        "-i", "--input",
        default="data/merged_hydro.csv",
        help="Path to the input CSV file (default: data/merged_hydro.csv)"
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    if 'precip_mm' not in df.columns or 'streamflow_cfs' not in df.columns:
        raise KeyError("Input CSV must contain 'precip_mm' and 'streamflow_cfs' columns.")

    precip = df['precip_mm']
    streamflow = df['streamflow_cfs']

    pearson_corr, pearson_p = calc_pearson_correlation(precip, streamflow)
    spearman_corr, spearman_p = calc_spearman_correlation(precip, streamflow)

    print("Pearson Correlation:")
    print(f"  correlation = {pearson_corr:.4f}")
    print(f"  p-value     = {pearson_p:.4g}\n")

    print("Spearman Correlation:")
    print(f"  correlation = {spearman_corr:.4f}")
    print(f"  p-value     = {spearman_p:.4g}")

if __name__ == "__main__":
    main()