import datetime
import pandas as pd
from erddapy import ERDDAP
from tqdm.notebook import tqdm
import glidertools as gt
import matplotlib.dates as mdates
import matplotlib
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime
import cartopy
import cartopy.crs as ccrs
import gsw
from cmocean import cm as cmo  
import matplotlib as mpl
import warnings
import sys
#sys.path.append('../data-load')
sys.path.append('/home/isgiddy/share/www/src/data-load')

import utils as seu

warnings.simplefilter(action='ignore', category=FutureWarning)

font = {'weight' : 'normal',
        'size'   : 30}
mpl.rc('font', **font)

mpl.rcParams['xtick.major.size'] = 8
mpl.rcParams['xtick.major.width'] = 1
mpl.rcParams['xtick.minor.size'] = 8
mpl.rcParams['xtick.minor.width'] = 1
mpl.rcParams['ytick.major.size'] = 8
mpl.rcParams['ytick.major.width'] = 1
mpl.rcParams['ytick.minor.size'] = 8
mpl.rcParams['ytick.minor.width'] = 1

def rot_ticks(axs,rot,ha):
    for xlabels in axs.get_xticklabels():
                xlabels.set_rotation(rot)
                xlabels.set_ha(ha)
                
def fix_xticks(ax,ds):
    
    if (ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 1 :
        ax.xaxis.set_minor_locator(mdates.HourLocator())
        ax.xaxis.set_major_locator(mdates.HourLocator(np.arange(0,24,3)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter(""))
        #ax.set_xlabel(f"{ds.time[0].values.astype('datetime64[D]')}")

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') >= 1) and ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 7):
        ax.xaxis.set_minor_locator(mdates.HourLocator([0,12]))
        ax.xaxis.set_major_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 6) and ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 15):
        ax.xaxis.set_minor_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax.xaxis.set_major_locator(mdates.DayLocator(np.arange(2,32,2)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter(""))
        ax.set_xlabel('2023')

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 14) and ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 31):
        ax.xaxis.set_minor_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax.xaxis.set_major_locator(mdates.DayLocator([5,10,15,20,25,30]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        #ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%d"))

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 30):
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator([1,5,10,15,20,25]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%B"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    
    rot_ticks(ax,0,'center')
    
def save_csv(ds,prof_id):
    df = ds.where((ds['profile_num'].diff('time'))==1,drop=True).reset_coords()[['time','longitude','latitude']].to_pandas().reset_index()
    df['time'] = df['time'].values.astype('datetime64[s]')
    df.loc[-1] = ds.reset_coords()[['time','longitude','latitude']].to_pandas().reset_index().iloc[0]
    df.index = df.index + 1  # shifting index
    df.sort_index(inplace=True) 
    df['platform_id'] = [prof_id]*len(df.time)
    df.to_csv(f"/home/isgiddy/share/www/data/{prof_id}_{df['time'].dt.strftime('%Y%m%d')[0]}.csv")
    #df.to_csv(f"../data/{prof_id}_{df['time'].dt.strftime('%Y%m%d')[0]}.csv")
    return df

def SEA070_plot(ds,df):
    
    var = ['temperature','salinity','chlorophyll','oxygen_concentration','nitrate_concentration']
    qc = [1,1,1,3,]
    cmap = [cmo.thermal,cmo.haline,cmo.delta,cmo.dense,cmo.matter]
    x = gt.utils.time_average_per_dive(ds['profile_num'],ds['time'])
    y = ds['depth']
    
    fig, ax = plt.subplots(len(var),1,figsize=(20,4*len(var)),sharex=True,constrained_layout=True)

    for i,axs in enumerate(ax):
        
        z = gt.grid_data(x,y,ds[var[i]],bins=np.arange(0,ds['depth'].max()+5,2))
        if var[i] == 'chlorophyll':
            # pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,vmin=ds[var[i]].min(), vmax=ds[var[i]].max())
            pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,vmin=0,vmax=2)

            # pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,norm=mpl.colors.LogNorm(vmin=ds[var[i]].min(), vmax=ds[var[i]].max()))
        else:
            # pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,vmin=np.nanpercentile(ds[var[i]].data, 0.5),vmax = np.nanpercentile(ds[var[i]].data, 99.5))
            pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,robust=True)

        if var[i] == 'salinity':
            plt.colorbar(pcm,ax=axs,label=f"(PSU)",pad=0.01)    
        else:
            if var[i] == 'chlorophyll':
                plt.colorbar(pcm,ax=axs,label=f"(log {ds[var[i]].attrs['units']})",pad=0.01)    
            else:    
                plt.colorbar(pcm,ax=axs,label=f"({ds[var[i]].attrs['units']})",pad=0.01)    
        
        axs.set_title(ds[var[i]].attrs['long_name'].capitalize(),loc='left',y=1.02)
        axs.set(xlabel='',ylabel='Depth (m)')
        axs.invert_yaxis()
    fig.autofmt_xdate()

    ax[0].set_title(ds.attrs['glider_model'] + ' 0' +ds.attrs['glider_serial'],fontsize=40)
    fix_xticks(axs,ds)
    plt.savefig(f"/home/isgiddy/share/www/plots/SEA0{ds.attrs['glider_serial']}_{df['time'].dt.strftime('%Y%m%d')[0]}.png")
    plt.savefig(f"/home/isgiddy/share/www/html/img/SEA0{ds.attrs['glider_serial']}_{df['time'].dt.strftime('%Y%m%d')[0]}.png") 
   
# plt.savefig(f"../plots/SEA0{ds.attrs['glider_serial']}_{df['time'].dt.strftime('%Y%m%d')[0]}.png")
    return

def SEA057_plot(ds,df):
    
    var = ['temperature','salinity','chlorophyll','oxygen_concentration','tke_dissipation_shear_1']
    qc = [1,1,1,3]
    cmap = [cmo.thermal,cmo.haline,cmo.delta,cmo.dense]
    x = gt.utils.time_average_per_dive(ds['profile_num'],ds['time'])
    y = ds['depth']
    
    fig, ax = plt.subplots(len(var),1,figsize=(20,4*len(var)),sharex=True,constrained_layout=True)

    for i,axs in enumerate(ax):
        z = gt.grid_data(x,y,ds[var[i]],bins=np.arange(0,ds['depth'].max()+5,2))

        if var[i] == 'tke_dissipation_shear_1':
                        
            pcm = z.plot(ax=ax[i], add_colorbar=False,
                         norm=mpl.colors.LogNorm(vmin=1e-10,vmax=1e-6),cmap=plt.cm.afmhot_r)

        elif var[i] == 'chlorophyll':
            # pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,vmin=ds[var[i]].min(), vmax=ds[var[i]].max())
            pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,vmin=0,vmax=2)

            # pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,norm=mpl.colors.LogNorm(vmin=ds[var[i]].min(), vmax=ds[var[i]].max()))
        else:
            # pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,vmin=np.nanpercentile(ds[var[i]].data, 0.5),vmax = np.nanpercentile(ds[var[i]].data, 99.5))
            pcm = z.plot(cmap=cmap[i], ax=ax[i], add_colorbar=False,robust=True)
        if var[i] == 'salinity':
            plt.colorbar(pcm,ax=axs,label=f"(PSU)",pad=0.01)    
        else:
            plt.colorbar(pcm,ax=axs,label=f"({ds[var[i]].attrs['units']})",pad=0.01)    
        
        axs.set_title(ds[var[i]].attrs['long_name'].capitalize(),loc='left',y=1.02)
        axs.set(xlabel='',ylabel='Depth (m)')
        axs.invert_yaxis()
    fig.autofmt_xdate()

    ax[0].set_title(ds.attrs['glider_model'] + ' 0' +ds.attrs['glider_serial'],fontsize=40)
    
    fix_xticks(axs,ds)
    plt.savefig(f"/home/isgiddy/share/www/plots/SEA0{ds.attrs['glider_serial']}_{df['time'].dt.strftime('%Y%m%d')[0]}.png")
    plt.savefig(f"/home/isgiddy/share/www/html/img/SEA0{ds.attrs['glider_serial']}_{df['time'].dt.strftime('%Y%m%d')[0]}.png")


    #plt.savefig(f"../plots/SEA0{ds.attrs['glider_serial']}_{df['time'].dt.strftime('%Y%m%d')[0]}.png")
    return


# These names has to be changed once the mission is up and running, and we know the correct mission number. These ones are placeholders tom make sure the code runs on the server
sea057 = 'nrt_SEA057_M75'
sea070 = 'nrt_SEA070_M29'

# Download the datasets
datasets_to_download = [sea057,sea070,]
ds_dict = seu.download_glider_dataset(datasets_to_download, nrt_only=True)

# Split into separate datasets and specify units and add a coordinate
SE1 = ds_dict[sea057]
SE1 = SE1.set_coords('profile_num')
SE1['salinity'].attrs['units'] = 'PSU'

SE2 = ds_dict[sea070]
SE2 = SE2.set_coords('profile_num')
SE2['salinity'].attrs['units'] = 'PSU'

# Save the coordinates for the beginning of each dive.
df1 = save_csv(SE1,'SEA057')
df2 = save_csv(SE2,'SEA070')

# Plot sections and save as png
# glider_plot(SE1,df1)
SEA070_plot(SE2,df2)
SEA057_plot(SE1,df1)
