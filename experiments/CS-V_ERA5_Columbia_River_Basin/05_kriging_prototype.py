#!/usr/bin/env python3

import os
import logging
import numpy as np
import xarray as xr
import geopandas as gpd
import rioxarray  # noqa: registers the rio accessor
from pykrige.ok import OrdinaryKriging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    # Paths
    nc_path = "data/era5_jan1980_daily_32611.nc"
    geojson_path = "data/columbia_basin_32611.geojson"
    output_dir = "outputs"
    pr_out = os.path.join(output_dir, "era5_19800101_pr_1km.nc")
    t2m_out = os.path.join(output_dir, "era5_19800101_t2m_1km.nc")

    logger.info("Ensuring output directory exists...")
    os.makedirs(output_dir, exist_ok=True)

    # Load dataset
    logger.info(f"Loading NetCDF: {nc_path}")
    ds = xr.open_dataset(nc_path)

    # Load basin boundary and get bounds
    logger.info(f"Loading basin boundary: {geojson_path}")
    basin = gpd.read_file(geojson_path)
    minx, miny, maxx, maxy = basin.total_bounds
    logger.info(f"Basin bounds (EPSG:32611): {minx}, {miny}, {maxx}, {maxy}")

    # Select January 1, 1980
    logger.info("Selecting data for 1980-01-01...")
    da_pr = ds["tp"].sel(valid_time="1980-01-01")
    da_t2m = ds["t2m"].sel(valid_time="1980-01-01")

    # Extract source grid coordinates and values
    logger.info("Extracting source grid and flattening...")
    x_src_1d = da_pr["x"].values
    y_src_1d = da_pr["y"].values
    gridx_src, gridy_src = np.meshgrid(x_src_1d, y_src_1d)
    z_pr = da_pr.values.flatten()
    z_t2m = da_t2m.values.flatten()
    x_pr = gridx_src.flatten()
    y_pr = gridy_src.flatten()

    # Define target grid at 1 km resolution
    logger.info("Defining 1 km target grid over basin extent...")
    res = 1000.0  # meters
    x_tg = np.arange(minx, maxx + res, res)
    y_tg = np.arange(miny, maxy + res, res)
    gridx_tg, gridy_tg = np.meshgrid(x_tg, y_tg)

    def run_kriging(x, y, z, var_name):
        logger.info(f"Running OrdinaryKriging for '{var_name}'...")
        # Filter out missing values
        mask = np.isfinite(z)
        x_clean = x[mask]
        y_clean = y[mask]
        z_clean = z[mask]

        if x_clean.size == 0:
            logger.error(f"No valid data points for '{var_name}', returning all-NaN grid.")
            z_grid = np.full(gridx_tg.shape, np.nan)
        else:
            # Try spherical first, fall back to linear
            try:
                ok = OrdinaryKriging(
                    x_clean, y_clean, z_clean,
                    variogram_model="spherical",
                    verbose=False,
                    enable_plotting=False,
                )
                logger.info(f"Initialized spherical variogram for '{var_name}'")
            except Exception as e:
                logger.warning(f"Spherical variogram failed for '{var_name}': {e}")
                logger.info(f"Falling back to linear variogram for '{var_name}'")
                ok = OrdinaryKriging(
                    x_clean, y_clean, z_clean,
                    variogram_model="linear",
                    variogram_parameters=[1.0, 100000.0],
                    verbose=False,
                    enable_plotting=False,
                )
                logger.info(f"Initialized linear variogram for '{var_name}'")

            logger.info(f"Executing kriging grid for '{var_name}'")
            z_grid, ss = ok.execute("grid", x_tg, y_tg)

        # Build xarray DataArray
        da = xr.DataArray(
            data=z_grid,
            dims=("y", "x"),
            coords={"y": y_tg, "x": x_tg},
            name=f"{var_name}_1km",
            attrs={"crs": "EPSG:32611", "units": "unknown"},
        )
        return da.to_dataset()

    # Interpolate precipitation
    ds_pr_out = run_kriging(x_pr, y_pr, z_pr, "tp")
    logger.info(f"Saving interpolated precipitation to '{pr_out}'...")
    ds_pr_out = ds_pr_out.rio.write_crs("EPSG:32611", inplace=False)
    ds_pr_out.to_netcdf(pr_out)

    # Interpolate temperature
    ds_t2m_out = run_kriging(x_pr, y_pr, z_t2m, "t2m")
    logger.info(f"Saving interpolated temperature to '{t2m_out}'...")
    ds_t2m_out = ds_t2m_out.rio.write_crs("EPSG:32611", inplace=False)
    ds_t2m_out.to_netcdf(t2m_out)

    logger.info("Kriging and export complete.")

if __name__ == "__main__":
    main()