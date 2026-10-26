import pandas as pd

def main():
    # Load the raw precipitation data, parsing the 'date' column as datetime
    df = pd.read_csv('data/raw_precip.csv', parse_dates=['date'])

    # Rename the precipitation column to 'precip_mm'
    df = df.rename(columns={'precipitation': 'precip_mm'})

    # Drop rows with any missing values
    df = df.dropna()

    # Save the cleaned data
    df.to_csv('data/clean_precip.csv', index=False)

if __name__ == '__main__':
    main()