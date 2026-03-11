import xarray as xr
import matplotlib.pyplot as plt

# load seaglider data

ds = xr.open_dataset('../../data/SG675_GOUGH_SAMBA/sg675_SG675_Gough_SAMBA_timeseries.nc')

# grid data

import numpy as np

# Common pressure grid
p_new = np.arange(0, 1000, 5)  # dbar

# Pull arrays once for efficiency
dive_ids = np.asarray(ds['sg_data_point_dive_number'].values)
pres     = np.asarray(ds['ctd_pressure'].values, dtype=float)

# Variables to grid
vars_to_interp = {
    'temperature': np.asarray(ds['temperature'].values, dtype=float),
    'salinity': np.asarray(ds['salinity'].values, dtype=float),
    'oxygen': np.asarray(ds['aanderaa4831_instrument_dissolved_oxygen'].values, dtype=float),
    'fluorescence': np.asarray(ds['wlbb2fl_sig695nm_adjusted'].values, dtype=float),
}

# Unique dives once
u_dives = np.unique(dive_ids)
n_rows = u_dives.size * 2  # down + up per dive

# Preallocate arrays for each variable
grids = {vname: np.full((n_rows, p_new.size), np.nan, dtype=np.float32)
         for vname in vars_to_interp}
dive_no = np.full(n_rows, np.nan, dtype=float)

r = 0
for d in u_dives:
    m = (dive_ids == d)
    p = pres[m]

    if p.size == 0 or np.all(~np.isfinite(p)):
        continue

    turn = np.nanargmax(p)

    for cast_type, sl in (('down', slice(None, turn)), ('up', slice(turn, None))):
        pup = p[sl]

        # Make sure we have enough valid samples
        if np.count_nonzero(np.isfinite(pup)) < 2:
            continue

        idx_sort = np.argsort(pup)
        x = pup[idx_sort]
        keep = np.r_[True, np.diff(x) > 0]
        x = x[keep]

        for vname, arr in vars_to_interp.items():
            y = arr[m][sl][idx_sort][keep]
            mask = np.isfinite(x) & np.isfinite(y)
            if np.count_nonzero(mask) < 2:
                continue
            grids[vname][r, :] = np.interp(p_new, x[mask], y[mask], left=np.nan, right=np.nan)

        dive_no[r] = d if cast_type == 'down' else d + 0.5
        r += 1


ds_grid = xr.Dataset(
    data_vars={
        k: (("dive", "pressure"), v[:r]) for k, v in grids.items()
    },
    coords={
        "pressure": p_new.astype(np.float32),
        "dive": dive_no[:r],
    },
    attrs={
        "note": "SeaGlider data interpolated onto common pressure grid. "
                "Downcasts = integer dive numbers; upcasts = dive+0.5.",
        "pressure_units": "dbar",
    },
)

# plot the sections
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import gsw  # TEOS-10 Gibbs SeaWater library
import numpy as np

# --- Compute potential density anomaly (sigma-theta) ---
# Extract numpy arrays
S = ds_grid['salinity'].values
T = ds_grid['temperature'].values
P = ds_grid['pressure'].values  # 1D pressure
# Use arbitrary latitude if not present — small effect on sigma0
lat = float(ds_grid.get('latitude', 0) if 'latitude' in ds_grid else 0)

# Compute Absolute Salinity (g/kg) and Conservative Temperature (°C)
SA = gsw.SA_from_SP(S, P[None, :], np.zeros_like(S), np.full_like(S, lat))
CT = gsw.CT_from_t(SA, T, P[None, :])
sigma0 = gsw.sigma0(SA, CT)  # potential density anomaly referenced to 0 dbar

# Add to dataset for reference (optional)
ds_grid['sigma0'] = (('dive', 'pressure'), sigma0)

# Choose contour levels (e.g., 1 kg/m³ spacing)
sigma_levels = np.arange(np.nanmin(sigma0), np.nanmax(sigma0), 0.25)

# --- Create figure and axes ---
fig, ax = plt.subplots(
    nrows=4, ncols=1,
    figsize=(10, 10),
    sharex=True,
    constrained_layout=True
)

# --- Plot main variables ---
pcm0 = ax[0].pcolormesh(ds_grid['dive'], ds_grid['pressure'], ds_grid['temperature'].T,
                        cmap=cmo.thermal, shading='auto')
pcm1 = ax[1].pcolormesh(ds_grid['dive'], ds_grid['pressure'], ds_grid['salinity'].T,
                        cmap=cmo.haline, shading='auto')
pcm2 = ax[2].pcolormesh(ds_grid['dive'], ds_grid['pressure'], ds_grid['oxygen'].T,
                        cmap=cmo.oxy, shading='auto', vmin=0, vmax=300)
pcm3 = ax[3].pcolormesh(ds_grid['dive'], ds_grid['pressure'], ds_grid['fluorescence'].T,
                        cmap=cmo.algae, shading='auto')

# --- Add density contours to each panel ---
for a in ax:
    cs = a.contour(ds_grid['dive'], ds_grid['pressure'], sigma0.T,
                   levels=sigma_levels, colors='k', linewidths=0.6, alpha=0.6)
    a.clabel(cs, fmt='%4.1f', fontsize=7, inline=True, colors='k')

# --- Add labels, colorbars, and titles ---
labels = [
    ('Temperature (°C)', pcm0),
    ('Salinity (psu)', pcm1),
    ('Dissolved O₂ (µmol/kg)', pcm2),
    ('Fluorescence (695 nm)', pcm3)
]

for a, (label, pcm) in zip(ax, labels):
    cb = fig.colorbar(pcm, ax=a, orientation='vertical', pad=0.03, aspect=25)
    cb.set_label(label, fontsize=9, rotation=-90, labelpad=20)
    a.set_ylim(1000 if "Fluorescence" not in label else 200, 0)
    a.set_ylabel('Depth (m)', fontsize=10)
    a.tick_params(axis='both', labelsize=10)
    a.grid(True, linestyle='--', alpha=0.3)

# --- Shared x-axis and title ---
ax[-1].set_xlabel('Dive Number', fontsize=10)
ax[0].set_title('SG675 Vertical Sections by Dive with Density Contours',
                fontsize=13, weight='bold', pad=12)

plt.savefig('/home/databot/share/www/html/img/sg675_sections_latest.png', transparent=True)

