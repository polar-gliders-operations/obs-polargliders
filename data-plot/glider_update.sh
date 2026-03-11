#!usr/bin/bash
source /home/isgiddy/sw/miniconda3/bin/activate gliders
python3 /home/isgiddy/share/www/src/data-plot/WG_updates.py
python3 /home/isgiddy/share/www/src/data-plot/plot_SE_data.py
python3 /home/isgiddy/share/www/src/data-plot/sb_plots.py
python3 /home/isgiddy/share/www/src/data-plot/sg_plot.py
