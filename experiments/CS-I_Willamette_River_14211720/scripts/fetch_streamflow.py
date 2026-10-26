#!/usr/bin/env python3
import os
import sys
import logging
import requests
import pandas as pd

def fetch_streamflow(site, start_date, end_date):
    """
    Fetch daily mean streamflow (cfs) from USGS Water Services API.
    """
    url = "https://waterservices.usgs.gov/nwis/dv/"
    params = {
        "format": "json",
        "sites": site,
        "startDT": start_date,
        "endDT": end_date,
        "parameterCd": "00060"  # Discharge
    }

    logging.info("Requesting data for site %s from %s to %s", site, start_date, end_date)
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error("Failed to fetch data: %s", e)
        sys.exit(1)

    try:
        data = resp.json()
    except ValueError as e:
        logging.error("Invalid JSON response: %s", e)
        sys.exit(1)

    # Navigate to the timeSeries values
    try:
        ts = data["value"]["timeSeries"]
        if not ts:
            raise KeyError("timeSeries is empty")
        values = ts[0]["values"][0]["value"]
    except (KeyError, IndexError) as e:
        logging.error("Unexpected JSON structure: %s", e)
        sys.exit(1)

    records = []
    for entry in values:
        date = entry.get("dateTime")
        raw_val = entry.get("value")
        try:
            flow = float(raw_val)
        except (TypeError, ValueError):
            flow = None
        records.append({
            "date": date,
            "streamflow_cfs": flow
        })

    df = pd.DataFrame.from_records(records)
    return df

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    site = "14211720"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    output_dir = "data"
    output_file = os.path.join(output_dir, "raw_streamflow.csv")

    df = fetch_streamflow(site, start_date, end_date)

    if df.empty:
        logging.warning("No data retrieved; dataframe is empty.")
        sys.exit(0)

    # Convert date column to datetime
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        logging.warning("Could not convert date column to datetime: %s", e)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        df.to_csv(output_file, index=False)
        logging.info("Saved %d records to %s", len(df), output_file)
    except Exception as e:
        logging.error("Failed to save CSV: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()