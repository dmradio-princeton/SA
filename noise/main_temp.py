import time
import os
import shutil

import matplotlib.pyplot as plt
from datetime import datetime

from redpitaya import RedPitaya
import numpy as np
import pandas as pd

from scipy.fft import fft, fftfreq

start_time = time.time()

path = "/home/dmradio/PycharmProjects/SQUID_LNA/noise/output/" + str(datetime.now())

if os.path.isdir(path):
    shutil.rmtree(path)
os.makedirs(path)

REDPITAYA_ADDRESS = "10.42.0.185"

meas = np.empty((0, 2))

N_SAMPLES = 16384
DEC_FACTOR = 1
SAMPLING_RATE = 125e6 / DEC_FACTOR
DURATION = N_SAMPLES / SAMPLING_RATE
FREQ_STEP = 1. / DURATION
TIME_STEP = 1. / SAMPLING_RATE

time.sleep(5)
redpitaya = RedPitaya(REDPITAYA_ADDRESS, DEC_FACTOR, N_SAMPLES, DURATION)

# sources = ["SOUR1", "SOUR2"]
sources = ["SOUR1"]


for source in sources:
    Navg = 10
    PSD, PSD_ampl = 0, 0
    RMS_PSD, RMS = 0, 0

    for i in range(Navg):
        print("{:.2f}% completed".format(i/Navg*100))
        buffs = redpitaya.data_acquisition(source=source, mode="LV")

        time.sleep(5)

        buff_ffts = fft(buffs)
        buff_rffts = fftfreq(int(N_SAMPLES), float(TIME_STEP))

        xPSD = np.append(buff_rffts[:int(N_SAMPLES / 2)], np.abs(buff_rffts[int(N_SAMPLES / 2)]))
        PSD1 = (np.square(np.abs(buff_ffts[:int(N_SAMPLES / 2)]))) / (N_SAMPLES ** 2 * FREQ_STEP)
        PSD2 = (np.square(np.abs(buff_ffts[int(N_SAMPLES / 2):][::-1]))) / (N_SAMPLES ** 2 * FREQ_STEP)

        PSD += np.add(np.append(PSD1, [0]), np.append([0], PSD2))
        PSD_ampl += np.sqrt(PSD)

        RMS_PSD += (np.sum(PSD) * FREQ_STEP)
        RMS += np.sum(np.square(buffs)) / N_SAMPLES

    PSD = PSD/Navg
    PSD_ampl = PSD_ampl/Navg

    peak_x = np.argmax(PSD[5:])
    freq_peak = xPSD[5:][peak_x]

    peak_y = np.amax(PSD[5:])
    Vpp_peak = 2 * np.sqrt(2 * peak_y * FREQ_STEP)

    Vpp_RMS = 2 * np.sqrt(2 * RMS)
    Vpp_RMSPSD = 2 * np.sqrt(2 * RMS_PSD)

    # print("Parsevals theorem (PSD): {:.4e}%".format(np.abs((RMS - RMS_PSD) / (2 * (RMS + RMS_PSD))) * 100))
    # print("Vpp_RMS ={:.4e}".format(Vpp_RMS))
    print("Vpp = {:.4e}V at {:.4e}Hz".format(Vpp_peak, freq_peak))

    source_path = path + "/{}".format(source)
    os.makedirs(source_path)

    data_PSD = \
        {
            'Frequency [Hz]': xPSD,
            'PSD, [V/srHz]': PSD_ampl,
        }

    data_PSD = pd.DataFrame(data_PSD)
    data_PSD.to_csv(source_path + '/PSD.csv')

    plt.loglog(xPSD, PSD_ampl)
    plt.grid()
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD, [V/$\sqrt{Hz}$]')
    plt.savefig(source_path + '/PSD.pdf')
    plt.clf()


print('--- {}s seconds ---'.format(time.time() - start_time))
