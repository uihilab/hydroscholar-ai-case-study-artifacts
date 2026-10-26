#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt


def plot_comparison(var_name, ds31km, ds1km, basin, date,
                    cmap, units, out_path):
    """
    Create a side‐by‐side comparison plot of ERA5 31km and kriged 1km data.
    """
    # Select the 31km slice
    try:
        da31 = ds31km[var_name].sel(valid_time=date)
    except Exception:
        da31 = ds31km[var_name].sel(time=date)

    # Select the 1km data (no time dim, already for date)
    da1 = ds1km[f"{var_name}_1km"]

    # Compute common colorbar limits
    vmin = float(min(da31.min().values, da1.min().values))
    vmax = float(max(da31.max().values, da1.max().values))

    # Create figure and axes
    fig, axes = plt.subplots(ncols=2, figsize=(12, 5), constrained_layout=True)
    titles = [f"ERA5 31km {var_name} on {date}",
              f"Kriged 1km {var_name} on {date}"]

    # Plot 31km
    im1 = da31.plot(
        ax=axes[0],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        add_colorbar=False
    )
    basin.boundary.plot(ax=axes[0], edgecolor="black", linewidth=1)
    axes[0].set_title(titles[0])
    axes[0].set_xlabel("")
    axes[0].set_ylabel("")

    # Plot 1km
    im2 = da1.plot(
        ax=axes[1],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        add_colorbar=False
    )
    basin.boundary.plot(ax=axes[1], edgecolor="black", linewidth=1)
    axes[1].set_title(titles[1])
    axes[1].set_xlabel("")
    axes[1].set_ylabel("")

    # Shared colorbar
    cbar = fig.colorbar(
        im1,
        ax=axes,
        orientation="vertical",
        fraction=0.02,
        pad=0.04
    )
    cbar.set_label(units)

    # Save figure
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot saved to {out_path}")


def main():
    # Paths
    path31 = Path("data/era5_jan1980_daily_32611.nc")
    path_pr1km = Path("outputs/era5_19800101_pr_1km.nc")
    path_t21km = Path("outputs/era5_19800101_t2m_1km.nc")
    basin_path = Path("data/columbia_basin_32611.geojson")
    figs_dir = Path("figures")

    # Check inputs
    for p in (path31, path_pr1km, path_t21km, basin_path):
        if not p.exists():
            print(f"ERROR: Required file not found: {p}")
            sys.exit(1)

    # Create output directory
    figs_dir.mkdir(parents=True, exist_ok=True)

    # Load datasets
    ds31 = xr.open_dataset(path31)
    ds_pr1km = xr.open_dataset(path_pr1km)
    ds_t21km = xr.open_dataset(path_t21km)

    # Load basin boundary
    basin = gpd.read_file(basin_path)

    # Date to plot
    date = "1980-01-01"

    # Plot precipitation comparison
    plot_comparison(
        var_name="tp",
        ds31km=ds31,
        ds1km=ds_pr1km,
        basin=basin,
        date=date,
        cmap="Blues",
        units="Precipitation (m)",
        out_path=figs_dir / "comparison_pr_19800101.png"
    )

    # Plot temperature comparison
    plot_comparison(
        var_name="t2m",
        ds31km=ds31,
        ds1km=ds_t21km,
        basin=basin,
        date=date,
        cmap="coolwarm",
        units="Temperature (K)",
        out_path=figs_dir / "comparison_t2m_19800101.png"
    )


if __name__ == "__main__":
    main()