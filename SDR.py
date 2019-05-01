import numpy as np
from subprocess import PIPE, run

class SDR:

    def __init__(self):
        # Initialising HackRF One
        self.driver = 'driver=hackrf'

    def receive(self, fc, fs, msec, gain = None):
        Nsamp = int(fs * msec / 1000)  # Number of samples
        if gain is None:
            command = f'./rx_sdr -f {int(fc)} -s {int(fs)} -d {self.driver} -n {Nsamp} -F CF32 samples.dat'
        else:
            command = f'./rx_sdr -f {int(fc)} -s {int(fs)} -d {self.driver} -n {Nsamp} -F CF32 -g {gain} samples.dat'
        run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return np.fromfile('samples.dat')

    def fft(self, s_t, n_fft):
        freqs = np.fft.fft(s_t, n_fft)
        freqs[0] = 0
        return np.fft.fftshift(freqs)

    def max_freq_hold(self, s_f_list):
        max = np.zeros(s_f_list[0].size)
        for s_f in s_f_list:
            max = np.maximum(max, s_f)
        return np.abs(max)
