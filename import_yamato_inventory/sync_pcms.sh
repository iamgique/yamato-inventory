
#!/bin/bash

source /etc/profile.d/python.sh

echo "4Begining script sync Stock pcms on" > /data/logs/ems/pcms_sys_stock.log

python /data/projects/ems/pcms_stock_sync/pcms_stock.py

echo "4Begining script sync Stock pcms on" > /data/logs/ems/pcms_sys_stock.log
