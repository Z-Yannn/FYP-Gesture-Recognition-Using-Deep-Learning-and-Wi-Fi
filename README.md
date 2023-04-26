# FYP_Gesture Recognition Using Deep Learning and Wi-Fi
The final year project is about gesture recognition using deep learning and Wi-Fi. From September 2022 to April 2023, the project aims to design, build and evaluate a system capable of recognizing five specific sign language words. A platform combining channel state information (CSI) extraction from Wi-Fi signals and classification algorithms were created.  

## Table of contents
- [Apparatus_and_software](#Apparatus_and_software)
- [Recognition_system_framework](#Recognition_system_framework)
- [CSI_collection](#CSI_collection)
## Apparatus_and_software
* Raspberry pi 4B
* AC750 Wi-Fi travel router (model: TL-WR902AC)
* Two personal computers
* One ethernet cable
* Nexmon (For full information about using Nexmon to collect CSI, please check [Nexmon](https://github.com/seemoo-lab/nexmon_csi))
* Real VNC

## Recognition_system_framework
![theoretical recognition system](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/Theoretical%20recognition%20system.png?raw=true)       

1. An access point (router) is used as a network bridge between the transmitter computer (Tx) and receiver Pi (Rx) at channel 36 and 20 MHz bandwidth under the 5GHz frequency spectrum.

	A private router is needed instead of a public router since the public router is unstable and the specific channel it chooses is changeable over time, increasing the difficulty for collecting stable CSI and maintaining consistency. Channel 36 is the only channel that worked most time. 20MHz bandwidth and 5GHz spectrum are chosen to avoid unnecessary interference and interruptions.

2. The transmitter is set to ping 100 packets every second by command:  

	```
	ping -i 0.01 $IP
	```
	where **$IP** is the current IP address of the access point. The _ping_ command should be run as administrator. Theoretically, higher transmission speed leads to higher accuracy for moving gestures since more CSI packets can be collected in the same period of time. Hence more subtle differences can be detected for classification.  
	
## CSI_collection
### Installation
First, finish the set up of Nexmon on the raspberry pi 4B. In addition to official documents, [Nexmonster](https://github.com/nexmonster/nexmon_csi/tree/pi-5.4.51-plus#getting-started) can also be checked for detailed installation guidance. 
Notice: for dependencies installation, do **not** run _apt upgrade_, that will change the kernel. Only kernels up to version 5.4 are compatible with Nexmon at the time of writing.  

### Measurement
1. Run [**MAC.sh**](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/PI%20Command/MAC.sh) on the raspberry pi to get the string.  
	```
	#!/bin/bash
	echo "Start set up"
	ip link set wlan0 up
	echo "Set up the makecsi params for pi with screen"
	mcp -c 36/20 -C 1 -N 1 -m $MAC -b 0x88
	```  
	where $MAC is the MAC address of the transmitter. 
	***Important***: 
Code explanations will be updated as soon as possible.
