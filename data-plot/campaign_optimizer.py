from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
import numpy as np

def build_interpolator(field, lats, lons):
    return RegularGridInterpolator(
        (lats, lons),
        field,
        bounds_error=False,
        fill_value=np.nan
    )

def normalize(v):
    n = np.linalg.norm(v)
    if not np.isfinite(n) or n == 0:
        return np.zeros_like(v)
    return v / n

def km_to_deg_lat(km):
    return km / 111.0

def km_to_deg_lon(km, lat):
    return km / (111.0 * np.cos(np.deg2rad(lat)))
    

def inside_domain(lat, lon, lat_min, lat_max, lon_min, lon_max, margin=0.0):
    return (
        lat_min + margin <= lat <= lat_max - margin and
        lon_min + margin <= lon <= lon_max - margin
    )
    
def directional_gain(interp_strain, lat, lon, dlat, dlon, direction):
    lat1 = lat + direction[0] * dlat
    lon1 = lon + direction[1] * dlon

    s0 = interp_strain((lat, lon))
    s1 = interp_strain((lat1, lon1))

    if not np.isfinite(s0) or not np.isfinite(s1):
        return -np.inf

    return (s1 - s0) / np.sqrt(dlat**2 + dlon**2)

def path_hits_nan(interp_nan, lat, lon, direction, step_km, lat_ref, n_samples=5):

    lats_path = []
    lons_path = []

    for a in np.linspace(0, 1, n_samples):
        la = lat + a * direction[0] * km_to_deg_lat(step_km)
        lo = lon + a * direction[1] * km_to_deg_lon(step_km, lat_ref)
        lats_path.append(la)
        lons_path.append(lo)

    samples = interp_nan(np.column_stack((lats_path, lons_path)))
    return np.any(samples > 0.5)

def distance_km(lat1, lon1, lat2, lon2):
    dlat = (lat2 - lat1) * 111.0
    dlon = (lon2 - lon1) * 111.0 * np.cos(np.deg2rad(lat1))
    return np.sqrt(dlat**2 + dlon**2)