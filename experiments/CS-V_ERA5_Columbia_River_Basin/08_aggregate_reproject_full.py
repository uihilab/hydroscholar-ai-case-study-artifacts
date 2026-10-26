#!/usr/bin/env python3

import os
import sys
import logging
import zipfile
import tempfile
from pathlib import Path

import numpy as np
import xarray as xr
import rioxarray  # noqa: registers the rio accessor
import geopandas as gpd

ENGINES = ["netcdf4", "h5netcdf", "scipy", "cfgrib"]


def find_time_dim(ds):
    for coord in ds.coords:
        if np.issubdtype(ds.coords[coord].dtype, np.datetime64):
            logging.info(f"Identified time dimension: '{coord}'")
            return coord
    logging.error("No datetime64 coordinate found in dataset")
    return None


def process_year(infile: Path, basin):
    year = infile.stem.split("_")[1]
    outfile = infile.parent / f"era5_{year}_daily_32611.nc"
    if outfile.exists():
        logging.info(f"[SKIP] Output exists: {outfile.name}")
        return

    logging.info(f"[START] Processing {infile.name} for year {year}")

    # Detect ZIP archive
    with open(infile, "rb") as f:
        magic = f.read(2)
    is_zip = magic == b"PK"

    tmpdir = None
    try:
        if is_zip:
            tmpdir = tempfile.TemporaryDirectory()
            logging.info(f"ZIP detected. Extracting to {tmpdir.name}")
            with zipfile.ZipFile(str(infile), "r") as z:
                nc_members = [n for n in z.namelist() if n.endswith(".nc")]
                if not nc_members:
                    logging.error("No .nc files found in ZIP")
                    return
                for member in nc_members:
                    z.extract(member, path=tmpdir.name)
            candidates = [Path(tmpdir.name) / n for n in nc_members]
        else:
            candidates = [infile]

        # Prepare containers for daily aggregates
        daily_vars = {"tp": [], "t2m": []}

        for candidate in candidates:
            opened = False
            for engine in ENGINES:
                try:
                    logging.info(f"Trying to open '{candidate.name}' with engine='{engine}'")
                    with xr.open_dataset(str(candidate), engine=engine, chunks=None) as ds:
                        logging.info(f"Opened '{candidate.name}' with engine='{engine}'")
                        time_dim = find_time_dim(ds)
                        if time_dim is None:
                            raise RuntimeError("Time dimension not found")
                        for var in ("tp", "t2m"):
                            if var in ds.data_vars:
                                if var == "tp":
                                    da = ds[var].resample({time_dim: "1D"}).sum(keep_attrs=True)
                                else:
                                    da = ds[var].resample({time_dim: "1D"}).mean(keep_attrs=True)
                                # unify name of time coordinate
                                if time_dim != "time":
                                    da = da.rename({time_dim: "time"})
                                logging.info(f"Aggregated '{var}' daily from '{candidate.name}'")
                                daily_vars[var].append(da)
                    opened = True
                    break
                except Exception as e:
                    logging.warning(f"Engine '{engine}' failed for '{candidate.name}': {e}")
            if not opened:
                logging.error(f"All engines failed to open '{candidate.name}'")
                sys.exit(1)

        # Merge lists of DataArrays into unified DataArrays
        merged_data = {}
        for var, das in daily_vars.items():
            if not das:
                logging.warning(f"No data found for variable '{var}' in any file")
                continue
            if len(das) > 1:
                da_all = xr.concat(das, dim="time").sortby("time")
                logging.info(f"Concatenated {len(das)} parts for '{var}'")
            else:
                da_all = das[0]
            merged_data[var] = da_all

        if not merged_data:
            logging.error("No variables were aggregated; skipping output")
            return

        # Build combined Dataset
        ds_daily = xr.Dataset(merged_data)
        logging.info("Merged variables into one Dataset")

        # Rename spatial dims to x/y if needed
        rename_map = {}
        for old, new in [("latitude", "y"), ("lat", "y"), ("longitude", "x"), ("lon", "x")]:
            if old in ds_daily.dims:
                rename_map[old] = new
        if rename_map:
            ds_daily = ds_daily.rename(rename_map)
            logging.info(f"Renamed spatial dims: {rename_map}")

        # Assign CRS, reproject, and clip
        ds_proj = (
            ds_daily
            .rio.write_crs("EPSG:4326", inplace=False)
            .rio.reproject("EPSG:32611")
        )
        logging.info("Reprojected to EPSG:32611")

        ds_clip = ds_proj.rio.clip(
            basin.geometry,
            basin.crs,
            drop=True,
            invert=False
        )
        logging.info("Clipped to basin boundary")

        # Write output with compression
        encoding = {var: {"zlib": True, "complevel": 4} for var in merged_data}
        ds_clip.to_netcdf(str(outfile), encoding=encoding)
        logging.info(f"[DONE] Wrote {outfile.name}")

    finally:
        # Ensure temporary directory is cleaned up after datasets are closed
        if tmpdir is not None:
            tmpdir.cleanup()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    data_dir = Path("data")
    basin_path = data_dir / "columbia_basin.geojson"
    if not basin_path.exists():
        logging.error(f"Basin file missing: {basin_path}")
        sys.exit(1)

    logging.info(f"Loading basin boundary from {basin_path}")
    basin = gpd.read_file(str(basin_path))
    try:
        basin = basin.to_crs("EPSG:32611")
    except Exception as e:
        logging.error(f"Failed to reproject basin: {e}")
        sys.exit(1)

    pattern = "era5_????_hourly.*"
    files = sorted(data_dir.glob(pattern))
    if not files:
        logging.warning(f"No files matching pattern: {pattern}")
        return

    for infile in files:
        try:
            process_year(infile, basin)
        except Exception as e:
            logging.error(f"Failed on {infile.name}: {e}")


if __name__ == "__main__":
    main()