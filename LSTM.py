from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from sklearn.model_selection import train_test_split
from tensorflow import keras
from keras import layers
from keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
from keras.utils.np_utils import to_categorical
import importlib
import config
import os
from numpy.random import seed
import tensorflow as tf
import dataLSTM
from keras.callbacks import LearningRateScheduler

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

seed(10)
tf.random.set_seed(20)

# variables need to change for each training
test_ratio = 0.2  # test size
Nw = 5  # number of classes - 1
epoch = 50
batch_size = 64
model_name = "play_lab_700_LSTM"

decoder = importlib.import_module(f'decoders.{config.decoder}')  # This is also an import

directories = ['pcapfiles/lab700/down','pcapfiles/lab700/left', 'pcapfiles/lab700/name', 'pcapfiles/lab700/right',
               'pcapfiles/lab700/stop']
# directories = ['pcapfiles/left', 'pcapfiles/right', 'pcapfiles/down', 'pcapfiles/name', 'pcapfiles/stop']
csi, label = dataLSTM.get_data(directories)

# number of classes
csi_train, csi_test, label_train, label_test = train_test_split(csi, label, test_size=test_ratio, random_state=5)
label_train = to_categorical(label_train, Nw)
label_test = to_categorical(label_test, Nw)

[T, M, N] = csi.shape
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(M, N)))
model.add(Dropout(0.1))
model.add(LSTM(32))
model.add(Dropout(0.1))
model.add(Dense(32, activation='relu'))
model.add(Dense(Nw, activation='softmax'))

model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Define early stopping callback
early_stopping = EarlyStopping(monitor='val_loss', patience=5)

history = model.fit(
    csi_train, label_train,
    epochs=epoch,
    batch_size=batch_size,
    validation_data=(csi_test, label_test),
)

model.save(model_name)
accuracy = history.history["accuracy"]
val_accuracy = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]
epochs = range(1, len(accuracy) + 1)
plt.plot(epochs, accuracy, "r", label="Training accuracy")
plt.scatter(epochs, accuracy, c='r', marker='x')
plt.plot(epochs, val_accuracy, "b", label="Validation accuracy")
plt.scatter(epochs, val_accuracy, c='b', marker='x')
plt.title("Training and validation accuracy")
plt.legend()
plt.figure()
plt.plot(epochs, loss, "r", label="Training loss")
plt.scatter(epochs, loss, c='r', marker='x')
plt.plot(epochs, val_loss, "b", label="Validation loss")
plt.scatter(epochs, val_loss, c='b', marker='x')
plt.title("Training and validation loss")
plt.legend()
plt.show()
