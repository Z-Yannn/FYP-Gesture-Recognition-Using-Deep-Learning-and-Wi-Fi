from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow import keras
from keras import layers
import matplotlib.pyplot as plt
from keras.utils.np_utils import to_categorical
import importlib
import config
import os
from numpy.random import seed
import tensorflow as tf
import getData
from keras.callbacks import LearningRateScheduler
import seaborn as sns
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from sklearn.preprocessing import LabelEncoder

seed(30)
tf.random.set_seed(20)

# variables need to change for each training
test_ratio = 0.3  # test size
Nw = 3  # number of classes
filt = 32  # filters
k_size = 3  # kernel_size
epoch = 50
batch_size = 64
model_name = "lab1500"
training = True  # set to train or calculate validation confusion matrix

decoder = importlib.import_module(f'decoders.{config.decoder}')  # This is also an import

directories = ['pcapfiles/down','pcapfiles/left', 'pcapfiles/right']
# directories = ['pcapfiles/lab700/down', 'pcapfiles/lab700/left', 'pcapfiles/lab700/name', 'pcapfiles/lab700/right',
#                'pcapfiles/lab700/stop']
#
# directories = ['pcapfiles/home/five', 'pcapfiles/home/fixed', 'pcapfiles/home/one', 'pcapfiles/home/ok',
#                'pcapfiles/home/wave']
csi, label = getData.get_data(directories)
print(csi.shape)
# number of classes
csi_train, csi_test, label_train, label_test = train_test_split(csi, label, test_size=test_ratio, random_state=5)

if training:
    label_train = to_categorical(label_train, Nw)
    label_test = to_categorical(label_test, Nw)
    [T, M, N, S] = csi.shape
    model = keras.Sequential([
        keras.Input(shape=(M,N,S)),
        layers.Conv2D(filters=filt,kernel_size=k_size,padding="valid"),
        layers.BatchNormalization(),
        layers.Activation("relu"),
        layers.MaxPooling2D(pool_size=(3,3),strides=(3,3)),
        layers.Conv2D(filters=32, kernel_size=(3, 3), padding="valid"),
        layers.BatchNormalization(),
        layers.Activation("relu"),
        layers.MaxPooling2D(pool_size=(3, 3), strides=(3, 3)),
        layers.Flatten(),
        layers.Dense(Nw, activation="softmax")
    ])


    # reduce lr when epoch increases
    def lr_scheduler(epoch, lr):
        if epoch < 10:
            return lr
        elif 10 <= epoch < 30:
            return 0.001
        else:
            return 0.0001


    opt = keras.optimizers.SGD(learning_rate=0.01, momentum=0.9)
    model.compile(loss="categorical_crossentropy",
                  optimizer=opt,
                  metrics=["accuracy"])

    lr_callback = LearningRateScheduler(lr_scheduler)

    history = model.fit(
        csi_train, label_train,
        epochs=epoch,
        batch_size= batch_size,
        validation_data=(csi_test, label_test),
        callbacks=[lr_callback]
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

# validation confusion matrix
else:
    model = keras.models.load_model(model_name)
    y_pred = np.argmax(model.predict(csi_test), axis=-1)
    cm = confusion_matrix(label_test, y_pred)
    sns.heatmap(cm, annot=True, cmap='Blues', fmt='g')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()
