# README_design.md

## 1. Project Objectives
High-resolution (1 km) downscaling of ERA5 total precipitation and 2 m temperature over the Columbia River Basin for the period 1980–2023.  
- Deliver daily 1 km gridded precipitation and temperature datasets.  
- Ensure consistent CRS (EPSG:32611) and basin‐wide coverage.

## 2. Prototype Phase (Phase 1)
Scope limited to January 1980 to validate workflow and data handling.  
- Acquire ERA5 hourly total precipitation and 2 m temperature via the CDS API.  
- Aggregate hourly fields to daily sums (precipitation) and daily means (temperature).  
- Export prototype outputs as single NetCDF files for January 1980.

## 3. Methodology (Phase 2)
1. Preprocessing  
   - Reproject ERA5 NetCDF and Columbia River Basin vector (shapefile/GeoJSON) to EPSG:32611 using `rioxarray` and `geopandas`.  
   - Clip/grids subsets to basin extent.
2. Downscaling  
   - Apply Ordinary Kriging from native ERA5 (~31 km) grid to 1 km target using `pykrige` or `scipy.interpolate`.  
   - Validate interpolation performance with cross-validation metrics.
3. Optional Topographic Correction  
   - Incorporate a high-resolution DEM (e.g., 30 m) and apply lapse-rate adjustment to downscaled temperature fields.

## 4. Full-Scale Pipeline (Phase 3)
- Automate processing for the full period 1980–2023.  
- Chunk by monthly or seasonal blocks to manage memory.  
- Parallelize where possible (e.g., dask).  
- Export results as chunked, CF‐compliant NetCDF files in `/data/processed/downscaled/`.

## 5. Required Tools and Libraries
- cdsapi: data acquisition from Copernicus Climate Data Store  
- xarray & rioxarray: NetCDF and raster I/O, CRS management  
- geopandas: vector handling and basin geometry  
- pykrige or scipy.interpolate: kriging algorithms  
- matplotlib: quick diagnostics and map visualizations  
- (Optional) rasterio or richDEM: DEM processing and hydrological corrections  

## 6. Coordinate Reference System (CRS)
All spatial data (raw, intermediate, and final) are maintained in EPSG:32611 (UTM zone 11N) to ensure consistency across processing steps.

## 7. Workspace Layout
/data/
  raw/
    era5/            # downloaded ERA5 hourly NetCDF files
    dem/             # high-resolution DEM
  processed/
    clipped/         # reprojected & clipped inputs
    downscaled/      # final 1 km NetCDF outputs chunked by period
/scripts/
  00_config.py
  01_acquire_basin_boundary.py
  02_fetch_era5.py
  03_preprocess.py
  04_downscale_kriging.py
  05_visualize_prototype.py
  06_pipeline_runner.py
  utils/             # helper functions and common routines
/outputs/
  figures/           # diagnostic plots, maps
  logs/              # processing logs
README_design.md     # this design document

## 8. Script Naming Conventions
- 00_config.py: global constants (paths, CRS, time ranges, API keys)  
- 01_acquire_basin_boundary.py: download/load basin geometry and reproject to EPSG:32611  
- 02_fetch_era5.py: fetch ERA5 hourly precipitation and temperature for prototype period  
- 03_preprocess.py: reproject, clip, aggregate to daily time step  
- 04_downscale_kriging.py: perform ordinary kriging to 1 km grid (with optional topo correction)  
- 05_visualize_prototype.py: generate summary figures for prototype outputs  
- 06_pipeline_runner.py: orchestrate full pipeline over multiple periods  
- utils/*.py: shared functions (e.g., logging setup, I/O wrappers, validation routines)