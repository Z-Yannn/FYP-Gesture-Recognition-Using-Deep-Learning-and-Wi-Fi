import socket
import os
import time
import numpy as np
import importlib
import config
from tensorflow import keras
import keyboard
from plotters.AmpPhaPlotter import Plotter # Amplitude and Phase plotter
import getData
import random
decoder = importlib.import_module(f'decoders.{config.decoder}') # This is also an import
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

filename = 'fypfiles/fyp.pcap'

while True:
    if os.path.exists(filename):
        class_name = {0:'down', 1:'left', 2:'right'}
        # class_name = {0:'down', 1:'left', 2:'name', 3:'right', 4:'stop'}
        model = keras.models.load_model('lab0323')
        # model = keras.models.load_model('play_lab_700')
        csis, _ = getData.get_data(['fypfiles'])
        csi = csis[0]
        csi = np.expand_dims(csi, axis=0)
        print(csi.shape)
        prediction = model.predict(csi)[0]
        label = np.argmax(prediction)
        name = class_name[label]
        print('Predicted class: {}, Name: {}'.format(label, name))

        # Delete the file once it has been processed.
        os.unlink(filename)
        time.sleep(1)

        # Set up socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 2000))

        # Send a message to the other program
        message = name
        sock.sendall(message.encode())

        # Close the socket connection
        sock.close()
    # else:
    #     print(f"Waiting for 'fyp.pcap' to appear...")
    #     time.sleep(1)  # Wait for 1 second before checking again


