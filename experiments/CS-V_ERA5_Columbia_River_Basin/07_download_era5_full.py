#!/usr/bin/env python3

import sys
from pathlib import Path

import cdsapi

def main():
    years = [2021, 2022, 2023]
    base_dir = Path("data")
    base_dir.mkdir(parents=True, exist_ok=True)

    # Define request parameters
    dataset = "reanalysis-era5-single-levels"
    variables = ["total_precipitation", "2m_temperature"]
    product_type = "reanalysis"
    area = [49.0, -124.5, 42.0, -116.0]  # north, west, south, east
    months = [f"{m:02d}" for m in range(1, 13)]
    days = [f"{d:02d}" for d in range(1, 32)]
    hours = [f"{h:02d}:00" for h in range(0, 24)]

    for year in years:
        output_file = base_dir / f"era5_{year}_hourly.nc"
        if output_file.exists():
            print(f"[SKIP] {output_file} already exists.")
            continue

        print(f"[DOWNLOAD] Starting download for year {year} -> {output_file}")
        try:
            client = cdsapi.Client(
                url="https://cds.climate.copernicus.eu/api",
                key="<REDACTED_CDS_API_KEY>"
            )
        except Exception as e:
            print(f"[ERROR] Failed to instantiate CDS API client: {e}", file=sys.stderr)
            sys.exit(1)

        request = {
            "format": "netcdf",
            "product_type": product_type,
            "variable": variables,
            "year": str(year),
            "month": months,
            "day": days,
            "time": hours,
            "area": area,
        }

        try:
            client.retrieve(dataset, request, str(output_file))
            print(f"[DONE] Downloaded data for {year} to {output_file}")
        except Exception as e:
            print(f"[ERROR] Download failed for year {year}: {e}", file=sys.stderr)
            if output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    pass
            sys.exit(1)

if __name__ == "__main__":
    main()