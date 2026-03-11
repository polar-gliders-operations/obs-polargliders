#! usr/bin/bash

ymd=$(date +%Y%m%d)
mnth=$(date +%m)
yr=$(date +%Y)

echo  "$ymd" >> /home/mduplessis/file.txt

copernicusmarine get --dataset-id METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2 --filter "${ymd}120000-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB-v02.0-fv02.0.nc" --username mduplessis2 --password erie9uMo* --output-directory /home/mduplessis/share/www/data/sst/
count=`ls -1 /home/mduplessis/share/www/data/sst/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2/${yr}/${mnth}/${ymd}120000-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB-v02.0-fv02.0.nc 2>/dev/null | wc -l`
if [ $count != 0 ]

then
    echo latest SST date stamp working

else
   ymd=$(date +%Y%m%d --date="1 days ago")
   mnth=$(date +%m --date="1 days ago")
   yr=$(date +%Y --date="1 days ago")
copernicusmarine get --dataset-id METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2 --filter "${ymd}120000-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB-v02.0-fv02.0.nc" --username mduplessis2 --password erie9uMo* --output-directory /home/mduplessis/share/www/data/sst/
fi

echo "downloaded" >> /home/mduplessis/file.txt

cp /home/mduplessis/share/www/data/sst/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2/${yr}/${mnth}/${ymd}120000-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB-v02.0-fv02.0.nc /home/mduplessis/share/www/data/sst_latest.nc 
