#!/usr/bin/env python3
import pandas as pd

def main():
    # Load cleaned precipitation and streamflow data
    precip = pd.read_csv('data/clean_precip.csv')
    streamflow = pd.read_csv('data/clean_streamflow.csv')

    # Merge on 'date' using an inner join
    merged = precip.merge(streamflow, on='date', how='inner')

    # Save the merged DataFrame
    merged.to_csv('data/merged_hydro.csv', index=False)

if __name__ == '__main__':
    main()