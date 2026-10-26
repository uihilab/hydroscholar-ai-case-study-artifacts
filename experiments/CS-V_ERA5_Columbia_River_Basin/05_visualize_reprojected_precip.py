#!/usr/bin/env python3

import os
from pathlib import Path

import xarray as xr
import rioxarray  # noqa: F401 to register the rio accessor
import geopandas as gpd
import matplotlib.pyplot as plt

def main():
    # Define input and output paths
    input_nc = Path("data/era5_jan1980_daily_32611.nc")
    input_geo = Path("data/columbia_basin_32611.geojson")
    output_png = Path("plots/precip_jan1_1980.png")

    # Check inputs
    if not input_nc.exists():
        print(f"ERROR: NetCDF file not found: {input_nc}")
        return
    if not input_geo.exists():
        print(f"ERROR: GeoJSON file not found: {input_geo}")
        return

    # Ensure output directory exists
    output_png.parent.mkdir(parents=True, exist_ok=True)

    # Load the daily ERA5 data
    ds = xr.open_dataset(str(input_nc))

    # Select precipitation for Jan 1, 1980 using valid_time
    try:
        tp = ds["tp"].sel(valid_time="1980-01-01")
    except Exception as e:
        print(f"ERROR: Failed to select valid_time slice: {e}")
        return

    # Load basin boundary
    basin = gpd.read_file(str(input_geo))

    # Assign CRS and clip to basin
    tp = tp.rio.write_crs("EPSG:32611", inplace=False)
    try:
        tp_clip = tp.rio.clip(basin.geometry, basin.crs, drop=True, invert=False)
    except Exception as e:
        print(f"ERROR: Failed to clip precipitation data: {e}")
        return

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    tp_clip.plot(
        ax=ax,
        cmap="Blues",
        cbar_kwargs={"label": "Precipitation (m)"}
    )
    basin.boundary.plot(
        ax=ax,
        edgecolor="black",
        linewidth=2
    )

    ax.set_title("Daily Precipitation for 1980-01-01 (EPSG:32611)")
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Save figure
    try:
        plt.savefig(str(output_png), dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Plot saved to {output_png}")
    except Exception as e:
        print(f"ERROR: Failed to save plot: {e}")

if __name__ == "__main__":
    main()