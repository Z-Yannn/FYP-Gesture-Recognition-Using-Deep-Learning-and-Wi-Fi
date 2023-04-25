# FYP_Gesture Recognition Using Deep Learning and Wi-Fi
The final year project is about gesture recognition using deep learning and Wi-Fi. From September 2022 to April 2023, the project aims to design, build and evaluate a system capable of recognizing five specific sign language words. A platform combining channel state information (CSI) extraction from Wi-Fi signals and classification algorithms were created.

## Apparatus and software
* Raspberry pi 4B
* AC750 Wi-Fi travel router (model: TL-WR902AC)
* Two personal computers
* One ethernet cable
* Nexmon (For full information about using Nexmon to collect CSI, please check [Nexmon](https://github.com/seemoo-lab/nexmon_csi))
* Real VNC

## Recognition system framework
![theoretical recognition system](https://github.com/Z-Yannn/FYP-Gesture-Recognition-Using-Deep-Learning-and-Wi-Fi/blob/main/Picture/Theoretical%20recognition%20system.png?raw=true)  
The basic principle is that various human activities produce different modifications in radio propagation. Such modifications can be quantified by channel state information (CSI). The CSI represented by the same gesture is similar, although slight differences exist due to different acquisition times or waving rates. If many sets of CSI records are collected, a deep learning model can be trained offline. The model can predict the activity type using CSI acquired during the test stage.

Code explanations will be updated as soon as possible.
