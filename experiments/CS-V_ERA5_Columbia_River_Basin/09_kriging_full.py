#!/usr/bin/env python3

import logging
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np
import xarray as xr
import geopandas as gpd
import rioxarray  # noqa: registers the rio accessor
from pykrige.ok import OrdinaryKriging

# Configure logging
tooling = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Directory paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
BASIN_GEOJSON = DATA_DIR / "columbia_basin_32611.geojson"

# Target grid resolution (meters)
GRID_RES = 1000.0


def init_target_grid():
    """
    Read basin bounds and construct 1km target grid (x_tg, y_tg).
    """
    if not BASIN_GEOJSON.exists():
        tooling.error(f"Basin file not found: {BASIN_GEOJSON}")
        raise FileNotFoundError(BASIN_GEOJSON)
    basin = gpd.read_file(str(BASIN_GEOJSON))
    # Ensure basin is in EPSG:32611
    basin = basin.to_crs("EPSG:32611")

    minx, miny, maxx, maxy = basin.total_bounds
    # Extend max bounds slightly to include last cell
    x_tg = np.arange(minx, maxx + GRID_RES, GRID_RES)
    y_tg = np.arange(miny, maxy + GRID_RES, GRID_RES)
    tooling.info(
        f"Target grid: x from {minx:.1f} to {maxx:.1f} ({len(x_tg)} points), "
        f"y from {miny:.1f} to {maxy:.1f} ({len(y_tg)} points)"
    )
    return x_tg, y_tg


def process_day(ds_path, date_str, date_tag, x_tg, y_tg, time_dim):
    """
    Krige precipitation and temperature for a single day.
    ds_path   : path to yearly daily NetCDF
    date_str  : 'YYYY-MM-DD' for xarray selection
    date_tag  : 'YYYYMMDD' for filename
    x_tg, y_tg: target grid 1d arrays
    time_dim  : name of the time coordinate in the ds
    """
    pr_out = OUTPUT_DIR / f"era5_{date_tag}_pr_1km.nc"
    t2m_out = OUTPUT_DIR / f"era5_{date_tag}_t2m_1km.nc"

    # Skip if both exist
    if pr_out.exists() and t2m_out.exists():
        tooling.info(f"[SKIP] Outputs exist for {date_tag}")
        return

    try:
        ds = xr.open_dataset(ds_path, decode_times=True)
        # Source grid coords
        x_src = ds["x"].values
        y_src = ds["y"].values
        gridx_src, gridy_src = np.meshgrid(x_src, y_src)
        x_flat = gridx_src.ravel()
        y_flat = gridy_src.ravel()

        # Extract 1-day slices
        da_pr = ds["tp"].sel({time_dim: date_str})
        da_t2m = ds["t2m"].sel({time_dim: date_str})
        z_pr = da_pr.values.ravel()
        z_t2m = da_t2m.values.ravel()

        # Mask NaNs
        mask_pr = ~np.isnan(z_pr)
        mask_t2m = ~np.isnan(z_t2m)
        x_pr = x_flat[mask_pr]; y_pr = y_flat[mask_pr]; z_pr = z_pr[mask_pr]
        x_t2m_src = x_flat[mask_t2m]; y_t2m_src = y_flat[mask_t2m]; z_t2m = z_t2m[mask_t2m]

        # Kriging precipitation
        tooling.info(f"Kriging tp for {date_tag} ({len(z_pr)} points)...")
        try:
            ok_pr = OrdinaryKriging(
                x_pr, y_pr, z_pr,
                variogram_model="spherical",
                verbose=False,
                enable_plotting=False
            )
        except Exception as e:
            tooling.warning(f"Variogram fit failed for tp {date_tag}: {e}. Falling back to defaults.")
            ok_pr = OrdinaryKriging(
                x_pr, y_pr, z_pr,
                variogram_model="spherical",
                variogram_model_parameters=(1.0, 0.0, 0.0),
                verbose=False,
                enable_plotting=False
            )
        z_pr_grid, _ = ok_pr.execute("grid", x_tg, y_tg)

        da_pr_1km = xr.DataArray(
            data=z_pr_grid,
            dims=("y", "x"),
            coords={"y": y_tg, "x": x_tg},
            name="tp_1km",
            attrs={"units": ds["tp"].attrs.get("units", ""), "crs": "EPSG:32611"}
        )
        ds_pr_out = da_pr_1km.to_dataset()
        ds_pr_out = ds_pr_out.rio.write_crs("EPSG:32611", inplace=False)
        ds_pr_out.to_netcdf(pr_out)
        tooling.info(f"Written precipitation krige to {pr_out}")

        # Kriging temperature
        tooling.info(f"Kriging t2m for {date_tag} ({len(z_t2m)} points)...")
        try:
            ok_t2m = OrdinaryKriging(
                x_t2m_src, y_t2m_src, z_t2m,
                variogram_model="spherical",
                verbose=False,
                enable_plotting=False
            )
        except Exception as e:
            tooling.warning(f"Variogram fit failed for t2m {date_tag}: {e}. Falling back to defaults.")
            ok_t2m = OrdinaryKriging(
                x_t2m_src, y_t2m_src, z_t2m,
                variogram_model="spherical",
                variogram_model_parameters=(1.0, 0.0, 0.0),
                verbose=False,
                enable_plotting=False
            )
        z_t2m_grid, _ = ok_t2m.execute("grid", x_tg, y_tg)

        da_t2m_1km = xr.DataArray(
            data=z_t2m_grid,
            dims=("y", "x"),
            coords={"y": y_tg, "x": x_tg},
            name="t2m_1km",
            attrs={"units": ds["t2m"].attrs.get("units", ""), "crs": "EPSG:32611"}
        )
        ds_t2m_out = da_t2m_1km.to_dataset()
        ds_t2m_out = ds_t2m_out.rio.write_crs("EPSG:32611", inplace=False)
        ds_t2m_out.to_netcdf(t2m_out)
        tooling.info(f"Written temperature krige to {t2m_out}")

    except Exception as e:
        tooling.error(f"[ERROR] Failed processing {date_tag}: {e}")
    finally:
        try:
            ds.close()
        except Exception:
            pass


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    x_tg, y_tg = init_target_grid()

    pattern = "era5_*_daily_32611.nc"
    daily_files = sorted(DATA_DIR.glob(pattern))
    if not daily_files:
        tooling.error(f"No daily files found matching {pattern}")
        return

    tasks = []
    for ds_path in daily_files:
        # Detect the actual time dimension name
        ds = xr.open_dataset(str(ds_path), decode_times=True)
        time_dims = [c for c in ds.coords if np.issubdtype(ds[c].dtype, np.datetime64)]
        if not time_dims:
            tooling.error(f"No datetime coordinate in {ds_path}")
            ds.close()
            continue
        time_dim = time_dims[0]
        times = ds[time_dim].values
        ds.close()

        for t in times:
            date_str = np.datetime_as_string(t, unit="D")
            date_tag = date_str.replace('-', '')
            tasks.append((str(ds_path), date_str, date_tag, x_tg, y_tg, time_dim))

    n_workers = max(1, cpu_count() - 1)
    tooling.info(f"Starting kriging with {n_workers} workers on {len(tasks)} tasks")
    with Pool(processes=n_workers) as pool:
        pool.starmap(process_day, tasks)

    tooling.info("All kriging tasks complete.")


if __name__ == "__main__":
    main()