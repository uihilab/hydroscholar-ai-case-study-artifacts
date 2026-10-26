import os
import requests
import pandas as pd

def fetch_usgs_streamflow():
    url = "https://waterservices.usgs.gov/nwis/dv/"
    params = {
        "format": "json",
        "sites": "01010000,01014000",
        "startDT": "2015-01-01",
        "endDT": "2020-12-31",
        "parameterCd": "00060"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    records = []
    time_series = data.get("value", {}).get("timeSeries", [])
    for ts in time_series:
        site_code = ts.get("sourceInfo", {}).get("siteCode", [{}])[0].get("value")
        values = ts.get("values", [])
        if not values:
            continue
        for entry in values[0].get("value", []):
            date = entry.get("dateTime")
            discharge_str = entry.get("value")
            try:
                discharge = float(discharge_str)
            except (TypeError, ValueError):
                discharge = None
            records.append({
                "date": date,
                "site_code": site_code,
                "discharge_cfs": discharge
            })
    return records

def main():
    records = fetch_usgs_streamflow()
    df = pd.DataFrame(records, columns=["date", "site_code", "discharge_cfs"])
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "raw_usgs_streamflow.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} records to {output_path}")

if __name__ == "__main__":
    main()