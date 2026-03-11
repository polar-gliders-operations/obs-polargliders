import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import os
import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%d-%m-%y')

from datetime import datetime
import numpy as np
import glob


import matplotlib as mpl
font = {'size'   : 18}

mpl.rc('font', **font)

from matplotlib.colors import ListedColormap, LinearSegmentedColormap
wind_c2 = ListedColormap(['#FCC681','#FF819E','#FF819E','#A0A3E0','#A0A3E0','#99D4E5','#99D4E5','#FCC681']) # Soft pastels, use this


fig,ax=plt.subplots(2,1,figsize=[20,8],sharex=True,constrained_layout=True)

wg_weather = pd.read_csv('/home/isgiddy/share/www/data/waveglider/weather/sv3_052_weather.csv')

date=[]
for i in range (len(wg_weather.TimeStamp)):
    datetime_str = wg_weather.TimeStamp[i]

    dateobject = (datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S'))
    date.append(np.datetime64(dateobject))
    
wg_weather['time'] = np.array(date)

wg_weather['Wind_Speed']=wg_weather['Wind Speed(kt)']*0.51444 
wg_weather['Wind Direction'] = (wg_weather['Wind Direction']+ 180) % 360


sct=ax[0].scatter(wg_weather.time,wg_weather.Wind_Speed,c=wg_weather['Wind Direction'],cmap=wind_c2)
cb = plt.colorbar(sct,              
                  pad=-0.06,
#                   label=f'{var} to',
                  ax=ax[0],
                  aspect=10,
                  ticks=[0,90,180,270,360])
cb.set_label('Wind Direction')
# cb.ax.set_yticklabels(['N',
#                        'E',
#                        'S',
#                        'W',
#                        'N'])

ax[0].set_ylabel('Wind Speed (m/s)')





import json
import pandas as pd
import glob
from datetime import datetime
# data = json.load(open('/home/isgiddy/share/www/src/data-load/wg/wg_data.json'))
# wg = pd.DataFrame(data["recordData"])

wg_files = glob.glob('/home/isgiddy/share/www/data/waveglider/2023*.csv')

list_of_files = sorted( filter( os.path.isfile,
                        glob.glob('/home/isgiddy/share/www/data/waveglider/'+ '*.csv') ) )



wg = pd.concat((pd.read_csv(filename) for filename in list_of_files), ignore_index=True)
# wg=wg.sort_values(by='Datetime',ascending=False)
# wgtime=np.sort(wg.Datetime)
date=[]
for i in range (len(wg.Datetime)):
    
    datetime_str =wg.Datetime[i]
    
    try:
        dateobject=pd.to_datetime(wg.Datetime[i])
        
        # dateobject = (datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S'))
        date.append(np.datetime64(dateobject))
    except:
        # print(wg.Datetime[i])
        date.append(np.nan)
    
# print(wg.Datetime[i])    
wg['time'] = np.array(date)
# time = np.array(date)
wg=wg.sort_values('time')
wg=wg.drop_duplicates('time')


df=wg
# df=df.sort_values(by='Datetime')
df=df.drop_duplicates('time')

def parseGPS(sxGPS):    ## CALCULATE SUBSURFACE LAT / LON (TODO: USING DEAD RECKONING)
    return np.sign(sxGPS) * (np.fix(np.abs(sxGPS)/100) + np.mod(np.abs(sxGPS),100)/60)

df['longitude'] = parseGPS(df['Longitude'])
df['latitude'] = parseGPS(df['Latitude'])

# wg=df




# wg_files = glob.glob('/home/isgiddy/share/www/data/waveglider/2023*.csv')
# wg = pd.concat((pd.read_csv(filename) for filename in wg_files[::-1]), ignore_index=True)

# date=[]
# for i in range (len(wg.Datetime)):
    
#     datetime_str =wg.Datetime[i]
#     try:
#         dateobject = (datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S'))
#         date.append(np.datetime64(dateobject))
#     except:
#         # print(wg.Datetime[i])
#         date.append(np.nan)
    
# wg['time'] = np.array(date)
# # time = np.array(date)
# # wg=wg.sort_values('time')
# wg=wg.drop_duplicates('time')


# df=wg
# df=df.sort_values('time')
# df=df.drop_duplicates('time')

# def parseGPS(sxGPS):    ## CALCULATE SUBSURFACE LAT / LON (TODO: USING DEAD RECKONING)
#     return np.sign(sxGPS) * (np.fix(np.abs(sxGPS)/100) + np.mod(np.abs(sxGPS),100)/60)

# df['longitude'] = parseGPS(df['Longitude'])
# df['latitude'] = parseGPS(df['Latitude'])

ax[1].xaxis.set_major_formatter(myFmt)

# ax[0].plot(wg_weather.)

ax[1].scatter(df.time.iloc[2:-2],np.where(df['Atmosphere CO2 Ave'].iloc[2:-2]>100,df['Atmosphere CO2 Ave'].iloc[2:-2],np.nan),c='k',label='Atm CO$_2$')
ax[1].plot(df.time.iloc[2:-2],df['Ocean CO2 Ave'].iloc[2:-2],label='Ocean CO$_2$',lw=2)
ax[1].legend(loc='lower right')
ax[1].set_ylabel('xCO$_2$ Ave')
         
ax[1].set_ylim(320,420)
ax1=ax[1].twinx()
ax1.plot(df.time.iloc[2:-2],df['CTD Temp'].iloc[2:-2],label='CTD Temp',c='tab:red',lw=2)
ax1.set_ylabel('Temperature')
ax1.legend(loc='lower center')

import gsw
df['Salinity']=gsw.SP_from_C(df['CTD Conductivity'].values*10,df['CTD Temp'].values,0) 

ax2=ax[1].twinx()
ax2.plot(df.time.iloc[2:-2],df['Salinity'].iloc[2:-2],label='Practical Salinity',c='tab:green',alpha=0.4,zorder=9)
ax2.set_ylabel('Salinity')
ax2.set_ylim(34.4,35.8)
ax2.legend(loc='lower left')
ax2.spines["right"].set_position(("axes", 1.1))





fig.autofmt_xdate()  

ax[0].set_title('Underway Waveglider')
plt.savefig('/home/isgiddy/share/www/html/img/Underway_WG.png')
# print(now)
