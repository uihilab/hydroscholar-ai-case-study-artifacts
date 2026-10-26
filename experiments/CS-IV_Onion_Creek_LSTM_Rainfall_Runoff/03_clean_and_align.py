import os
import pandas as pd

def main():
    # 1. Load raw data
    discharge = pd.read_csv('data/raw/discharge.csv', parse_dates=['date'])
    precip = pd.read_csv('data/raw/precip.csv', parse_dates=['date'])

    # 2. Set date as index
    discharge = discharge.set_index('date')
    precip = precip.set_index('date')

    # 3. Create continuous daily date index
    full_idx = pd.date_range(start='2015-01-01', end='2020-12-31', freq='D')

    # 4. Reindex and merge
    discharge = discharge.reindex(full_idx)
    precip = precip.reindex(full_idx)
    discharge.index.name = 'date'
    precip.index.name = 'date'
    df = precip.join(discharge, how='outer')

    # 5. Fill or interpolate missing values
    # Linear interpolate based on time index
    df['precipitation_mm'] = df['precipitation_mm'].interpolate(method='time')
    df['discharge_cfs']    = df['discharge_cfs'].interpolate(method='time')
    # Fill any remaining precip gaps with 0, discharge with nearest values
    df['precipitation_mm'] = df['precipitation_mm'].fillna(0)
    df['discharge_cfs']    = df['discharge_cfs'].fillna(method='ffill').fillna(method='bfill')

    # 6. Save cleaned data
    df = df.reset_index()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    os.makedirs('data/clean', exist_ok=True)
    df.to_csv(
        'data/clean/cleaned_data.csv',
        index=False,
        columns=['date', 'precipitation_mm', 'discharge_cfs']
    )

if __name__ == '__main__':
    main()