#! usr/bin/bash

ymd=$(date +%Y%m%d)
mnth=$(date +%m)
yr=$(date +%Y)
d=$(date +%d)

#echo "$yr-$mnth-$d" >> /home/isgiddy/file.txt


source /home/isgiddy/sw/miniconda3/bin/activate RTD

#echo "activate" >> /home/isgiddy/file.txt

rm /home/isgiddy/share/www/data/adt/fsle/fsle.nc

python /home/isgiddy/share/www/src/data-plot/fsle/map_of_fle.py /home/isgiddy/share/www/data/adt/fsle/list.ini /home/isgiddy/share/www/data/fsle.nc "2023-03-28" --advection_time 14 --resolution=0.05  --integration_time 6\
   --x_min -35 --x_max 40 --y_min -50 --y_max -20     --final_separation 0.2 --verbose --time_direction backward

#echo "done" >> /home/isgiddy/file.txt
