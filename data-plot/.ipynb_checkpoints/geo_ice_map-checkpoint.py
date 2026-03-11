## Plot map of aviso geostrophic velocitites and sea ice concentration

import xarray as xr
import gsw
import matplotlib.dates as mdates
from cmocean import cm as cmo  
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib
#import geopandas as gpd
import os

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

# Load the data

#sst = xr.open_dataset('/home/isgiddy/share/www/data/sst_latest.nc',engine='netcdf4').sel(lat=slice(-70,-50),lon=slice(-15,15)).squeeze()
#fsle = xr.open_dataset('/home/isgiddy/share/www/data/fsle.nc').sel(lat=slice(-45,-30),lon=slice(0,25)).squeeze()
adt = xr.open_dataset('/home/isgiddy/share/www/data/adt_latest.nc').sel(latitude=slice(-70,-50),longitude=slice(-15,25)).squeeze()
seaice = xr.open_dataset('/home/isgiddy/share/www/data/seaice_latest.nc')
seaice_coords = xr.open_dataset('/home/isgiddy/share/www/data/LongitudeLatitudeGrid-s6250-Antarctic.hdf',engine='pynio')
try:
    seaice['zm']=xr.DataArray(np.where(seaice.z==0.,np.nan,seaice.z),dims=({'x','y'}))
except:
    seaice['zm']=xr.DataArray(np.where(seaice.z==0.,np.nan,seaice.z).T,dims=({'x','y'})).T
    
    
adt['gos'] = (('latitude', 'longitude'), np.sqrt(adt.ugos**2+adt.vgos**2).data)


# Extens for the big map and the subset
bextent = [-5,20,-70,-50] # Big extent
sextent = [14,18,-61,-59] # Small extent

def add_featuresb(ax,left):
    
    ax.add_feature(cfeature.LAND,   facecolor='0.8',edgecolor='k',zorder=3)
    ax.add_feature(cfeature.RIVERS, edgecolor='w'  ,zorder=3)
    ax.add_feature(cfeature.LAKES,  facecolor='w'  ,zorder=3)
    ax.set(xlabel='',ylabel='')

    gls = ax.gridlines(crs=ccrs.PlateCarree(), 
                        draw_labels=True,
                        x_inline=False, 
                        y_inline=False,
                        linewidth=0.75,
                        alpha=0.75, 
                        linestyle='--', 
                        color='w',
                        ylocs=matplotlib.ticker.MultipleLocator(base=2),
                        xlocs=matplotlib.ticker.MultipleLocator(base=2))

    gls.top_labels = False
    gls.bottom_labels = True
    gls.right_labels = False    
    gls.left_labels = left
    gls.xpadding=10
    gls.ypadding=10   

def add_features(ax,left):
    
    ax.add_feature(cfeature.LAND,   facecolor='0.8',edgecolor='k',zorder=3)
    ax.add_feature(cfeature.RIVERS, edgecolor='w'  ,zorder=3)
    ax.add_feature(cfeature.LAKES,  facecolor='w'  ,zorder=3)
    ax.set(xlabel='',ylabel='')

    gls = ax.gridlines(crs=ccrs.PlateCarree(), 
                        draw_labels=True,
                        x_inline=False, 
                        y_inline=False,
                        linewidth=0.75,
                        alpha=0.75, 
                        linestyle='--', 
                        color='w',
                        ylocs=matplotlib.ticker.MultipleLocator(base=0.5),
                        xlocs=matplotlib.ticker.MultipleLocator(base=0.5))

    gls.top_labels = False
    gls.bottom_labels = True
    gls.right_labels = False    
    gls.left_labels = left
    gls.xpadding=10
    gls.ypadding=10   
    

    
# 

def plot_gos(ax):
    
    image = ax.contourf(adt.longitude, adt.latitude,
                         adt.gos,
                         levels=np.arange(0, 0.5, 0.05),
                         cmap=plt.get_cmap('cmo.speed',31), extend='max',
                         transform=ccrs.PlateCarree(),zorder=1)
    
    vctrs = ax.quiver(adt.longitude[::1], adt.latitude[::1],
                       adt.ugos[::1, ::1], adt.vgos[::1, ::1],
                       scale=2.5e1, alpha=0.8, headaxislength=5, headlength=5, headwidth=5, width=1e-3,
                       transform=ccrs.PlateCarree(),zorder=1)
    
    cb = plt.colorbar(image,ax=ax,pad=0.01,shrink=0.6)
    
    
    qk = ax.quiverkey(vctrs, 0.855, 1.025, 0.5, '0.5 m s$^{-1}$', labelpos='E',
                   coordinates='axes',zorder=6,color='k')
    
    
    cb.set_label('Geostrophic velocity (m s$^{-1}$)\nAVISO', labelpad=20)
    
    cs = ax.pcolormesh(seaice_coords.Longitudes,seaice_coords.Longitudes,seaice.z,cmap=cmo.ice,
                      transform=ccrs.PlateCarree(),zorder=1)
    # ax.set_title('{}'.format(adt.time.data))
    ax.set_title(adt.time.values.astype('datetime64[D]'),y=1,x=0.5)
    
    
## Finally plot and save
fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

plot_gos(ax)
cs = ax.pcolormesh(seaice_coords.Longitudes,seaice_coords.Latitudes,seaice.zm,cmap=cmo.ice,
                      transform=ccrs.PlateCarree(),zorder=1)
ax.set_extent(bextent)
add_featuresb(ax,True)

plt.savefig('/home/isgiddy/share/www/html/img/gos_ice_big_latest.png')
plt.savefig('/home/isgiddy/share/www/plots/gos_big_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values))

