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

sst = xr.open_dataset('/home/isgiddy/share/www/data/sst_latest.nc',engine='netcdf4').sel(lat=slice(-70,-50),lon=slice(-15,15)).squeeze()
#fsle = xr.open_dataset('/home/isgiddy/share/www/data/fsle.nc').sel(lat=slice(-45,-30),lon=slice(0,25)).squeeze()
adt = xr.open_dataset('/home/isgiddy/share/www/data/adt_latest.nc').sel(latitude=slice(-70,-50),longitude=slice(-15,15)).squeeze()
seaice = xr.open_dataset('/home/isgiddy/share/www/data/seaice_latest.nc')
seaice_coords = xr.open_dataset('/home/isgiddy/share/www/data/LongitudeLatitudeGrid-s6250-Antarctic.hdf')
# Read the gliders metadata
#sb1812 = pd.read_csv('')
#sb2326 = pd.read_csv('')
#sg675  = pd.read_csv('')
#se057  = pd.read_csv('')
#se070  = pd.read_csv('')





#SG
# dirName="/home/databot/share/MISSIONS/quicche/sg675/"
# fileName="/home/isgiddy/share/www/data/sg675_SG675_QUICCHE_deployment_1.0m_up_and_down_profile.nc"
# SG=xr.open_dataset(dirName+fileName)

#SG=pd.read_csv('/home/isgiddy/share/www/data/SG675_meta_20230322.csv')


#Others

#SB=pd.read_csv('/home/isgiddy/share/www/data/SB1812D.csv')
#SB2=pd.read_csv('/home/isgiddy/share/www/data/Pimpim_meta_20230322.csv')

#SE70=pd.read_csv('/home/isgiddy/share/www/data/SEA070_20230306.csv')
#SE57=pd.read_csv('/home/isgiddy/share/www/data/SEA057_20230307.csv')

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

def add_platforms(ax):
    
    # ax.scatter(17.8,35.2,marker='x',s=40,label='bifurcation',transform=ccrs.PlateCarree())
    # plt.scatter(df.lon.iloc[-10000:][::50],df.lat.iloc[-10000:][::50])
    ax.scatter(SG.lon.iloc[:][::50],SG.lat.iloc[:][::50],marker='.',
            edgecolors='green',facecolors="green",
               s=30,transform=ccrs.PlateCarree(),label='SG675',zorder=8,)
    
    ax.scatter(SG.lon.iloc[-1],SG.lat.iloc[-1],marker='.',c='k',s=30,transform=ccrs.PlateCarree(),zorder=8 )

    
    ax.scatter(wg.longitude.iloc[-500:],wg.latitude.iloc[-500:],marker='.',c='hotpink',s=30,transform=ccrs.PlateCarree(),zorder=6,label='waveglider'
              )
    ax.scatter(wg.longitude.iloc[-2],wg.latitude.iloc[-2],marker='.',c='k',s=30,transform=ccrs.PlateCarree(),zorder=6
              )
    
    ax.scatter(SB.Long.iloc[-500:],SB.Lat.iloc[-500:],marker='.',c='tab:blue',s=30,transform=ccrs.PlateCarree(),zorder=6,label='SB-Kringla'
              )
    ax.scatter(SB.Long.iloc[-1],SB.Lat.iloc[-2],marker='.',c='k',s=30,transform=ccrs.PlateCarree(),zorder=6
              )
    
    ax.scatter(SB2.lon.iloc[-500:],SB2.lat.iloc[-500:],marker='.',c='darkblue',s=30,transform=ccrs.PlateCarree(),zorder=9,label='SB-PimPim'
              )
    ax.scatter(SB2.lon.iloc[-1],SB2.lat.iloc[-1],marker='.',c='w',s=30,transform=ccrs.PlateCarree(),zorder=9
              )
    
    ax.scatter(SE70.longitude.iloc[-500:],SE70.latitude.iloc[-500:],marker='v',
               facecolors="None",
               edgecolors='tab:orange',
               s=30,transform=ccrs.PlateCarree(),zorder=7,label='SE070'
              )
    ax.scatter(SE70.longitude.iloc[-1],SE70.latitude.iloc[-1],marker='v',
               c="k",
               edgecolors='tab:orange',
               s=30,transform=ccrs.PlateCarree(),zorder=7
              )
    ax.scatter(SE57.longitude.iloc[-500:],SE57.latitude.iloc[-500:],
               marker='^',
               facecolors="None",
               edgecolors='tab:red',
               s=30,transform=ccrs.PlateCarree(),zorder=6,label='SE057')
              
    ax.scatter(SE57.longitude.iloc[-1],SE57.latitude.iloc[-1],marker='^',
               edgecolors='tab:red',facecolors='k',s=30,transform=ccrs.PlateCarree(),zorder=6
              ) 

    ax.legend(loc='lower right')
    
    
def add_sla_contours(ax,c):
    ax.contour(adt.longitude, adt.latitude,
                    adt.sla.squeeze(),
                    linewidths=0.75, alpha=1,
                    levels=np.arange(-2, 2, 0.1), colors=c,zorder=2)
    


def plot_gos(ax):
    
    image = ax.contourf(adt.longitude, adt.latitude,
                         adt.gos,
                         levels=np.arange(0, 1.6, 0.05),
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
    # ax.set_title('{}'.format(adt.time.data))
    ax.set_title(adt.time.values.astype('datetime64[D]'),y=1,x=0.5)

    
def plot_fsle(ax):
    im = ax.pcolor(fsle.lon,fsle.lat,fsle.lambda1.T,cmap='viridis',zorder=1)
    plt.colorbar(im,ax=ax, label="FLE associated to the maximum eigenvalues\nof Cauchy-Green strain tensor (day$^{-1}$)",pad=0.01)
    
# def plot_sst(ax):
#     im = ax.pcolor(sst.lon,sst.lat,sst['analysed_sst'],cmap=cmo.thermal,vmin=15,vmax=25,zorder=1)
#     plt.colorbar(im,ax=ax, label='Sea surface temperature (°C)\nGHRSST MUR',pad=0.01)
#     ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)

# def plot_sst_g(ax):
#     im = ax.pcolor(sst.lon,sst.lat,sst.gradient,cmap=cmo.thermal,vmin=0,vmax=0.1,zorder=1)
#     plt.colorbar(im,ax=ax, label='Sea surface temperature gradient (°C/km)\nGHRSST MUR',pad=0.01)
#     ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)

def plot_sla(ax):
    im = ax.pcolor(adt.longitude,adt.latitude,adt.sla,cmap=cmo.balance,vmin=-1,vmax=1,zorder=1)
    plt.colorbar(im,ax=ax, label='Sea level anomaly (m)\nAVISO',pad=0.01,shrink=0.6)
    ax.set_title(adt.time.values.astype('datetime64[D]'),y=1,x=0.5)

big = [True,True,True,True,True,False,False,False,False,False]
for i in range(10):
    fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

  #  add_swath(ax)
  #  add_platforms(ax)
    
    if i in [0,2,3,4,6,8,9,10]: # FSLE does not need contours
        add_sla_contours(ax,'w')
    if i in [5,11]: # FSLE does not need contours
        add_sla_contours(ax,'k')
    
    if big[i] == True:
        extent = bextent
        add_featuresb(ax,True)

        add_box(ax)
      # add_moorings(ax,1)
        save = 'big'

    else:
        extent = sextent
        add_features(ax,True)

        # add_platforms(ax)

       # add_M1(ax,-1)
        save = 'small'

    if (i == 0) | (i == 6):
        plot_gos(ax)
        ax.set_extent(extent)
        plt.savefig('/home/isgiddy/share/www/plots/gos_{}_{}.png'.format(save,adt.time.dt.strftime("%Y%m%d").values))
        plt.savefig('/home/isgiddy/share/www/html/img/gos_{}_latest.png'.format(save))
    
  #  if (i == 1) | (i == 7):
      #  plot_fsle(ax)
       # ax.set_title(f"Advection time: {fsle.attrs['advection_time'][:-9]} from {fsle.attrs['start_time'][:-9]}")
      #  ax.set_extent(extent)
      #  plt.savefig('/home/isgiddy/share/www/plots/fsle_{}_{}_{}_days.png'.format(save,fsle.attrs['start_time'][:-9],int(fsle.attrs['advection_time'][:2])))
      #  plt.savefig('/home/isgiddy/share/www/html/img/fsle_{}_latest.png'.format(save))
    if (i == 2) | (i == 8):
         plot_sst(ax)
         ax.set_extent(extent)
         plt.savefig('/home/isgiddy/share/www/plots/sst_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
         plt.savefig('/home/isgiddy/share/www/html/img/sst_{}_latest.png'.format(save))
    if (i == 3) | (i == 9):
         plot_sst_g(ax)
         ax.set_extent(extent)
         plt.savefig('/home/isgiddy/share/www/plots/sst_g_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
         plt.savefig('/home/isgiddy/share/www/html/img/sst_g_{}_latest.png'.format(save))
    if (i == 4) | (i == 10):
        plot_sla(ax)
        ax.set_extent(extent)
        plt.savefig('/home/isgiddy/share/www/plots/sla_{}_{}.png'.format(save,adt.time.dt.strftime("%Y%m%d").values))
        plt.savefig('/home/isgiddy/share/www/html/img/sla_{}_latest.png'.format(save))
