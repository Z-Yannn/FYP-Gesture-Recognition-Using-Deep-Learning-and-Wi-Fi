import numpy as np
import importlib
import config
import os
from numpy.random import seed
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
        packets = decoder.read_pcap(file_path)
        number_packets = packets.nsamples_max

        for i in range(number_packets):
            csi = packets.get_csi(
                index=i,
                rm_nulls=True,
                rm_pilots=False
            )

            indices_to_remove = [x + 32 for x in [
                -32, -31, -30, -29,
                31, 30, 29, 0
            ]]
            csi = np.delete(csi, indices_to_remove, axis=0)
            (sequence_no, _) = packets.get_seq(index=i)
            if sequence_no != 0:
                csi_abs = np.absolute(csi)
                csi_phase = np.angle(csi)
                # linear transformation for phase
                csi_phase = linear_transformation(csi_phase)

                indices_to_remove_pilot = [x + 32 for x in [
                    -21, -7, 7, 21
                ]]
                csi_abs = np.delete(csi_abs, indices_to_remove_pilot, axis=0)
                csi_phase = np.delete(csi_phase, indices_to_remove_pilot, axis=0)

                csi_tensor = np.hstack((csi_abs, csi_phase))
                csi_one_file.append(csi_tensor)
        csi_one_file = np.array(csi_one_file[0:200])
        # print(csi_one_file.shape)
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


def get_data(directories):
    csi = []

    for i in range(len(directories)):
        csi_file = read_files(directories[i])
        if len(csi) == 0:
            csi = csi_file
        else:
            csi = np.vstack((csi, csi_file))

    label = np.zeros((3500,))
    for j in range(700):
        label[j] = 0
        label[j + 700] = 1
        label[j + 1400] = 2
        label[j + 2100] = 3
        label[j + 2800] = 4

    return csi, label

# def csi_phase_process(csi):


if __name__ == '__main__':
    csi, label = get_data('pcapfiles/wavetest')
    print(csi.shape)

