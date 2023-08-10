# FYP_Gesture Recognition Using Deep Learning and Wi-Fi
The final year project is about gesture recognition using deep learning and Wi-Fi, supervised by [Junqing Zhang](https://junqing-zhang.github.io/). From September 2022 to April 2023, the project aims to design, build and evaluate a system capable of recognizing five specific sign language words. A platform combining channel state information (CSI) extraction from Wi-Fi signals and classification algorithms was created.  

## Table of contents
- [Apparatus_and_software](#Apparatus_and_software)
- [Recognition_system_framework](#Recognition_system_framework)
- [CSI_collection](#CSI_collection)
- [CSI_visualization](#CSI_visualization)
- [Data_preprocessing](#Data_preprocessing)
- [Classification](#Classification)
- [Control_Spotify](#Control_Spotify)
## Apparatus_and_software
* Raspberry Pi 4B
* AC750 Wi-Fi travel router (model: TL-WR902AC)
* Two personal computers
* One ethernet cable
* Nexmon (For full information about using Nexmon to collect CSI, please check [Nexmon](https://github.com/seemoo-lab/nexmon_csi))
* Wireshark
* Real VNC

## Recognition_system_framework       
<img width="450" src="https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/Theoretical%20recognition%20system.png?raw=true"/>  

1. An access point (router) is used as a network bridge between the transmitter computer (Tx) and receiver Pi (Rx) at channel 36 and 20 MHz bandwidth under the 5GHz frequency spectrum.

	A private router is needed instead of a public router since the public router is unstable and the specific channel it chooses is changeable over time, increasing the difficulty of collecting stable CSI and maintaining consistency. Channel 36 is the only channel that works most time. 20MHz bandwidth and 5GHz spectrum are chosen to avoid unnecessary interference and interruptions.

2. The transmitter is set to ping 100 packets every second by command:  

	```
	ping -i 0.01 $IP
	```
	where `$IP` is the current IP address of the access point. The ping command should be run as administrator. Theoretically, higher transmission speed leads to higher accuracy for moving gestures since more CSI packets can be collected in the same period. Hence more subtle differences can be detected for classification.  
	
## CSI_collection
### Installation
First, finish the set up of Nexmon on the raspberry pi 4B. In addition to official documents, [Nexmonster](https://github.com/nexmonster/nexmon_csi/tree/pi-5.4.51-plus#getting-started) can also be checked for detailed installation guidance.  
Notice: for dependencies installation, do **not** run `apt upgrade`, that will change the kernel. Only kernels up to version 5.4 are compatible with Nexmon at the time of writing.  

### Measurement
1. Activate the wireless card associated with "wlan0" on the raspberry pi and enables the network connection: 
	```
	ip link set wlan0 up
	```  
2. Use _mcp_ to generate a base64 encoded parameter string that can be used to configure the extractor. The following example call generates a parameter string that enables collection on channel 36 with 20 MHz bandwidth on the first core for the first spatial stream for frames starting with 0x88 originating from _$MAC_:
	```
	mcp -c 36/20 -C 1 -N 1 -m $MAC -b 0x88
	```
	You can also check the full command list with `mcp -h`.  
	***Important:*** `-b 0x88` is **necessary** for collecting real transmission data. Otherwise, [weird zeros](https://github.com/nexmonster/nexmon_csi/issues/36) will occur in the raw CSI pcap file.  
	
3. Make sure the interface is up:
	```
	ifconfig wlan0 up
	```
4. Configure the extractor using `nexutil` and the generated parameters (parameters after `-v`):
	```
	nexutil -Iwlan0 -s500 -b -l34 -vJNABEQGIAQCcPlOPiGIAAAAAAAAAAAAAAAAAAAAAAAAAAA==
	```
5. Enable monitor mode:
	```
	iw dev wlan0 interface add mon0 type monitor
	ip link set mon0 up
	```
6. Collect CSI by listening on UDP socket 5500:
	```
	tcpdump -i wlan0 dst port 5500 -vv -w $file_name -c 155
	``` 
	 The raw CSI will be stored in a pcap file called `$file_name`. `-c` represents capturing continuously until 155 packets are collected. You can use `-i` to control the duration.

For collection convenience, `CSI.sh` can generate a pcap file including the corresponding gesture information each time it is run. It is normal if `command failed: Operation not supported (-95)` shows in the command line. The problem comes from duplicated `ip link set mon0 up`. The monitor mode can only be set once. It can be solved by rebooting the raspberry pi.

### Decode
During the collection period, each gesture sample has many CSI packets stored in chronological order in one pcap file. The information in this file cannot be used directly and should be decoded to extract CSI.

Before decoding, the transmission packets have 10.10.10.10 as the source address and 255.255.255.255 as the destination address on port 5500. The payload starts with two magic bytes 0x1111. Six bytes source Mac address is followed. Next two bytes represent the sequence number of this packet. The core and spatial stream is displayed in later two bytes. The next two bytes contain channel specifications, followed by two bytes declaring the chip version. All other bytes denote the actual CSI. 20, 40 and 80MHz channels have 64, 128, or 256 times four bytes long respectively.  

![Theoretical data format](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/Theoretical%20data%20format.png?raw=true)  
  
`Interleaved.py` can extract CSI samples in pcap files fast and efficiently.  

## CSI_visualization
1. Open `config.py` and select your WiFi chip. Default is bcm43455c0 (Raspberry Pi)
2. Store the files into the `pcapfiles` folder.
3. Run `csiexplorer.py`  

Enter the pcap's filename. Type an index to show it's plot. Type indexes separated by `-` to play animation (example: `0-10`). Type `all` to show all CSI packets drawn in one figure. Type `help` for running tips.  

<img width="600" src="https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/csiexplorer.png?raw=true"/>  

<img width="600" src="https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/allcsi.png?raw=true"/>  

### Get CSI data
`getData.py` is an example about using the `interleaved.py` to extract CSI data.   

```
import importlib
import config

decoder = importlib.import_module(f'decoders.{config.decoder}') # This is also an import
packets = decoder.read_pcap(file_path)
number_packets = packets.nsamples_max
# print(filename)
for i in range(number_packets):
	csi = packets.get_csi(
			index=i,
			rm_nulls=True,
			rm_pilots=False
)
```

## Data_preprocessing
### Algorithm 1: CSI PREPROCESSING
**Input**: Raw data as $CSI_{raw}$, pilot and null as $CSI_{pilot}$ and $CSI_{null}$
**Output**: CSI preconditioned as $CSI_{precond}$
1. $CSI_{precond}$ <- $CSI_{raw}$ - $CSI_{p}$ - $CSI_{null}$

### Algorithm 2: HAMPEL FILTER
**Input**: $CSI_{med}$ <- local median of current window of the magnitude of $CSI_{precond}$: |$\widehat{H}(f,t)$| 
**Output**: Magnitude outliers removed as |$\widetilde{H}(f,t)$| 
1. median absolute deviation (MAD) of the current subcarrier
2. **if** $|\widetilde{H}(f_i,t)| - CSI_{med}(i) > n_σ × MAD$
3. $\widetilde{H}(f_i,t) = CSI_{med}(i)$
4. **end if**

### Algorithm3: LINEAR TRANSFORMATION
**Input**:  The phase of $CSI_{precond}$: $∠\widehat{H}(f,t)$
**Output**: Sanitised phase $∠\widetilde{H}(f,t)$

1. $k = \frac{∠\widetilde{H}(f_{52},t) - ∠\widetilde{H}(f_{1},t)}{m_{52} - m_1}$
2.  $b=\frac{1}{52}\sum_{i=52}∠\widetilde{H}(f_{i},t)$
3.  $∠\widetilde{H}(f_{i},t) = ∠\widehat{H}(f,t) - km_i - b_i$

### After signal preprocessing
![After](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/preprocessing.png?raw=true)

The process shows all CSI packets for one sample of sign “Left” after signal processing

## Classification

### Model structure
![CNN](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/CNN.png?raw=true)  

Hyperparameters | Value | 
| :---: | :---:
Conv2D  | filters=32, kernel_size=3
MaxPooling2D  | pool_size=3, strides=3
Learning rate  | 0.01 (0-10) -> 0.001 (10-30) -> 0.0001 (30-50)
Batch size  | 64

Run `train.py` to make a trained CNN model.

### Performance
For 3500 samples collected in the lab:  
  
<img width="450" src="https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/loss.png?raw=true"/>  

<img width="450" src="https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/accuracy.png?raw=true"/>  

<img width="450" src="https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/confusion%20matrix.png?raw=true"/>  

## Control Spotify
Combined the system with the Spotify API to remotely control web music playback.
[![watch the video]](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/recognitionvideo.mp4)

```
# Authenticate and get the access token    
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
```
```
# define the action to be executed when a message is received  
def execute(message):  
    if message == "down":  
        sp.pause_playback()  
    if message == "start":  
        sp.start_playback()  
    if message == "right":  
        sp.next_track()  
    if message == "left":  
        sp.previous_track()  
```
```
# Set up socket connection  
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind(('localhost', 2000))  
sock.listen()  
```
