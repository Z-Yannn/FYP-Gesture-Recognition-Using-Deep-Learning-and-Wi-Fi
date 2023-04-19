#!/bin/bash
echo "Start set up"
ip link set wlan0 up
echo "Set up the makecsi params for pi with screen"
mcp -c 36/20 -C 1 -N 1 -m 9c:3e:53:8f:88:62 -b 0x88