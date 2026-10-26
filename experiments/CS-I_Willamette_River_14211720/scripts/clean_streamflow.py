#!/usr/bin/env python3
import pandas as pd

def main():
    input_file = 'data/raw_streamflow.csv'
    output_file = 'data/clean_streamflow.csv'
    
    df = pd.read_csv(input_file, parse_dates=['date'])
    df.rename(columns={'discharge': 'streamflow_cfs'}, inplace=True)
    df.dropna(inplace=True)
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    main()