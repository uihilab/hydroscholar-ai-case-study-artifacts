import cdsapi
import logging
from pathlib import Path
import sys

# Instantiate CDS API client directly with provided URL and key
client = cdsapi.Client(
    url='https://cds.climate.copernicus.eu/api',
    key='<REDACTED_CDS_API_KEY>'
)

# Setup logging
tools = Path(__file__).name
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(tools)

def main():
    # Ensure data directory exists
    data_dir = Path("data")
    logger.info(f"Ensuring data directory exists at '{data_dir}'")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Define request parameters
    variables = ["total_precipitation", "2m_temperature"]
    days = [f"{d:02d}" for d in range(1, 32)]
    times = [f"{h:02d}:00" for h in range(24)]
    area = [49.0, -124.5, 42.0, -116.0]  # north, west, south, east

    out_file = data_dir / "era5_jan1980_hourly.nc"
    logger.info(
        f"Requesting ERA5 data for Jan 1980: variables={variables}, "
        f"days=1-31, times=00-23, area={area}"
    )

    try:
        client.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "data_format": "netcdf",               # updated key
                "variable": variables,                   # full names
                "year": "1980",
                "month": "01",
                "day": days,
                "time": times,
                "area": area,
            },
            str(out_file),
        )
        logger.info(f"ERA5 data successfully downloaded to {out_file}")
    except Exception as e:
        logger.error(f"Failed to download ERA5 data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()