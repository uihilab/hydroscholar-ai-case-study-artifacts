#!/usr/bin/env python3

import logging
import sys
from pathlib import Path

import xarray as xr
import rioxarray  # noqa: F401 to register the rio accessor
import geopandas as gpd


def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Define input and output paths
    input_nc = Path("data/era5_jan1980_daily.nc")
    input_geo = Path("data/columbia_basin.geojson")
    output_nc = Path("data/era5_jan1980_daily_32611.nc")
    output_geo = Path("data/columbia_basin_32611.geojson")

    # Check inputs
    if not input_nc.exists():
        logger.error(f"Daily ERA5 file not found: {input_nc}")
        sys.exit(1)
    if not input_geo.exists():
        logger.error(f"Basin boundary file not found: {input_geo}")
        sys.exit(1)

    # Ensure output directories exist
    for p in [output_nc.parent, output_geo.parent]:
        if not p.exists():
            logger.info(f"Creating directory: {p}")
            p.mkdir(parents=True, exist_ok=True)

    # Load and reproject basin boundary
    logger.info(f"Loading basin boundary from {input_geo}")
    try:
        basin = gpd.read_file(str(input_geo))
    except Exception as e:
        logger.error(f"Failed to read basin GeoJSON: {e}")
        sys.exit(1)

    logger.info("Reprojecting basin boundary to EPSG:32611")
    try:
        basin_32611 = basin.to_crs(epsg=32611)
    except Exception as e:
        logger.error(f"Failed to reproject basin: {e}")
        sys.exit(1)

    logger.info(f"Saving reprojected basin to {output_geo}")
    try:
        basin_32611.to_file(str(output_geo), driver="GeoJSON")
    except Exception as e:
        logger.error(f"Failed to save reprojected basin GeoJSON: {e}")
        sys.exit(1)

    # Load daily ERA5 NetCDF
    logger.info(f"Loading ERA5 daily data from {input_nc}")
    try:
        ds = xr.open_dataset(str(input_nc))
    except Exception as e:
        logger.error(f"Failed to open NetCDF: {e}")
        sys.exit(1)

    # Assign the native CRS (likely EPSG:4326)
    logger.info("Assigning CRS 'EPSG:4326' to the dataset")
    try:
        ds = ds.rio.write_crs("EPSG:4326", inplace=False)
    except Exception as e:
        logger.error(f"Failed to write CRS to dataset: {e}")
        sys.exit(1)

    # Reproject to EPSG:32611
    logger.info("Reprojecting ERA5 data to EPSG:32611")
    try:
        ds_32611 = ds.rio.reproject("EPSG:32611")
    except Exception as e:
        logger.error(f"Failed to reproject ERA5 dataset: {e}")
        sys.exit(1)

    # Clip to basin extent
    logger.info("Clipping reprojected data to basin boundary")
    try:
        ds_clip = ds_32611.rio.clip(
            basin_32611.geometry,
            basin_32611.crs,
            drop=True,
            invert=False
        )
    except Exception as e:
        logger.error(f"Failed to clip dataset: {e}")
        sys.exit(1)

    # Save the result
    logger.info(f"Saving clipped dataset to {output_nc}")
    try:
        ds_clip.to_netcdf(str(output_nc))
    except Exception as e:
        logger.error(f"Failed to write output NetCDF: {e}")
        sys.exit(1)

    logger.info("Reprojection and clipping complete.")


if __name__ == "__main__":
    main()