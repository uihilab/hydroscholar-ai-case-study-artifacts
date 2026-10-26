import os
import sys
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def date_chunks(start_date_str, end_date_str):
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    chunks = []
    current_start = start
    while current_start <= end:
        year_end = datetime(current_start.year, 12, 31)
        current_end = min(year_end, end)
        chunks.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
        current_start = current_end + timedelta(days=1)
    return chunks

def fetch_precipitation_data(token, station_id, start_date, end_date):
    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": token}
    all_results = []
    chunks = date_chunks(start_date, end_date)
    for chunk_start, chunk_end in chunks:
        logging.info(f"Fetching chunk: {chunk_start} to {chunk_end}")
        params = {
            "datasetid": "GHCND",
            "datatypeid": "PRCP",
            "stationid": station_id,
            "startdate": chunk_start,
            "enddate": chunk_end,
            "limit": 1000,
            "offset": 1
        }
        while True:
            logging.info(f"Requesting NOAA data: {chunk_start} to {chunk_end}, offset={params['offset']}")
            try:
                resp = requests.get(base_url, headers=headers, params=params, timeout=30)
                resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error(f"HTTP request failed for {chunk_start} to {chunk_end}, offset={params['offset']}: {e}")
                sys.exit(1)
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            all_results.extend(results)
            logging.info(f"Fetched {len(results)} records (total so far: {len(all_results)})")
            params["offset"] += params["limit"]
    logging.info(f"Completed fetching all chunks. Total records: {len(all_results)}")
    return all_results

def build_dataframe(records):
    logging.info("Building DataFrame from records")
    df = pd.DataFrame.from_records(records)
    if "date" not in df.columns or "value" not in df.columns:
        logging.error("Expected keys 'date' and 'value' not found in NOAA response records")
        sys.exit(1)
    df = df[["date", "value"]].rename(columns={"value": "precipitation_mm"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["precipitation_mm"] = pd.to_numeric(df["precipitation_mm"], errors="coerce") / 10.0
    df = df.dropna(subset=["date"])
    df = df.drop_duplicates(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    logging.info("Converted date to datetime.date and precipitation to mm")
    return df

def save_dataframe(df, out_path):
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(out_path, index=False)
    logging.info(f"Saved precipitation data to {out_path}")

def main():
    setup_logging()
    token = os.getenv("NOAA_TOKEN")
    if not token:
        logging.error("Environment variable NOAA_TOKEN not set")
        sys.exit(1)
    station_id = "GHCND:USW00013904"
    start_date = "2015-01-01"
    end_date = "2020-12-31"
    logging.info(f"Fetching precipitation for station {station_id} from {start_date} to {end_date}")
    records = fetch_precipitation_data(token, station_id, start_date, end_date)
    if not records:
        logging.error("No precipitation records retrieved; exiting")
        sys.exit(1)
    df = build_dataframe(records)
    out_path = os.path.join("data", "raw", "precip.csv")
    save_dataframe(df, out_path)

if __name__ == "__main__":
    main()