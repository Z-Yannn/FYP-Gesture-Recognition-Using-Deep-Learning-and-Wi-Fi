import numpy as np
import importlib
import config
import os
from numpy.random import seed
from scipy.stats import median_abs_deviation
import tensorflow as tf
seed(2)
tf.random.set_seed(3)

decoder = importlib.import_module(f'decoders.{config.decoder}')  # This is also an import


# load dataset
def read_files(directory):
    csi_all = []
    for filename in os.listdir(directory):
        csi_one_file = []
        file_path = os.path.join(directory, filename)
        # print(filename)
        packets = decoder.read_pcap(file_path)
        number_packets = packets.nsamples_max
        # print(filename)
        for i in range(number_packets):
            csi = packets.get_csi(
                index=i,
                rm_nulls=True,
                rm_pilots=False
            )

            indices_to_remove = [x + 32 for x in [
                -32, -31, -30, -29, -21, -7,
                31, 30, 29, 0, 7, 21
            ]]
            csi = np.delete(csi, indices_to_remove, axis=0)
            csi_abs = np.absolute(csi)
            csi_phase = np.angle(csi)

            # linear transformation for phase
            csi_phase = linear_transformation(csi_phase)

            csi_tensor = np.hstack((csi_abs, csi_phase))
            # csi_tensor = csi_abs
            csi_one_file.append(csi_tensor)
        csi_one_file = np.array(csi_one_file[0:150])
        # print(csi_one_file.shape)
        # filtered = hampel_filter(csi_one_file[:,:52], 3, 3)
        # csi_one_file[:, :52] = filtered
        csi_all.append(csi_one_file)

    csi_final = np.array(csi_all)
    # print(csi_final.shape)
    return csi_final


# fix the problem due to the unknown cfo and sfo
def linear_transformation(phase):
    phase = np.array(phase)
    sanitized_phase = np.zeros_like(phase)

    phase_len = phase.shape[0]
    k = (phase[-1] - phase[0])/(phase_len - 1)
    b = np.mean(phase)

    for i in range(phase_len):
        sanitized_phase[i] = phase[i] - k * i - b

    return sanitized_phase

def hampel_filter(data, window_size, threshold):
    filtered_data = np.zeros_like(data)
    for i in range(data.shape[1]):
        subcarrier_data = data[:, i]
        mad = median_abs_deviation(subcarrier_data)
        hampel_values = np.array([0.0] * len(subcarrier_data))
        for j in range(len(subcarrier_data)):
            start = max(0, j - window_size)
            end = min(len(subcarrier_data), j + window_size)
            median = np.median(subcarrier_data[start:end])
            if abs(subcarrier_data[j] - median) > threshold * mad:
                hampel_values[j] = median
            else:
                hampel_values[j] = subcarrier_data[j]
        filtered_data[:, i] = hampel_values

    return filtered_data


def get_data(directories):
    csi = []

    for i in range(len(directories)):
        csi_file = read_files(directories[i])
        if len(csi) == 0:
            csi = csi_file
        else:
            csi = np.vstack((csi, csi_file))
    csi = np.expand_dims(csi, axis=3)

    label = np.zeros((4500,))
    for j in range(1500):
        label[j] = 0
        label[j + 1500] = 1
        label[j + 3000] = 2
        # label[j + 1200] = 3
        # label[j + 1600] = 4
    #
    # label = np.zeros((900,))
    # for j in range(300):
    #     label[j] = 0
    #     label[j + 300] = 1
    #     label[j + 600] = 2
        # label[j + 2100] = 3
        # label[j + 2800] = 4
    #
    return csi, label



if __name__ == '__main__':
    csi, label = get_data('pcapfiles/left/left100.pcap')
    # print(csi.shape)

