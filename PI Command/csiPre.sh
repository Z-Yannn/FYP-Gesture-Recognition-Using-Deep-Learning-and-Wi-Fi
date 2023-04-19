#!/bin/bash

echo "Set wlan.up"
ifconfig wlan0 up
echo "Set up nexutil"
nexutil -Iwlan0 -s500 -b -l34 -vJNABEQGIAQCcPlOPiGIAAAAAAAAAAAAAAAAAAAAAAAAAAA==
echo "Set up the monitor mode for wlan0"
iw dev wlan0 interface add mon0 type monitor
ip link set mon0 up

#timeout 180 tcpdump -i wlan0 dst port 5500 -vv -w fixed.pcap
tcpdump -i wlan0 dst port 5500 -vv -w notsame2.pcap -c 500