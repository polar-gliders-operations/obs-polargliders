#! usr/bin/bash
#echo "start" >> /home/isgiddy/file.txt

source /home/isgiddy/sw/miniconda3/bin/activate data
#echo "activate" >> /home/isgiddy/file.txt

rm /home/isgiddy/share/www/data/fsle.nc
rm /home/isgiddy/share/www/data/adt/fsle/list.ini
touch /home/isgiddy/share/www/data/adt/fsle/list.ini

python3 /home/isgiddy/share/www/src/data-plot/fsle/prep_fsle.py

#echo "prep" >> /home/isgiddy/file.txt
