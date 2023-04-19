#!/bin/bash

echo "Set wlan.up"
ifconfig wlan0 up
echo "Set up nexutil"
nexutil -Iwlan0 -s500 -b -l34 -vJNABEQGIAQCcPlOPiGIAAAAAAAAAAAAAAAAAAAAAAAAAAA==
echo "Set up the monitor mode for wlan0"
iw dev wlan0 interface add mon0 type monitor
ip link set mon0 up

dir="./left0323"
# Find the next number in the sequence
num=$(ls "$dir" | awk -F'[^0-9]*' '{print $2}' | sort -n | tail -1)
num=$((num + 1))

# Create the new file name
file_name="left$num.pcap"
tcpdump -i wlan0 dst port 5500 -vv -w left0323/$file_name -c 155