#!/bin/bash

ymd=$(date +%Y%m%d)
mnth=$(date +%m)
yr=$(date +%Y)

echo  "$ymd" >> /home/databot/file.txt

copernicusmarine get --dataset-id cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D --filter "nrt_global_allsat_phy_l4_${ymd}_${ymd}.nc" --username mduplessis2 --password erie9uMo* --output-directory /home/mduplessis/share/www/data/adt/
count=`ls -1 /home/databot/share/www/data/adt/SEALEVEL_GLO_PHY_L4_NRT_008_046/cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_202506/${yr}/${mnth}/nrt_global_allsat_phy_l4_${ymd}_${ymd}.nc 2>/dev/null | wc -l`
if [ $count != 0 ]

then
    echo latest ADT date stamp working

else
   ymd=$(date +%Y%m%d --date="1 days ago")
   mnth=$(date +%m --date="1 days ago")
   yr=$(date +%Y --date="1 days ago")
copernicusmarine get --dataset-id cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D --filter "nrt_global_allsat_phy_l4_${ymd}_${ymd}.nc" --username mduplessis2 --password erie9uMo* --output-directory /home/mduplessis/share/www/data/adt/
fi

echo "downloaded" >> /home/databot/file.txt

cp /home/databot/share/www/data/adt/SEALEVEL_GLO_PHY_L4_NRT_008_046/cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_202506/${yr}/${mnth}/nrt_global_allsat_phy_l4_${ymd}_${ymd}.nc /home/databot/share/www/data/adt_latest.nc 
