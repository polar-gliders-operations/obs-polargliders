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
import geopandas as gpd

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

sst = xr.open_dataset('/home/isgiddy/share/www/data/sst_latest.nc',engine='netcdf4').sel(lat=slice(-45,-30),lon=slice(0,25)).squeeze()

swath = gpd.read_file('/home/isgiddy/share/www/data/swot/swot_calval_orbit_june2015-v2_swath.shp')


#plotform positions
import json
import pandas as pd
import glob
from datetime import datetime

wg_files = glob.glob('/home/isgiddy/share/www/data/waveglider/2023*.csv')
wg = pd.concat((pd.read_csv(filename) for filename in wg_files[::-1]), ignore_index=True)

date=[]
for i in range (len(wg.Datetime)):
    datetime_str =wg.Datetime[i]

    dateobject = (datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S'))
    date.append(np.datetime64(dateobject))
    
wg['time'] = np.array(date)
wg=wg.sort_values('time')
wg=wg.drop_duplicates('time')

def parseGPS(sxGPS):    ## CALCULATE SUBSURFACE LAT / LON (TODO: USING DEAD RECKONING)
    return np.sign(sxGPS) * (np.fix(np.abs(sxGPS)/100) + np.mod(np.abs(sxGPS),100)/60)

wg['longitude'] = parseGPS(wg['Longitude'])
wg['latitude'] = parseGPS(wg['Latitude'])


SB=pd.read_csv('/home/isgiddy/share/www/data/SB1812D.csv')
SE70=pd.read_csv('/home/isgiddy/share/www/data/SEA070_20230306.csv')
SE57=pd.read_csv('/home/isgiddy/share/www/data/SEA057_20230307.csv')



# Calculate dx and dy for each grid cell
lons, lats = np.meshgrid(sst.lon,sst.lat)
diff_lons = gsw.distance(lons,lats)
diff_lats = gsw.distance(lons.T,lats.T).T

# Calculate sst gradient and gos magnitude
sst['gradient'] = ((sst['analysed_sst'].diff('lat')/diff_lats)**2 + (sst['analysed_sst'].diff('lon')/diff_lons)**2)**(1/2)*1000


# Moorings
M1 = [16.049411,-37.157775] # When the moorings are deployed, these values might need to be updated to reflect the actual locations
M2 = [13.472228,-35.970445]

# Extens for the big map and the subset
bextent = [9.99,25.01,-40.01,-29.99] # Big extent
sextent = [15.5,18,-38.0,-36.5] # Small extent

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
    
    
    
def add_platforms(ax):
    ax.scatter(wg.longitude,wg.latitude,marker='.',c='hotpink',s=30,transform=ccrs.PlateCarree(),zorder=6,label='waveglider'
              )
    ax.scatter(wg.longitude.iloc[-1],wg.latitude.iloc[-2],marker='.',c='k',s=30,transform=ccrs.PlateCarree(),zorder=6
              )
    
    ax.scatter(SB.Long,SB.Lat,marker='.',c='tab:blue',s=30,transform=ccrs.PlateCarree(),zorder=6,label='SB-Kringla'
              )
    ax.scatter(SB.Long.iloc[-1],SB.Lat.iloc[-2],marker='.',c='k',s=30,transform=ccrs.PlateCarree(),zorder=6
              )
    
    ax.scatter(SE70.longitude,SE70.latitude,marker='v',
               facecolors="None",
               edgecolors='tab:orange',
               s=30,transform=ccrs.PlateCarree(),zorder=7,label='SE070'
              )
    ax.scatter(SE70.longitude.iloc[-1],SE70.latitude.iloc[-2],marker='v',
               c="k",
               edgecolors='tab:orange',
               s=30,transform=ccrs.PlateCarree(),zorder=7
              )
    ax.scatter(SE57.longitude,SE57.latitude,
               marker='^',
               facecolors="None",
               edgecolors='tab:red',
               s=30,transform=ccrs.PlateCarree(),zorder=6,label='SE057')
              
    ax.scatter(SE57.longitude.iloc[-1],SE57.latitude.iloc[-1],marker='^',
               edgecolors='tab:red',facecolors='k',s=30,transform=ccrs.PlateCarree(),zorder=6
              )
    
    ax.legend(loc='upper left')
    
    
def add_moorings(ax,d):
    
    ax.scatter(M1[0],M1[1],marker='o',fc='w',s=200,zorder=6,ec='k',lw=2)
    ax.text(M1[0]+.0025*d,M1[1]-.01,'1',c='k',zorder=6,ha='center',va='center',fontsize=10)
    
    ax.scatter(M2[0],M2[1],marker='o',fc='w',s=200,zorder=6,ec='k',lw=2)
    ax.text(M2[0]+0.0025*d,M2[1]-0.01,'2',c='k',zorder=6,ha='center',va='center',fontsize=10)
    
def add_M1(ax,d):
    
    ax.scatter(M1[0],M1[1],marker='o',fc='w',s=200,zorder=6,ec='k',lw=2)
    ax.text(M1[0]+.0025*d,M1[1]-.01,'1',c='k',zorder=6,ha='center',va='center',fontsize=10)
    
    # ax.scatter(M2[0],M2[1],marker='o',fc='w',s=200,zorder=6,ec='k',lw=2)
    # ax.text(M2[0]+0.0025*d,M2[1]-0.01,'2',c='k',zorder=6,ha='center',va='center',fontsize=10)

def add_box(ax):
    ax.plot([12,18],[-34,-34],c='w',lw=2,ls='--',zorder=5)
    ax.plot([12,18],[-38,-38],c='w',lw=2,ls='--',zorder=5)
    ax.plot([12,12],[-34,-38],c='w',lw=2,ls='--',zorder=5)
    ax.plot([18,18],[-34,-38],c='w',lw=2,ls='--',zorder=5)
    
def add_swath(ax):
    Swath = ax.add_geometries(swath.geometry, crs=ccrs.PlateCarree(),zorder=4)
    Swath._kwargs['facecolor'] = 'w'
    Swath._kwargs['edgecolor'] = 'k'
    Swath._kwargs['alpha'] = 0.25
    
    
    
def plot_sst(ax):
    im = ax.pcolor(sst.lon,sst.lat,sst['analysed_sst'],cmap=cmo.thermal,vmin=15,vmax=25,zorder=1)
    plt.colorbar(im,ax=ax, label='Sea surface temperature (°C)\nGHRSST MUR',pad=0.01)
    ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)
    
    
def plot_sst_g(ax):
    im = ax.pcolor(sst.lon,sst.lat,sst.gradient,cmap=cmo.thermal,vmin=0,vmax=0.1,zorder=1)
    plt.colorbar(im,ax=ax, label='Sea surface temperature gradient (°C/km)\nGHRSST MUR',pad=0.01)
    ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)
    
def add_sla_contours(ax,c):
    ax.contour(adt.longitude, adt.latitude,
                    adt.sla.squeeze(),
                    linewidths=0.75, alpha=1,
                    levels=np.arange(-2, 2, 0.1), colors=c,zorder=2)


fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)


add_swath(ax)
add_platforms(ax)

add_sla_contours(ax,'w')
extent = bextent
add_featuresb(ax,True)

add_box(ax)
add_moorings(ax,1)
save = 'big'
plot_sst(ax)
ax.set_extent(extent)
plt.savefig('/home/isgiddy/share/www/plots/sst_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/isgiddy/share/www/html/img/sst_{}_latest.png'.format(save))


fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)
add_swath(ax)
add_platforms(ax)
add_sla_contours(ax,'w')
extent = sextent
add_features(ax,True)
add_M1(ax,-1)
save = 'small'

plot_sst(ax)
ax.set_extent(extent)
plt.savefig('/home/isgiddy/share/www/plots/sst_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/isgiddy/share/www/html/img/sst_{}_latest.png'.format(save))


fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)


add_swath(ax)
add_platforms(ax)

add_sla_contours(ax,'w')
extent = bextent
add_featuresb(ax,True)

add_box(ax)
add_moorings(ax,1)
save = 'big'
plot_sst_g(ax)
ax.set_extent(extent)
plt.savefig('/home/isgiddy/share/www/plots/sst_g_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/isgiddy/share/www/html/img/sst_g_{}_latest.png'.format(save))


fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)
add_swath(ax)
add_platforms(ax)
add_sla_contours(ax,'w')
extent = sextent
add_features(ax,True)
add_M1(ax,-1)
save = 'small'

plot_sst_g(ax)
ax.set_extent(extent)
plt.savefig('/home/isgiddy/share/www/plots/sst_g_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
plt.savefig('/home/isgiddy/share/www/html/img/sst_g_{}_latest.png'.format(save))
