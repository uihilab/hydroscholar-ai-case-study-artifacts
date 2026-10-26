#!/usr/bin/env python3

import pandas as pd
import numpy as np
import rasterio
from pathlib import Path

def compute_ndwi_area(green_path, red_path, nir_path, threshold=0.1, pixel_area_km2=0.0001):
    """
    Compute the surface water area (in km²) where NDWI > threshold.
    NDWI = (green - nir) / (green + nir)
    """
    with rasterio.open(green_path) as src_green, \
         rasterio.open(red_path)   as src_red, \
         rasterio.open(nir_path)   as src_nir:

        # Read bands as masked arrays
        green = src_green.read(1, masked=True).astype("float32")
        red   = src_red.read(1, masked=True).astype("float32")
        nir   = src_nir.read(1, masked=True).astype("float32")

        # Ensure all rasters align
        if green.shape != red.shape or green.shape != nir.shape:
            raise ValueError(
                f"Raster dimensions do not match: "
                f"green={green.shape}, red={red.shape}, nir={nir.shape}"
            )

        # Compute NDWI, handling division by zero
        with np.errstate(divide="ignore", invalid="ignore"):
            ndwi = (green - nir) / (green + nir)

        # ndwi is a MaskedArray: masked where source was nodata or invalid
        valid_mask = ~ndwi.mask
        water_mask = (ndwi.data > threshold) & valid_mask

        count_water_pixels = int(np.sum(water_mask))
        area_km2 = count_water_pixels * pixel_area_km2

        return area_km2

def main():
    inventory_csv = Path("data/satellite_inventory.csv")
    output_csv    = Path("data/processed_inventory.csv")

    # Read existing inventory
    df = pd.read_csv(inventory_csv)

    # Prepare list to collect computed areas
    areas = []

    # Iterate over each record
    for _, row in df.iterrows():
        green_path = row["green_path"]
        red_path   = row["red_path"]
        nir_path   = row["nir_path"]

        try:
            area = compute_ndwi_area(green_path, red_path, nir_path)
        except Exception as e:
            # If there's an error, record NaN and continue
            print(f"Error processing {row['date']}: {e}")
            area = np.nan

        areas.append(area)

    # Append new column and write out
    df["surface_area_sqkm"] = areas
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Processed inventory written to {output_csv}")

if __name__ == "__main__":
    main()