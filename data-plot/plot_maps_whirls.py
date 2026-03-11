from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cmocean import cm as cmo  
import cartopy.crs as ccrs
from glob import glob
import xarray as xr
import numpy as np
import matplotlib
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import cartopy.crs as ccrs
from matplotlib.patches import Patch
from datetime import datetime, timezone
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle
import numpy as np
import cartopy.crs as ccrs
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import gsw

# set font properties

font = {
        'weight' : 'normal',
        'size'   : 20}

matplotlib.rc('font', **font)

matplotlib.rcParams['xtick.major.size'] = 8
matplotlib.rcParams['xtick.major.width'] = 1
matplotlib.rcParams['xtick.minor.size'] = 8
matplotlib.rcParams['xtick.minor.width'] = 1
matplotlib.rcParams['ytick.major.size'] = 8
matplotlib.rcParams['ytick.major.width'] = 1
matplotlib.rcParams['ytick.minor.size'] = 8
matplotlib.rcParams['ytick.minor.width'] = 1

# load in the datasets
# sst = xr.open_dataset('/home/databot/share/www/data/sst_latest.nc',engine='netcdf4').sel(lat=slice(-70,-50),lon=slice(-15,15)).squeeze()
adt = xr.open_dataset('/home/databot/share/www/data/adt_latest.nc').sel(latitude=slice(-60,-20),longitude=slice(0,35)).squeeze()

# calculate geostrophic velocity
adt['gos'] = (('latitude', 'longitude'), np.sqrt(adt.ugos**2+adt.vgos**2).data)

def strain_xr(ds):

    #fac = 110.5741e3

    dvdx = ds.vgos.diff('lon')/(111.320 *1e3 *np.cos(np.deg2rad(ds.latitude)))
    dudy = ds.ugos.diff('lat')/(110.574 * 1e3)

    dvdy = ds.vgos.diff('lat')/(110.574 * 1e3)
    dudx = ds.ugos.diff('lon')/(111.320 * 1e3*np.cos(np.deg2rad(ds.latitude)))

    S = np.sqrt( (dudx - dvdy)**2 +
                (dvdx + dudy)**2 )

    return S

adt['strain'] = ('latitude', 'longitude'), strain_xr(adt).data

# Extents for the big map and the subset
bextent = [10,20,-38,-32] # Big extent
#sextent = [14,18,-61,-59] # Small extent

# add features
def add_featuresb(ax,small=False):
    
    ax.add_feature(cfeature.LAND,   facecolor='0.8',edgecolor='w',zorder=2)
    ax.add_feature(cfeature.RIVERS, edgecolor='w'  ,zorder=2)
    ax.add_feature(cfeature.LAKES,  facecolor='w'  ,zorder=2)
    ax.set(xlabel='',ylabel='')

    gls = ax.gridlines(crs=ccrs.PlateCarree(), 
                        draw_labels=True,
                        x_inline=False, 
                        y_inline=False,
                        linewidth=0.75,
                        alpha=0.75, 
                        linestyle='--', 
                        color='w',
                        ylocs=matplotlib.ticker.MultipleLocator(base=.5 if small else 1),
                        xlocs=matplotlib.ticker.MultipleLocator(base=.5 if small else 1))

    gls.top_labels = False
    gls.bottom_labels = True
    gls.right_labels = False    
    gls.left_labels = True
    gls.xpadding=10
    gls.ypadding=10   

    gls.xlabel_style = {'size': 16, 'color': 'k'}  # change size, color
    gls.ylabel_style = {'size': 16, 'color': 'k'}   

def add_sla_contours(ax,c):
    ax.contour(adt.longitude, adt.latitude,
                    adt.sla.squeeze(),
                    linewidths=0.75, alpha=1,
                    levels=np.arange(-2, 2, 0.05), colors=c,zorder=2)

def plot_gos(ax,fig):
    
    image = ax.contourf(adt.longitude, adt.latitude,
                         adt.gos,
                         levels=np.arange(0, 1.6, 0.05),
                         cmap=plt.get_cmap('cmo.speed',31), extend='max',
                         transform=ccrs.PlateCarree(),zorder=1)
    
    vctrs = ax.quiver(adt.longitude[::1], adt.latitude[::1],
                       adt.ugos[::1, ::1], adt.vgos[::1, ::1],
                       scale=2.5e1, alpha=0.8, headaxislength=5, headlength=5, headwidth=5, width=1e-3,
                       transform=ccrs.PlateCarree(),zorder=1)

    cb_ax = fig.add_axes([0.81, 0.75, 0.01, 0.15])
    cb = plt.colorbar(image,cax=cb_ax)
    cb.set_ticks([0,0.5,1,1.5])

    qk = ax.quiverkey(vctrs, 0.855, 1.04, 0.5, '0.5 m s$^{-1}$', labelpos='E',
                   coordinates='axes',zorder=6,color='k')
    
    cb.set_label('m s$^{-1}$', labelpad=18)
    # ax.set_title('{}'.format(adt.time.data))
    ax.set_title('Geostrophic Velocity AVISO ' + str(adt.time.values.astype('datetime64[D]')),y=1.015,x=0.5, fontsize=22)

def plot_strain(ax,fig):
    
    image = ax.contourf(adt.longitude, adt.latitude,
                         adt.strain * 1e5,
                         levels=np.arange(0, 3 + 1e-2, 1e-2),
                         cmap=plt.get_cmap('cmo.amp',31), extend='max',
                         transform=ccrs.PlateCarree(),zorder=1)
    
    cb_ax = fig.add_axes([0.81, 0.75, 0.01, 0.15])
    cb = plt.colorbar(image,cax=cb_ax)
    cb.set_ticks([0,1,2,3])
 

    vctrs = ax.quiver(adt.longitude[::1], adt.latitude[::1],
                       adt.ugos[::1, ::1], adt.vgos[::1, ::1],
                       scale=2.5e1, alpha=0.8, headaxislength=5, headlength=5, headwidth=5, width=1e-3,
                       transform=ccrs.PlateCarree(),zorder=1)
    
    qk = ax.quiverkey(vctrs, 0.855, 1.04, 0.5, '0.5 m s$^{-1}$', labelpos='E',
                   coordinates='axes',zorder=6,color='k')


    cb.set_label('10$^{-5}$ s$^{-1}$', labelpad=18)
    # ax.set_title('{}'.format(adt.time.data))
    ax.set_title('Geostrophic Strain AVISO ' + str(adt.time.values.astype('datetime64[D]')),y=1.015,x=0.5, fontsize=22)

def plot_sla(ax,fig):
    im = ax.pcolor(adt.longitude,adt.latitude,adt.sla,cmap=cmo.balance,vmin=-1,vmax=1,zorder=1)

    image = ax.contourf(adt.longitude, adt.latitude,
                         adt.sla,
                         levels=np.arange(-0.75, 0.8, 0.05),
                         cmap=plt.get_cmap('RdBu_r',31), extend='both',
                         transform=ccrs.PlateCarree(),zorder=1)
    
    vctrs = ax.quiver(adt.longitude[::1], adt.latitude[::1],
                       adt.ugos[::1, ::1], adt.vgos[::1, ::1],
                       scale=2.5e1, alpha=0.8, headaxislength=5, headlength=5, headwidth=5, width=1e-3,
                       transform=ccrs.PlateCarree(),zorder=1)

    cb_ax = fig.add_axes([0.81, 0.75, 0.01, 0.15])
    cb = plt.colorbar(image,cax=cb_ax)
    cb.set_ticks([-0.5,0,0.5])

    qk = ax.quiverkey(vctrs, 0.855, 1.04, 0.5, '0.5 m s$^{-1}$', labelpos='E',
                   coordinates='axes',zorder=6,color='k')
    
    cb.set_label('m', labelpad=18)
    # ax.set_title('{}'.format(adt.time.data))
    ax.set_title('Sea level anomaly AVISO ' + str(adt.time.values.astype('datetime64[D]')),y=1.015,x=0.5, fontsize=22)      

# def plot_fsle(ax):
#     im = ax.pcolor(fsle.lon,fsle.lat,fsle.lambda1.T,cmap='viridis',zorder=1)
#     plt.colorbar(im,ax=ax, label="FLE associated to the maximum eigenvalues\nof Cauchy-Green strain tensor (day$^{-1}$)",pad=0.01)
    
# def plot_sst(ax):
#     im = ax.pcolor(sst.lon,sst.lat,sst['analysed_sst'],cmap=cmo.thermal,vmin=15,vmax=25,zorder=1)
#     plt.colorbar(im,ax=ax, label='Sea surface temperature (°C)\nGHRSST MUR',pad=0.01)
#     ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)

# def plot_sst_g(ax):
#     im = ax.pcolor(sst.lon,sst.lat,sst.gradient,cmap=cmo.thermal,vmin=0,vmax=0.1,zorder=1)
#     plt.colorbar(im,ax=ax, label='Sea surface temperature gradient (°C/km)\nGHRSST MUR',pad=0.01)
#     ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)

################## ------------------ SWOT PASSES ------------------ ##################

def plot_swot_passes(
    ax,
    *,
    lon_range,                 # (lon_min, lon_max)
    lat_range,                 # (lat_min, lat_max)
    geometries_file,           # path to KaRIn_2kms_science_geometries.geojson
    passes_csv,                # path to selected_passes.csv with 'Pass number','First date','Last date'
    now=None,                  # datetime; defaults to UTC 'now'
    color='0.25',
    recent_alpha=0.50,
    upcoming_alpha=0.25,
    show_legend=True,
    legend_loc='upper right',
    legend_kw=None,
    set_extent=True            # set ax extent from lon_range/lat_range
):
    """
    Plot the most recent and next SWOT swath polygons for the map region on a Cartopy axis.

    Returns
    -------
    dict with keys: {'recent': pandas.Series|None, 'upcoming': pandas.Series|None}
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # 1) Read geometries (GeoJSON) and ensure geographic CRS
    swaths = gpd.read_file(geometries_file)
    if swaths.crs is None:
        # assume lon/lat degrees if missing
        swaths = swaths.set_crs(epsg=4326)
    else:
        swaths = swaths.to_crs(epsg=4326)

    # 2) Spatial filter by bbox for performance
    bbox_poly = box(lon_range[0], lat_range[0], lon_range[1], lat_range[1])
    # Use spatial index if available
    try:
        candidate_idx = list(swaths.sindex.query(bbox_poly, predicate='intersects'))
        swaths_in_box = swaths.iloc[candidate_idx]
        swaths_in_box = swaths_in_box[swaths_in_box.intersects(bbox_poly)]
    except Exception:
        # fallback without sindex
        swaths_in_box = swaths[swaths.intersects(bbox_poly)]

    # 3) Read passes CSV and pick recent/upcoming
    df = pd.read_csv(passes_csv, sep=';')
    df = df.copy()
    df["First date"] = pd.to_datetime(df["First date"], utc=True)
    df["Last date"]  = pd.to_datetime(df["Last date"],  utc=True)

    past = df[df["Last date"] <= now]
    recent = past.iloc[-1] if not past.empty else None

    future = df[df["First date"] > now]
    upcoming = future.iloc[0] if not future.empty else None

    # 4) Helper to draw a swath collection on Cartopy axis
    def _add_swath(pass_num, alpha):
        gsub = swaths_in_box.loc[swaths_in_box["pass_number"] == pass_num]
        if gsub.empty:
            return None
        # Cartopy's add_geometries returns a collection; we’ll use proxy for legend anyway
        ax.add_geometries(
            gsub.geometry.values,
            crs=ccrs.PlateCarree(),
            color=color,
            alpha=alpha,
            linewidth=0.8,
            zorder=3,
            label=None  # legend handled via proxy
        )
        return True

    # 5) Draw recent and upcoming swaths (if present)
    legend_handles = []
    legend_labels  = []

    if recent is not None:
        _add_swath(int(recent["Pass number"]), recent_alpha)
        legend_handles.append(Patch(facecolor=color, edgecolor=color, alpha=recent_alpha))
        lbl = f"Pass {int(recent['Pass number'])} — {recent['First date'].strftime('%Y-%m-%d %H:%M UTC')}"
        legend_labels.append(lbl)

    if upcoming is not None:
        _add_swath(int(upcoming["Pass number"]), upcoming_alpha)
        legend_handles.append(Patch(facecolor=color, edgecolor=color, alpha=upcoming_alpha))
        lbl = f"Pass {int(upcoming['Pass number'])} — {upcoming['First date'].strftime('%Y-%m-%d %H:%M UTC')}"
        legend_labels.append(lbl)

    # 6) Legend (use proxies so it always appears)
    if show_legend and legend_handles:
        kw = dict(frameon=True, fontsize=9)
        if legend_kw:
            kw.update(legend_kw)
        ax.legend(legend_handles, legend_labels, loc=legend_loc, **kw)

    # 7) Optional: set map extent
    if set_extent:
        ax.set_extent([lon_range[0], lon_range[1], lat_range[0], lat_range[1]], crs=ccrs.PlateCarree())

    return {"recent": recent, "upcoming": upcoming}

################## ------------------ INSET SMALL MAP ------------------ ##################

def inset_map(fig, bextent, *, inset_pos=(0.05, 0.75, 0.18, 0.18),
              land_color='0.85', ocean_color='lightsteelblue',
              rect_color='crimson', rect_lw=1.5, coast_lw=0.5):
    """
    Add a small orthographic globe inset to a figure showing the map's global position.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The parent figure to which the inset axes will be added.
    bextent : list or tuple
        Main map extent [lon_min, lon_max, lat_min, lat_max].
    inset_pos : tuple, optional
        Position of the inset [x0, y0, width, height] in figure coordinates.
    land_color : str, optional
        Fill color for land.
    ocean_color : str, optional
        Fill color for ocean.
    rect_color : str, optional
        Color of the bounding box rectangle.
    rect_lw : float, optional
        Line width of bounding box rectangle.
    coast_lw : float, optional
        Line width of coastlines.

    Returns
    -------
    ax_globe : cartopy.mpl.geoaxes.GeoAxesSubplot
        The inset axes created.
    """
    # Center the globe on the middle of your region
    globe_proj = ccrs.Orthographic(
        central_longitude=np.mean(bextent[:2]),
        central_latitude=np.mean(bextent[2:])
    )

    # Create inset axes
    ax_globe = fig.add_axes(inset_pos, projection=globe_proj)
    ax_globe.set_global()

    # Add features
    ax_globe.add_feature(cfeature.LAND, facecolor=land_color, zorder=0)
    ax_globe.add_feature(cfeature.OCEAN, facecolor=ocean_color, zorder=0)
    ax_globe.coastlines(lw=coast_lw, zorder=1)

    # Draw rectangle for main map extent
    rect = Rectangle(
        (bextent[0], bextent[2]),
        bextent[1] - bextent[0],
        bextent[3] - bextent[2],
        edgecolor=rect_color,
        facecolor='none',
        lw=rect_lw,
        transform=ccrs.PlateCarree(),
        zorder=5
    )
    ax_globe.add_patch(rect)

    # Neat border around inset
    for spine in ax_globe.spines.values():
        spine.set_edgecolor('0.2')
        spine.set_linewidth(1)

    return ax_globe

################## ------------------ ADD SG675 DATA ------------------ ##################

def sg675(
    ax,
    *,
    nc_path='/home/databot/share/www/data/SG675_GOUGH_SAMBA/sg675_SG675_Gough_SAMBA_timeseries.nc',
    line_color='0.5',
    line_width=1.5,
    marker='.',
    last_color='gold',
    last_edgecolor='k',
    last_size=100,
    zorder=100
):
    """
    Plot the SG675 Seaglider track and last position on a Cartopy map.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        The Cartopy axis to plot on.
    nc_path : str, optional
        Path to the Seaglider NetCDF timeseries file.
    line_color : str, optional
        Color of the track line.
    line_width : float, optional
        Width of the track line.
    marker : str, optional
        Marker for track points.
    last_color : str, optional
        Fill color for the last-position marker.
    last_edgecolor : str, optional
        Edge color for the last-position marker.
    last_size : int, optional
        Size of the last-position marker.
    zorder : int, optional
        Z-order for layering.

    Returns
    -------
    ds : xarray.Dataset
        The opened dataset (for further use if needed).
    """
    ds = xr.open_dataset(nc_path)

    # Plot glider track
    ax.plot(
        ds.end_longitude,
        ds.end_latitude,
        c=line_color,
        marker=marker,
        lw=line_width,
        transform=ccrs.PlateCarree(),
        label='SG675 Mission #1',
        zorder=11,
        alpha=0.5

    )

    # Plot last glider position
    # ax.scatter(
    #     ds.end_longitude[-1],
    #     ds.end_latitude[-1],
    #     s=last_size,
    #     c=last_color,
    #     edgecolors=last_edgecolor,
    #     transform=ccrs.PlateCarree(),
    #     zorder=zorder,
    #     label='Seaglider last pos'
    # )

    return ds

################## ------------------ ADD SEAGLIDER IMAGE ------------------ ##################

def plot_sg(ds, ax, image_path="../../html/img/platforms/seaglider_yellow2.png", zoom=0.04):
    """
    Plot the latest seaglider position on a Cartopy map, with the glider icon rotated to face
    the direction of the last dive.

    Parameters
    ----------
    ds : xarray.Dataset or similar
        Dataset containing `end_longitude` and `end_latitude` variables.
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        The Cartopy map axes on which to plot the icon.
    image_path : str, optional
        Path to the seaglider image (PNG with transparency).
    zoom : float, optional
        Zoom factor for the image size.
    """

    # ---- Extract last two valid positions ----
    lons = np.asarray(ds.end_longitude).astype(float)
    lats = np.asarray(ds.end_latitude).astype(float)
    valid = np.isfinite(lons) & np.isfinite(lats)

    if valid.sum() < 2:
        raise ValueError("Need at least two valid surfacing positions to compute heading.")

    idx = np.where(valid)[0]
    i2, i1 = idx[-1], idx[-2]
    lon1, lat1 = lons[i1], lats[i1]
    lon2, lat2 = lons[i2], lats[i2]

    # ---- Compute bearing (degrees clockwise from North) ----
    phi1, phi2 = np.deg2rad(lat1), np.deg2rad(lat2)
    dlambda = np.deg2rad(lon2 - lon1)
    y = np.sin(dlambda) * np.cos(phi2)
    x = np.cos(phi1)*np.sin(phi2) - np.sin(phi1)*np.cos(phi2)*np.cos(dlambda)
    azimuth_deg = (np.rad2deg(np.arctan2(y, x)) + 360) % 360

    # ---- Convert to rotation CCW from East ----
    theta_deg = 90.0 - azimuth_deg
    if theta_deg > 180:
        theta_deg -= 360

    if np.isclose(lon1, lon2) and np.isclose(lat1, lat2):
        theta_deg = 0.0

    # ---- Load and rotate the image ----
    img = Image.open(image_path).convert("RGBA")
    img_rot = img.rotate(theta_deg, resample=Image.BICUBIC, expand=True)

    # ---- Create OffsetImage and AnnotationBbox ----
    oi = OffsetImage(np.asarray(img_rot), zoom=zoom)
    ab = AnnotationBbox(
        oi,
        (lon2, lat2),
        xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
        frameon=False,
        box_alignment=(0.5, 0.35)
    )
    ab.set_zorder(12)
    ax.add_artist(ab)

    # Plot the whale survey target position
    target_lon = 17.419
    target_lat = -34.406
    # You can replace these with actual distance and ETA calculations if available
    # ax.scatter(target_lon, target_lat, marker="o", c='r', edgecolors='k', transform=ccrs.PlateCarree(), zorder=12, label='Target')
    
    # Calclate average speed and ETA
    u = np.nanmedian(gsw.distance(ds.start_longitude[-8:], ds.start_latitude[-8:])[0]) / ds.start_time.diff("dive").dt.seconds[-8:].median()
    d = (gsw.distance([lon2,target_lon], [lat2,target_lat])[0])
    kms = int(d / 1000)
    eta_hours = d / u / 3600
    eta = (pd.to_datetime(ds.end_time[-1].values) + pd.Timedelta(hours=eta_hours.item())).strftime("%d %b @ %H:%M")

    return ab, kms, eta  # optional, in case you want to modify or remove later

################## ------------------ ADD WAVE GLIDER DATA ------------------ ##################

def wg1170(
    ax,
    *,
    size="large",
    nc_path="/home/jedholm/share/gliders/waveglider/wg1170/WG_WHIRLS_M2_L1.nc",
    line_color='C1',
    marker='.'):
    """
    Plot the WG1070 Wave Glider track and last position on a Cartopy map.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        The Cartopy axis to plot on.
    nc_path : str, optional
        Path to the Seaglider NetCDF timeseries file.
    line_color : str, optional
        Color of the second mission track line.
    line_width : float, optional
        Width of the track line.
    marker : str, optional
        Marker for track points.
    last_color : str, optional
        Fill color for the last-position marker.
    last_edgecolor : str, optional
        Edge color for the last-position marker.
    last_size : int, optional
        Size of the last-position marker.
    zorder : int, optional
        Z-order for layering.

    Returns
    -------
    ds : xarray.Dataset
        The opened dataset (for further use if needed).
    """
    ds = xr.open_dataset(nc_path)

    ax.plot(
        ds.longitude,
        ds.latitude,
        c="k",
        markeredgecolor="k",
        marker=marker,
        markersize=4 if size == "large" else 6,
        lw=0.5,
        transform=ccrs.PlateCarree(),
        label='Wave Glider Mission #2',
        zorder=11
    )

    ax.plot(
        ds.longitude,
        ds.latitude,
        c=line_color,
        markeredgecolor="None",
        marker=marker,
        markersize=4 if size == "large" else 6,
        lw=0,
        transform=ccrs.PlateCarree(),
        label='Wave Glider Mission #2',
        zorder=12
    )

    ax.plot(
        # np.nanmean(ds.longitude[-3:]),
        ds.longitude[-1],
        # np.nanmean(ds.latitude[-3:]),
        ds.latitude[-1],
        c=line_color,
        marker='o',
        markersize=8 if size == "large" else 10,
        markeredgecolor='k',
        lw=0,
        transform=ccrs.PlateCarree(),
        label='WG-1170 Current Position: ' + pd.to_datetime(ds.time[-1].values).strftime('%d %b %H:%M'),
        zorder=22
    )

    return ds  # optional, in case you want to modify or remove later

################## ------------------ ADD SG267 DATA ------------------ ##################

def sgx(ax, size="large", path="/home/databot/share/www/data/sg267_WHIRLS_Mission2_2026/sg267_mission2_track.csv"):

    df = pd.read_csv(path)
    sg267_lon_fix = df['longitude'].values
    sg267_lat_fix = df['latitude'].values

    ax.scatter(sg267_lon_fix, sg267_lat_fix, s=30 if size == "large" else 100, c='k', marker='.', edgecolor='k', label='SG267 Mission #2', zorder=20, transform=ccrs.PlateCarree())
    ax.scatter(sg267_lon_fix, sg267_lat_fix, s=30 if size == "large" else 100, c='gold', marker='.', edgecolor='None', label='SG267 Mission #2', zorder=20, transform=ccrs.PlateCarree())
    ax.scatter(sg267_lon_fix[-1], sg267_lat_fix[-1], s=50 if size == "large" else 125, c='gold', marker='o', edgecolor='k', label='SG267 Current Position', zorder=21, transform=ccrs.PlateCarree())

    return df

################## ------------------ ADD LEGEND ------------------ ##################

def show_legend(ax, out, *, loc='lower left', fontsize=12, frameon=True):
    """
    Add a standardized legend to a SWOT + Seaglider map.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The map axis to draw the legend on.
    out : dict
        Output from plot_swot_passes() with keys 'recent' and 'upcoming'.
    loc : str, optional
        Legend location (default 'lower left').
    fontsize : int, optional
        Legend font size.
    frameon : bool, optional
        Whether to draw a frame around the legend.
    """
    legend_elements = []

    # Add SWOT pass entries if present
    if out.get('recent') is not None:
        legend_elements.append(
            Patch(facecolor='0.25', edgecolor='0.25', alpha=0.5,
                  label=f"Last SWOT Pass {out['recent']['Pass number']} — "
                        f"{pd.to_datetime(out['recent']['First date']).strftime('%Y-%m-%d %H:%M')}")
        )

    if out.get('upcoming') is not None:
        legend_elements.append(
            Patch(facecolor='0.25', edgecolor='0.25', alpha=0.25,
                  label=f"Next SWOT Pass {out['upcoming']['Pass number']} — "
                        f"{pd.to_datetime(out['upcoming']['First date']).strftime('%Y-%m-%d %H:%M')}")
        )

    # Seaglider proxies
    legend_elements.extend([
        Line2D([0], [0], color='0.5', lw=1, label='SG675 Mission #1'),
        # Line2D([0], [0], color='0.8', lw=1.5, label='Wave Glider Mission #1'),
        Line2D([0], [0], color='C1', lw=2, label='WG-1170 Mission #2'),
        Line2D([0], [0], color='gold', lw=2, label='SG267 Mission #2'),
        Line2D([0], [0], marker='o', linestyle='', markerfacecolor='gold', markeredgecolor='k', label='SG267 Current Position'),
        Line2D([0], [0], marker='o', linestyle='', markerfacecolor='C1', markeredgecolor='k', label='WG-1170 Current Position'),
        #Line2D([0], [0], marker='o', linestyle='', markerfacecolor='r',
        #       markeredgecolor='k', label=f'Whale survey target, {kms} km, ETA: {eta}')
    ])

    # Draw the legend
    ax.legend(handles=legend_elements, loc=loc, frameon=frameon, fontsize=fontsize)

    return ax

######## ------- plot geostrophic velocity ------- ########

fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

plot_gos(ax,fig)
add_sla_contours(ax,c='k')

# add the glider data
sg = sgx(ax)
ds = sg675(ax)
wg = wg1170(ax, line_color='C1')
# wg = plot_wg(wg_lon, wg_lat, ax)

# add small map
inset_map(fig, bextent, inset_pos=(0.05, 0.75, 0.18, 0.18))

# swot 
out = plot_swot_passes(
    ax,
    lon_range=(0, 30),
    lat_range=(-60, -20),
    geometries_file='../../data/swot/KaRIn_2kms_science_geometries.geojson',
    passes_csv='../../data/swot/selected_passes.csv',
    color='0.25',
    recent_alpha=0.45,
    upcoming_alpha=0.20,
    legend_loc='lower left'
)

ax.set_extent(bextent)
add_featuresb(ax)

# ab, kms, eta = plot_sg(ds, ax) # optional, in case you want to add the seaglider icon 

show_legend(ax, out, loc='lower left', fontsize=16)

plt.savefig('/home/databot/share/www/plots/gos_big_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/databot/share/www/html/img/gos_big_latest.png', transparent=True)


######## ------- plot sea level anomaly ------- ########

fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

plot_sla(ax,fig)
add_sla_contours(ax,c='k')

# add the glider data
sg = sgx(ax)
ds = sg675(ax)
wg = wg1170(ax, line_color='C1')
# wg = plot_wg(wg_lon, wg_lat, ax)

# add small map
inset_map(fig, bextent, inset_pos=(0.05, 0.75, 0.18, 0.18))

# swot 
out = plot_swot_passes(
    ax,
    lon_range=(0, 30),
    lat_range=(-60, -20),
    geometries_file='../../data/swot/KaRIn_2kms_science_geometries.geojson',
    passes_csv='../../data/swot/selected_passes.csv',
    color='0.25',
    recent_alpha=0.45,
    upcoming_alpha=0.20,
    legend_loc='lower left'
)

ax.set_extent(bextent)
add_featuresb(ax)

# ab, kms, eta = plot_sg(ds, ax)

show_legend(ax, out, loc='lower left', fontsize=16)

plt.savefig('/home/databot/share/www/plots/sla_big_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/databot/share/www/html/img/sla_big_latest.png', transparent=True)

######## ------- ZOOOOOOOOOOM ------- ########
######## ------- plot sea level anomaly ------- ########

fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

plot_sla(ax,fig)
add_sla_contours(ax,c='k')

# add the glider data
sg = sgx(ax, size="small")
ds = sg675(ax)
wg = wg1170(ax, size="small", line_color='C1')
# wg = plot_wg(wg_lon, wg_lat, ax)

min_lat = sg.latitude.values[-1] - 1
max_lat = sg.latitude.values[-1] + 1
min_lon = sg.longitude.values[-1] - 1.667
max_lon = sg.longitude.values[-1] + 1.667

sextent = [min_lon, max_lon, min_lat, max_lat]

# add small map
inset_map(fig, sextent, inset_pos=(0.05, 0.75, 0.18, 0.18))

# # swot 
# out = plot_swot_passes(
#     ax,
#     lon_range=(0, 30),
#     lat_range=(-60, -20),
#     geometries_file='../../data/swot/KaRIn_2kms_science_geometries.geojson',
#     passes_csv='../../data/swot/selected_passes.csv',
#     color='0.25',
#     recent_alpha=0.45,
#     upcoming_alpha=0.20,
#     legend_loc='lower left'
# )

ax.set_extent(sextent)
add_featuresb(ax, small=True)

# ab, kms, eta = plot_sg(ds, ax)

#show_legend(ax, out, loc='lower left', fontsize=16)

plt.savefig('/home/databot/share/www/plots/sla_zoom_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/databot/share/www/html/img/sla_zoom_latest.png', transparent=True)

######## ------- plot geostrophic velocity ------- ########

fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

plot_gos(ax,fig)
add_sla_contours(ax,c='k')

# add the glider data
sg = sgx(ax,size="small")
#ds = sg675(ax)
wg = wg1170(ax,size="small", line_color='C1')
# wg = plot_wg(wg_lon, wg_lat, ax)

# add small map
inset_map(fig, sextent, inset_pos=(0.05, 0.75, 0.18, 0.18))

# # swot 
# out = plot_swot_passes(
#     ax,
#     lon_range=(0, 30),
#     lat_range=(-60, -20),
#     geometries_file='../../data/swot/KaRIn_2kms_science_geometries.geojson',
#     passes_csv='../../data/swot/selected_passes.csv',
#     color='0.25',
#     recent_alpha=0.45,
#     upcoming_alpha=0.20,
#     legend_loc='lower left'
# )

ax.set_extent(sextent)
add_featuresb(ax, small=True)

# ab, kms, eta = plot_sg(ds, ax) # optional, in case you want to add the seaglider icon 

#show_legend(ax, out, loc='lower left', fontsize=16)

plt.savefig('/home/databot/share/www/plots/gos_zoom_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/databot/share/www/html/img/gos_zoom_latest.png', transparent=True)


# ######## ------- plot geostrophic strain ------- ########

# fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

# plot_strain(ax,fig)
# add_sla_contours(ax,c='k')

# # add the glider data
# ds = sgx(ax)
# ds = sg675(ax)
# wg = wg1070(ax, line_color_m1='0.5', line_color_m2='C1')
# # wg = plot_wg(wg_lon, wg_lat, ax)

# # add small map
# inset_map(fig, bextent, inset_pos=(0.05, 0.75, 0.18, 0.18))

# # swot 
# out = plot_swot_passes(
#     ax,
#     lon_range=(0, 30),
#     lat_range=(-60, -20),
#     geometries_file='../../data/swot/KaRIn_2kms_science_geometries.geojson',
#     passes_csv='../../data/swot/selected_passes.csv',
#     color='0.25',
#     recent_alpha=0.45,
#     upcoming_alpha=0.20,
#     legend_loc='lower left'
# )

# ax.set_extent(bextent)
# add_featuresb(ax)

# # ab, kms, eta = plot_sg(ds, ax) # optional, in case you want to add the seaglider icon 

# show_legend(ax, out, loc='lower left', fontsize=16)

# plt.savefig('/home/databot/share/www/plots/strain_big_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values))
# plt.savefig('/home/databot/share/www/html/img/strain_big_latest.png', transparent=True)