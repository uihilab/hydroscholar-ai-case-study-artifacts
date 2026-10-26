import pandas as pd

def main():
    # Load raw data, parse the lowercase 'date' column as datetime
    df = pd.read_csv('data/raw_usgs_streamflow.csv', parse_dates=['date'])
    
    # Pivot so 'date' is the index and each site_code becomes a column
    df_pivot = df.pivot(index='date', columns='site_code', values='discharge_cfs')
    
    # Rename the site_code columns
    df_pivot.rename(columns={
        1010000: 'Flow_Upstream',
        1014000: 'Flow_Downstream'
    }, inplace=True)
    
    # Ensure flow values are floats
    df_pivot = df_pivot.astype(float)
    
    # Sort by date and interpolate missing values linearly
    df_pivot.sort_index(inplace=True)
    df_pivot.interpolate(method='linear', inplace=True)
    
    # Save cleaned and pivoted data
    df_pivot.to_csv('data/clean_pivoted_flow.csv', index=True)

if __name__ == "__main__":
    main()