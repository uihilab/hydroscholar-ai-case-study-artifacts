#!/usr/bin/env python3

import sys
import subprocess
import importlib
import logging
from pathlib import Path

# Ensure required packages are installed
required_packages = {
    "dataretrieval": "dataretrieval",
    "pandas": "pandas"
}

for module_name, pip_name in required_packages.items():
    try:
        importlib.import_module(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

import pandas as pd
from dataretrieval import nwis

# Configuration
SITE_ID = "11407000"            # USGS site for discharge
PARAMETER_CD = "00060"          # 00060 = Discharge
START_DATE = "2022-10-01"
END_DATE = "2023-06-01"
OUTPUT_CSV = Path("data/gauge_levels.csv")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def fetch_discharge(site_id, parameter_cd, start, end):
    """
    Fetch daily discharge (dv) for a single parameter.
    """
    logger.info(f"Fetching daily mean discharge for site {site_id}, parameter {parameter_cd}, "
                f"from {start} to {end}")
    try:
        df = nwis.get_record(
            sites=site_id,
            service="dv",
            start=start,
            end=end,
            parameterCd=parameter_cd
        )
        return df
    except Exception as e:
        logger.error(f"Failed to fetch discharge data: {e}")
        sys.exit(1)

def clean_discharge(df, parameter_cd):
    """
    Clean the discharge DataFrame:
    - Reset index to make dates a column
    - Rename columns to ['date', 'discharge_cfs']
    - Parse dates, drop missing values
    """
    if df.empty:
        logger.warning("No discharge data returned.")
        return df

    df = df.reset_index()

    # Rename datetime/index column to 'date'
    if "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})
    elif "index" in df.columns:
        df = df.rename(columns={"index": "date"})
    else:
        logger.warning("Could not find datetime/index column; proceeding without rename.")

    mean_col = f"{parameter_cd}_Mean"
    if mean_col not in df.columns:
        logger.error(f"Expected column '{mean_col}' not found in data.")
        sys.exit(1)

    df = df.rename(columns={mean_col: "discharge_cfs"})
    df = df[["date", "discharge_cfs"]]

    # Parse dates and format
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    # Drop rows where discharge is missing
    before = len(df)
    df = df.dropna(subset=["discharge_cfs"])
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with missing discharge values")

    return df

def save_to_csv(df, output_path):
    """
    Save the cleaned discharge data to CSV.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Discharge data saved to '{output_path}'")

def main():
    df_raw = fetch_discharge(SITE_ID, PARAMETER_CD, START_DATE, END_DATE)
    df_clean = clean_discharge(df_raw, PARAMETER_CD)
    if not df_clean.empty:
        save_to_csv(df_clean, OUTPUT_CSV)
    else:
        logger.warning("No data to save after cleaning.")

if __name__ == "__main__":
    main()