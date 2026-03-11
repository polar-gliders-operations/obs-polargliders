#!usr/bin/bash

#rm /home/isgiddy/share/www/src/data-load/wg/wg_data.json
#
#
#touch /home/isgiddy/share/www/src/data-load/wg/wg_data.json
source /home/isgiddy/sw/miniconda3/bin/activate data
end=$(date --date '-1 hour' +%Y-%m-%dT%TZ) 
echo $end >> time.txt
start=$(date --date '-4320 min'  +%Y-%m-%dT%TZ)
echo $start  >> time.txt
#wg_data=$(python3 wg_dataservice.py --getReportData --vehicle 2107397055 --startDate $start --endDate $end)
#echo $wg_data >> wg_data.json

python3 wg_dataservice.py --getReportData --vehicle 2107397055 --startDate $start --endDate $end
