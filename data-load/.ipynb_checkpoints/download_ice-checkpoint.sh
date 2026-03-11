ymd=$(date +%Y%m%d)
mnth=$(date +%m)
yr=$(date +%Y)
day=$(date +%d --date="1 days ago")


echo "https://data.seaice.uni-bremen.de/amsr2/asi_daygrid_swath/s6250/netcdf/2023/asi-AMSR2-s6250-${yr}${mnth}${day}-v5.4.nc"

wget -P /home/isgiddy/share/www/data/seaice/  -r -nc -np -nH -e robots=off "https://data.seaice.uni-bremen.de/amsr2/asi_daygrid_swath/s6250/netcdf/2023/asi-AMSR2-s6250-${yr}${mnth}${day}-v5.4.nc"

cp /home/isgiddy/share/www/data/seaice/amsr2/asi_daygrid_swath/s6250/netcdf/2023/asi-AMSR2-s6250-${yr}${mnth}${day}-v5.4.nc /home/isgiddy/share/www/data/seaice_latest.nc 
