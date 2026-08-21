markdown
# Full Pipeline Design for ERA5 Downscaling (1980–2023)

## 1. Objectives
- Downscale ERA5 hourly data (1980–2023) from native grid (~31 km) to 1 km over the Columbia Basin.
- Aggregate hourly to daily totals/means.
- Reproject to EPSG:32611 and clip to basin boundary.
- Apply Ordinary Kriging for daily interpolation at 1 km resolution.
- Assemble final time series NetCDF with complete metadata.

## 2. Modular Scripts & Responsibilities

1. **07_download_era5_full.py**
   - Use the `cdsapi` client to request ERA5 hourly data in manageable time‐chunks (e.g., 5 year batches).
   - Read CDS API key from environment or `~/.cdsapirc`.
   - Save raw NetCDFs to `data/raw/era5_{start}_{end}.nc`.
   - Verify download integrity (checksums or file sizes).

2. **08_aggregate_reproject_full.py**
   - Loop over `data/raw/*.nc`.
   - Load with `xarray` + `dask` (chunk on time).
   - Aggregate hourly to daily for variables: `tp` (sum), `t2m` (mean).
   - Assign CRS EPSG:4326, reproject to EPSG:32611 via `rioxarray`.
   - Clip to Columbia Basin boundary (`data/basin/columbia_basin.geojson`).
   - Write daily files to `data/processed/daily_32611/{date}.nc`.

3. **09_kriging_full.py**
   - Discover daily NetCDFs in `data/processed/daily_32611/`.
   - For each day:
     - Extract point values on native grid.
     - Generate 1 km target grid over basin bounds.
     - Perform OrdinaryKriging for `tp` and `t2m` using PyKrige.
     - Parallelize per‐day tasks using `dask.distributed` or `multiprocessing.Pool`.
   - Output 1 km results to `data/processed/kriged_1km/{date}_1km.nc`.

4. **10_assemble_outputs.py**
   - Collect per‐day kriged files.
   - Concatenate along time dimension into two time‐series datasets:
     - `outputs/era5_tp_1km_19800101-20231231.nc`
     - `outputs/era5_t2m_1km_19800101-20231231.nc`
   - Inject global attributes: title, institution, CRS, variable units.
   - Compress and chunk final outputs for efficient access.

5. **README.md**
   - Project overview and dataflow diagram.
   - Environment setup: Conda or pip requirements.
   - Dependency list: xarray, dask, rioxarray, geopandas, pykrige, matplotlib, cdsapi.
   - CRS details: source (EPSG:4326), target (EPSG:32611).
   - Directory structure and naming conventions.
   - Usage examples for each script.

## 3. Technical Notes

- **Memory & Performance**
  - Use `xarray.open_dataset(..., chunks={'time': 1, 'x': 500, 'y': 500})`.
  - Leverage `dask.distributed` cluster for parallel kriging jobs.
  - Persist common data (basin geometry) in worker memory.

- **Input / Output Structure**
  - `data/raw/`    : downloaded ERA5 chunks
  - `data/processed/` 
    - `daily_32611/`  : daily reprojected/clipped files
    - `kriged_1km/`   : per‐day 1 km kriging outputs
  - `outputs/`        : final concatenated NetCDFs
  - `figures/`        : diagnostics and QA plots

- **Naming Conventions**
  - Raw: `era5_{YYYYMMDD}-{YYYYMMDD}.nc`
  - Daily: `era5_daily_{YYYYMMDD}.nc`
  - Kriged: `{YYYYMMDD}_1km.nc`
  - Final: `era5_{var}_1km_19800101-20231231.nc`

- **Logging & Error Handling**
  - Standardize on `logging` module with levels INFO/WARNING/ERROR.
  - Exit codes on failure; retry logic for downloads.
  - Validate inputs exist before processing.

## 4. Next Steps

- Prototype and test on January 1980 subset.
- Profile Dask memory usage and adjust chunk sizes.
- Scale up to full 1980–2023 period.
- Add unit tests for each module and end‐to‐end integration test.