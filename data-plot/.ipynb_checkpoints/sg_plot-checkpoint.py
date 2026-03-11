import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import cmocean.cm as cmo
from matplotlib.dates import DateFormatter, DayLocator, HourLocator
import matplotlib as mpl

font = {'size'   :20}
mpl.rc('font', **font)

mpl.rcParams['xtick.major.size'] = 8
mpl.rcParams['xtick.major.width'] = 2
mpl.rcParams['xtick.minor.size'] = 8
mpl.rcParams['xtick.minor.width'] = 1
mpl.rcParams['ytick.major.size'] = 8
mpl.rcParams['ytick.major.width'] = 2
mpl.rcParams['ytick.minor.size'] = 8
mpl.rcParams['ytick.minor.width'] = 1

# load data
dirName="/home/databot/share/MISSIONS/quicche/sg675/"
# fileName="p6750011.nc"
# fileName="sg675_SG675_QUICCHE_deployment_timeseries.nc"
filenames=dirName+"p6750*.nc"
# fileName="sg675_SG675_QUICCHE_deployment_1.0m_up_and_down_profile.nc"


import glidertools as gt

names = [
    'ctd_depth',
    'ctd_time',
    'ctd_pressure',
    'salinity',
    'temperature',
    'eng_wlbb2flvmt_Chlsig',
    'eng_wlbb2flvmt_wl470sig',
    'eng_wlbb2flvmt_wl700sig',
    'aanderaa4831_dissolved_oxygen',
    'eng_qsp_PARuV',
]

ds_dict = gt.load.seaglider_basestation_netCDFs(
    filenames, names,
    return_merged=True,
    keep_global_attrs=False
)



ds = ds_dict['sg_data_point']

fig,ax=plt.subplots(3,1,figsize=[20,12],sharex=True,constrained_layout=True)

# plt.suptitle('SG675')
c1=ax[0].scatter(ds.ctd_time_dt64[::30],ds.ctd_depth[::30],c=ds.temperature[::30],cmap=cmo.thermal,vmin=2,vmax=22)
ax[0].set_ylim(1000,0)
cs1=plt.colorbar(c1,ax=ax[0])
cs1.set_label('$^o$C')
ax[0].text(0.01,0.85,'Temperature',bbox=dict(facecolor='white', alpha=0.5), transform=ax[0].transAxes)



c2=ax[1].scatter(ds.ctd_time_dt64[::30],ds.ctd_depth[::30],c=ds.salinity[::30],cmap=cmo.haline,vmin=34.2,vmax=35.3)
ax[1].set_ylim(1000,0)
cs2=plt.colorbar(c2,ax=ax[1])
cs2.set_label('PSU')

ax[1].text(0.01,0.85,'Salinity',bbox=dict(facecolor='white', alpha=0.5), transform=ax[1].transAxes)

c3=ax[2].scatter(ds.ctd_time_dt64[::30],ds.ctd_depth[::30],c=ds.aanderaa4831_dissolved_oxygen[::30],cmap="Spectral_r",vmin=150,vmax=200)
ax[2].set_ylim(1000,0)
fig.autofmt_xdate()
cs3=plt.colorbar(c3,ax=ax[2])
ax[2].text(0.01,0.85,'Oxygen',bbox=dict(facecolor='white', alpha=0.5), transform=ax[2].transAxes)
cs3.set_label('micromoles/kg')

plt.savefig('/home/isgiddy/share/www/html/img/SG675.png',dpi=300,bbox_inches='tight')


#meta

id=np.repeat('SG675',len(ds.ctd_time_dt64))    
meta = pd.DataFrame(data={'time':ds.ctd_time_dt64.values,
                     'lon':ds.longitude.values,
                     'lat':ds.latitude.values,
                     'id':id})
meta.to_csv('/home/isgiddy/share/www/data/SG675_meta_20230322.csv')