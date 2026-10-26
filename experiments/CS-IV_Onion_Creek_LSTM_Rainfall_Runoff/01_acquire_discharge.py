import os
import sys
import logging
import requests
import pandas as pd

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    url = 'https://waterservices.usgs.gov/nwis/dv/'
    params = {
        'site': '08158000',
        'parameterCd': '00060',
        'startDT': '2015-01-01',
        'endDT': '2020-12-31',
        'format': 'json'
    }

    try:
        logging.info('Requesting data from USGS API...')
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f'HTTP request failed: {e}')
        sys.exit(1)

    try:
        data = response.json()
    except ValueError as e:
        logging.error(f'Failed to parse JSON: {e}')
        sys.exit(1)

    try:
        time_series = data['value']['timeSeries']
        if not time_series:
            logging.error('No time series data found in response.')
            sys.exit(1)
        values = time_series[0]['values'][0]['value']
        records = [{'date': v['dateTime'], 'discharge_cfs': v['value']} for v in values]
    except (KeyError, IndexError, TypeError) as e:
        logging.error(f'Error extracting data: {e}')
        sys.exit(1)

    df = pd.DataFrame.from_records(records)
    df['date'] = pd.to_datetime(df['date'])
    df['discharge_cfs'] = pd.to_numeric(df['discharge_cfs'], errors='coerce')

    output_dir = os.path.join('data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'discharge.csv')

    try:
        df.to_csv(output_path, index=False)
        logging.info(f'Data saved to {output_path}')
    except Exception as e:
        logging.error(f'Failed to save CSV: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()