#!/home/isgiddy/sw/miniconda3/bin/envs/data


import numpy as np
import xarray as xr
import os

########

def prep_files(datadir,datadir_edit):
    """
    subset and rename files
    """
    ls = os.listdir(datadir)

    ls.sort()
 
    for filename in ls:
        if filename[-3:]=='.nc': 
            print(filename)
            ds=xr.open_dataset(datadir+filename)
            try:
                latlon=ds.nv.data
            except:
                ds['nv']=np.array([0,1])
                latlon=ds.nv.data
            variables=['ugosa','vgosa']
            ds=ds[variables]

            Y=str(ds.time.dt.year.values)[1:-1]

            if len(str(ds.time.dt.month.values))<4:
                M=str(ds.time.dt.month.values)[1:-1].zfill(2)
            else: 
                M=str(ds.time.dt.month.values)[1:-1]

            if len(str(ds.time.dt.day.values))<4:
                D=str(ds.time.dt.day.values)[1:-1].zfill(2)
            else: 
                D=str(ds.time.dt.day.values)[1:-1]

            ds_new=xr.Dataset(
               data_vars=dict(
                   Grid_0001=(["NbLongitudes", "NbLatitudes"], (ds.ugosa.astype('float64').data.T*100).squeeze()),
                    Grid_0002=(["NbLongitudes", "NbLatitudes"], (ds.vgosa.astype('float64').data.T*100).squeeze()),
                ),

                coords=dict(

                    LatLon=(["LatLon"], latlon),
                    NbLongitudes=(["NbLongitudes"], ds.longitude.data),
                    NbLatitudes=(["NbLatitudes"], ds.latitude.data)

                ))


            ds_new.Grid_0001.attrs['long_name']='U'
            ds_new.Grid_0002.attrs['long_name']='V'

            ds_new.Grid_0001.attrs['units']='cm/s'
            ds_new.Grid_0002.attrs['units']='cm/s'

            ds_new.Grid_0001.attrs['date']='{}-{}-{} 00:00:00.000000 UTC'.format(Y,M,D)
            ds_new.Grid_0002.attrs['date']='{}-{}-{} 00:00:00.000000 UTC'.format(Y,M,D)


            ds_new.NbLongitudes.attrs['long_name']='Longitudes'
            ds_new.NbLongitudes.attrs['units']='degrees_east'
            ds_new.NbLatitudes.attrs['long_name']='Latitudes'
            ds_new.NbLatitudes.attrs['units']='degrees_north'

            ds_new.to_netcdf(datadir_edit+'{}'.format(filename))
            
    return None
                    

def create_ini(datadir):
    """
    Create list.ini file, replaces previous file
    """

    import os

    os.remove(os.path.join(datadir,'list.ini'))

    ls = os.listdir(datadir)
    ls.sort()

    with open(datadir+"list.ini", "w") as a:

        for filename in ls:
            a.write('U='+datadir+str(filename) + os.linesep) 

        for filename in ls:
            a.write('V='+datadir+str(filename) + os.linesep) 


        a.write('U_NAME = Grid_0001'+ os.linesep)
        a.write('V_NAME = Grid_0002'+ os.linesep)
        a.write('FILL_VALUE = 0'+ os.linesep)

        return None
    

    
if __name__ == "__main__":
    datadir='/home/isgiddy/share/www/data/adt/'
    datadir_edit='/home/isgiddy/share/www/data/adt/fsle/'
    prep_files(datadir,datadir_edit)
    create_ini(datadir_edit)
    
    
    
