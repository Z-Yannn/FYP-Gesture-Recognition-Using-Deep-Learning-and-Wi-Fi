import numpy as np
import importlib
import config
import os
from numpy.random import seed
import tensorflow as tf
from scipy.stats import median_abs_deviation
import matplotlib.pyplot as plt
seed(2)
tf.random.set_seed(3)

decoder = importlib.import_module(f'decoders.{config.decoder}')  # This is also an import


# load dataset
def read_file(directory):
    c_abs = []
    c_pha = []
    # print(filename)
    packets = decoder.read_pcap(directory)
    number_packets = packets.nsamples_max
    for i in range(number_packets):
        csi = packets.get_csi(
            index=i,
            rm_nulls=True,
            rm_pilots=True
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
        c_abs.append(csi_abs)
        c_pha.append(csi_phase)

    c_abs = np.array(c_abs)
    c_abs_final = hampel_filter(c_abs, 3, 3)

    c_pha_final = np.array(c_pha)
    # print(csi_final.shape)
    return c_abs_final, c_pha_final


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


if __name__ == '__main__':
    c_abs, c_pha = read_file('pcapfiles/lab700/name/name627.pcap')

    fig, axs = plt.subplots(2)
    ax_amp = axs[0]
    ax_pha = axs[1]

    ax_amp.set_ylabel('Amplitude')
    ax_pha.set_ylabel('Phase')
    ax_pha.set_xlabel('Subcarrier')
    fig.suptitle('Channel State Information')
    ax_amp.grid(True)
    ax_pha.grid(True)

    x = np.arange(-26, 26)
    for index in range(0, c_abs.shape[0]):
        ax_amp.plot(x, c_abs[index])
        ax_pha.plot(x, c_pha[index])

    plt.draw()
    plt.pause(100)

