from glob import glob
import numpy as np
import pandas as pd
import xarray as xr

sg267_path='/home/databot/share/www/data/sg267_WHIRLS_Mission2_2026/*.nc'

filenames = sorted(glob(sg267_path))

# 1. Initialize as empty lists
sg267_time_fix = []
sg267_lat_fix = []
sg267_lon_fix = []

for fname in filenames:
    # Use 'with' or ensure you close to avoid memory leaks with many files
    with xr.open_dataset(fname, decode_timedelta=False) as ds:
        # 2. Use .append() on the list
        sg267_time_fix.append(ds['ctd_time'][2].values)
        sg267_lat_fix.append(ds['log_gps_lat'][2].values)
        sg267_lon_fix.append(ds['log_gps_lon'][2].values)

# 3. Create the DataFrame (Pandas will automatically detect the datetime type)
df = pd.DataFrame({
    "time": sg267_time_fix, 
    "longitude": sg267_lon_fix, 
    "latitude": sg267_lat_fix
})

df.to_csv('/home/databot/share/www/data/sg267_WHIRLS_Mission2_2026/sg267_mission2_track.csv', index=False)