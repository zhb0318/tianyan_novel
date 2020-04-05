#！/bin/bash

python3 crawler.py

echo "======downloadstarting======"

while(($? == 1))

do

sleep 200

du -sh >> abc.txt

echo "======sync failed,re sync starting====="

python3 crawler.py

done
