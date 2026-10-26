#!/usr/bin/env python3

import sys
import subprocess
import importlib
import logging
import os
import csv
import datetime
from pathlib import Path

# Ensure required packages are installed
required_packages = {
    "pystac_client": "pystac-client",
    "planetary_computer": "planetary-computer",
    "requests": "requests"
}

for module_name, pip_name in required_packages.items():
    try:
        importlib.import_module(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

import requests
from pystac_client import Client
import planetary_computer

# Configuration
API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION_ID = "sentinel-2-l2a"
BBOX = [-121.15, 39.50, -121.05, 39.60]
START_DATE = datetime.date(2023, 1, 1)
END_DATE = datetime.date(2023, 6, 1)
MAX_CLOUD = 10  # percent
DATA_DIR = Path("data/satellite")
INVENTORY_CSV = Path("data/satellite_inventory.csv")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def ensure_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def daterange_months(start_date, end_date):
    current = start_date
    while current <= end_date:
        if current.month == 12:
            next_month = datetime.date(current.year + 1, 1, 1)
        else:
            next_month = datetime.date(current.year, current.month + 1, 1)
        month_end = min(next_month, end_date)
        yield current, month_end
        current = next_month

def select_lowest_cloud_item(client, month_start, month_end):
    search = client.search(
        collections=[COLLECTION_ID],
        bbox=BBOX,
        datetime=f"{month_start.isoformat()}/{month_end.isoformat()}",
        query={"eo:cloud_cover": {"lt": MAX_CLOUD}}
    )
    items = list(search.get_items())
    if not items:
        return None
    best = min(items, key=lambda it: it.properties.get("eo:cloud_cover", 100))
    return best

def download_asset(url, dest_path):
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"Downloaded {dest_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def update_inventory(records):
    existing = {}
    if INVENTORY_CSV.exists():
        try:
            with open(INVENTORY_CSV, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing[row["date"]] = {
                        "date": row["date"],
                        "red_path": row.get("red_path", ""),
                        "nir_path": row.get("nir_path", ""),
                        "green_path": row.get("green_path", "")
                    }
        except Exception as e:
            logger.warning(f"Could not read existing inventory: {e}")

    for rec in records:
        existing[rec["date"]] = rec

    with open(INVENTORY_CSV, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["date", "red_path", "nir_path", "green_path"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for date in sorted(existing.keys()):
            writer.writerow(existing[date])
    logger.info(f"Inventory updated at {INVENTORY_CSV}")

def main():
    ensure_directories()

    client = Client.open(API_URL)
    downloaded_records = []

    for month_start, month_end in daterange_months(START_DATE, END_DATE):
        logger.info(f"Searching period {month_start} to {month_end}")
        item = select_lowest_cloud_item(client, month_start, month_end)
        if item is None:
            logger.warning(f"No items found for {month_start.isoformat()}")
            continue

        date_str = item.datetime.date().isoformat()
        band_paths = {}
        for band, key in [("B04", "red_path"), ("B08", "nir_path"), ("B03", "green_path")]:
            asset = item.assets.get(band)
            if asset is None:
                logger.warning(f"Item {item.id} missing asset {band}")
                continue
            signed_url = planetary_computer.sign(asset.href)
            filename = f"{date_str}_{band}.tif"
            dest_path = DATA_DIR / filename
            success = download_asset(signed_url, dest_path)
            if success:
                band_paths[key] = str(dest_path)
            else:
                logger.error(f"Skipping record for {date_str} due to download failure of {band}")
                band_paths = {}
                break

        if all(k in band_paths for k in ("red_path", "nir_path", "green_path")):
            downloaded_records.append({
                "date": date_str,
                "red_path": band_paths["red_path"],
                "nir_path": band_paths["nir_path"],
                "green_path": band_paths["green_path"]
            })

    if downloaded_records:
        update_inventory(downloaded_records)
    else:
        logger.info("No new records downloaded; inventory not updated.")

if __name__ == "__main__":
    main()