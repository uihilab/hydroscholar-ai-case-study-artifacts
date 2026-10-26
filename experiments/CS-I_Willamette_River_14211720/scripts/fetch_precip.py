#!/usr/bin/env python3
import os
import sys
import requests
import csv

API_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
STATION_ID = "GHCND:USW00024233"
DATASET_ID = "GHCND"
DATATYPE_ID = "PRCP"
START_DATE = "2023-01-01"
END_DATE = "2023-12-31"
LIMIT = 1000
OUTPUT_CSV = "data/raw_precip.csv"

def fetch_precipitation():
    token = os.getenv("NOAA_TOKEN")
    if not token:
        sys.exit("Error: NOAA_TOKEN environment variable not set")

    headers = {"token": token}
    params = {
        "datasetid": DATASET_ID,
        "stationid": STATION_ID,
        "datatypeid": DATATYPE_ID,
        "startdate": START_DATE,
        "enddate": END_DATE,
        "limit": LIMIT,
        "offset": 1
    }

    all_records = []
    while True:
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code != 200:
            sys.exit(f"Error fetching data: {response.status_code} {response.text}")

        data = response.json().get("results", [])
        if not data:
            break

        for rec in data:
            date = rec["date"][:10]
            # PRCP values are in tenths of mm, convert to mm
            precip_mm = rec["value"] / 10.0
            all_records.append((date, precip_mm))

        if len(data) < LIMIT:
            break
        params["offset"] += LIMIT

    return all_records

def save_to_csv(records, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "precip_mm"])
        for date, precip in records:
            writer.writerow([date, precip])

def main():
    records = fetch_precipitation()
    save_to_csv(records, OUTPUT_CSV)
    print(f"Saved {len(records)} records to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()