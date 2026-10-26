import os
import sys
import tempfile
import zipfile
import shutil
import xarray as xr
import numpy as np

def find_time_dim(ds):
    # Prefer a coord literally named 'time'
    if 'time' in ds.coords:
        return 'time'
    # Otherwise pick the first datetime64 coordinate
    for name, coord in ds.coords.items():
        if hasattr(coord, 'dtype') and np.issubdtype(coord.dtype, np.datetime64):
            return name
    return None


def aggregate_var(file_path, var_name):
    print(f"Opening '{file_path}' for variable '{var_name}'...")
    ds = xr.open_dataset(file_path)
    print(f"Variables in dataset: {list(ds.data_vars)}")
    if var_name not in ds.data_vars:
        ds.close()
        raise ValueError(f"Variable '{var_name}' not found in {file_path}")
    time_dim = find_time_dim(ds)
    if not time_dim:
        ds.close()
        raise ValueError(f"No datetime coordinate found in {file_path}")
    print(f"Resampling '{var_name}' along '{time_dim}' to daily...")
    if var_name == 'tp':
        daily = ds[var_name].resample(**{time_dim: '1D'}).sum()
    else:
        daily = ds[var_name].resample(**{time_dim: '1D'}).mean()
    ds.close()
    return daily


def main():
    input_path = os.path.join('data', 'era5_jan1980_hourly.nc')
    output_path = os.path.join('data', 'era5_jan1980_daily.nc')

    print(f"Checking for input file at '{input_path}'...")
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    if os.path.getsize(input_path) == 0:
        print(f"ERROR: Input file is empty (0 bytes): {input_path}")
        sys.exit(1)

    print("Inspecting file header for ZIP signature...")
    is_zip = False
    with open(input_path, 'rb') as f:
        if f.read(4) == b'PK\x03\x04':
            is_zip = True
            print("Detected ZIP archive.")

    tmp_dir = None
    tp_daily = None
    t2m_daily = None

    try:
        if is_zip:
            print("Extracting ZIP archive...")
            tmp_dir = tempfile.mkdtemp(prefix='era5_unzip_')
            with zipfile.ZipFile(input_path, 'r') as z:
                z.extractall(tmp_dir)
            # Find all .nc files
            nc_files = []
            for root, _, files in os.walk(tmp_dir):
                for fname in files:
                    if fname.lower().endswith('.nc'):
                        nc_files.append(os.path.join(root, fname))
            if not nc_files:
                raise RuntimeError("No .nc files found inside the ZIP archive.")
            print(f"Found {len(nc_files)} .nc files: {nc_files}")
            # Map variables to their files
            var_files = {'tp': None, 't2m': None}
            for fp in nc_files:
                ds = xr.open_dataset(fp, decode_times=False)
                for var in list(var_files):
                    if var in ds.data_vars:
                        var_files[var] = fp
                ds.close()
            if var_files['tp'] is None or var_files['t2m'] is None:
                raise RuntimeError(f"Could not locate both 'tp' and 't2m' in extracted files: {var_files}")
            # Aggregate each variable
            tp_daily = aggregate_var(var_files['tp'], 'tp')
            t2m_daily = aggregate_var(var_files['t2m'], 't2m')
        else:
            # Single-file case
            print(f"Opening single NetCDF '{input_path}'...")
            ds = xr.open_dataset(input_path)
            if 'tp' not in ds.data_vars or 't2m' not in ds.data_vars:
                ds.close()
                raise RuntimeError("Single file does not contain both 'tp' and 't2m'.")
            time_dim = find_time_dim(ds)
            if not time_dim:
                ds.close()
                raise RuntimeError("No datetime coordinate found in the dataset.")
            print("Aggregating 'tp' and 't2m' from single file...")
            tp_daily = ds['tp'].resample(**{time_dim: '1D'}).sum()
            t2m_daily = ds['t2m'].resample(**{time_dim: '1D'}).mean()
            ds.close()

        # Combine into one Dataset
        print("Combining aggregated variables into a single Dataset...")
        daily_ds = xr.Dataset({'tp': tp_daily, 't2m': t2m_daily})
        # Ensure output directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            print(f"Creating output directory '{out_dir}'...")
            os.makedirs(out_dir, exist_ok=True)
        # Save
        print(f"Saving daily dataset to '{output_path}'...")
        daily_ds.to_netcdf(output_path)
        print("Daily aggregation complete.")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        if tmp_dir and os.path.isdir(tmp_dir):
            print(f"Cleaning up temporary directory '{tmp_dir}'...")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            print("Temporary files removed.")

if __name__ == '__main__':
    main()