import os
import time
import numpy as np
import importlib
import config
from tensorflow import keras
from plotters.AmpPhaPlotter import Plotter # Amplitude and Phase plotter
import getData
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
decoder = importlib.import_module(f'decoders.{config.decoder}') # This is also an import
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

model_name = "binarybinary"
# home
# known = {'down':0,'left':1, 'your':2, 'five':3, 'wave':4}
# class_name = {0:'left',1:'right', 2:'your', 3:'five', 4:'wave'}
# lab
known = {'down': 0, 'left': 1}
class_name = {0: 'down', 1: 'left'}
model = keras.models.load_model(model_name)

# directories = ['pcapfiles/lab/babytest']
directories = ['pcapfiles/test0320']
csis, _ = getData.get_data(directories)

target = np.zeros((200,))
target[0:100] = 0
target[100:200] = 1
# target[100:200] = 1
# target[200:269] = 3
# for j in range(40):
#     target[j] = 0
#     target[j + 40] = 1
#     target[j + 80] = 2
    # target[j + 120] = 2
    # target[j + 160] = 2


correct = 0
true_labels = []
predicted_labels = []
index = 0
for csi in csis:
    csi = np.expand_dims(csi, axis=0)
    prediction = model.predict(csi)[0]
    label = np.argmax(prediction)
    name = class_name[label]
    confidence = prediction[label]
    print('Predicted class: {}, Name: {}, Confidence score: {:.2f}'.format(label, name, confidence))
    if label == target[index]:
        correct += 1
    index += 1
    true_labels.append(target)
    predicted_labels.append(label)

tes_acc = correct/len(csis)
print("test dataset accuracy is {}".format(tes_acc))

# calculate confusion matrix
predicted_labels = np.array(predicted_labels)
print(target.shape, predicted_labels.shape)
cm = confusion_matrix(target, predicted_labels)
print(cm)

# create heatmap of confusion matrix
sns.heatmap(cm, annot=True, cmap="Blues")
plt.xlabel("Predicted labels")
plt.ylabel("True labels")
plt.show()
