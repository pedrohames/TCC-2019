import numpy as np
from subprocess import PIPE, run
import matplotlib.pyplot as plt


class SDR:

    def __init__(self, fs=20e6, supported_bw=None, driver=None, path=None):
        self.fs = fs
        if supported_bw is None:
            self.supported_bw = ['5', '10', '20']
        else:
            self.supported_bw = supported_bw
        if driver is None:  # Initialising HackRF One
            self.driver = 'driver=hackrf'
        else:
            self.driver = driver
        if path is None:
            self.path = '/dev/shm/samples.dat'
        else:
            self.path = path

    def receive(self, fc, msec, gain=20):
        Nsamp = int(self.fs * msec / 1000)  # Number of samples
        size_Bytes = Nsamp*128/8
        max_ram = 1024**3
        if size_Bytes > max_ram:
            raise ValueError('Sorry, too many samples.')

        command = f'./rx_sdr -f {int(fc)} -s {int(self.fs)} -d {self.driver} -n {Nsamp} -F CF32 -g LNA={gain} {self.path}'
        run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return np.fromfile(self.path, np.complex64)

    def receive_to_file(self, fc, msec, gain=20):
        Nsamp = int(self.fs * msec / 1000)  # Number of samples
        size_Bytes = Nsamp*128/8
        max_ram = 1024**3
        if size_Bytes > max_ram:
            raise ValueError('Sorry, too many samples.')

        command = f'./rx_sdr -f {int(fc)} -s {int(self.fs)} -d {self.driver} -n {Nsamp} -F CF32 -g LNA={gain} {self.path}'
        run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return self.path

    @staticmethod
    def receive_from_file(path):
        return np.fromfile(path, np.complex64)

    @staticmethod
    def fft(s_t, n_fft):
        freqs = np.fft.fft(s_t, n_fft)
        freqs[0] = freqs[1]
        freqs_shift = np.fft.fftshift(freqs)
        return 20 * np.log10(np.abs(freqs_shift))

    def fft_split(self, s_t, n_fft, time_ms):
        split_samples = self.fs*(time_ms/1000)
        split_n = int(np.floor(len(s_t)/split_samples))
        s_f_list = []
        for n in range(0, split_n-1):
            p0 = int(n * split_samples)
            p1 = int((n + 1) * split_samples)
            s_f_split = s_t[p0:p1]
            s_f_list.append(self.fft(s_f_split, n_fft))
        return np.array(s_f_list)

    @staticmethod
    def max_freq_hold(s_f_list):
        s_f_max = np.zeros(s_f_list[0].size)
        for s_f in s_f_list:
            s_f_max = np.maximum(s_f_max, s_f)
        return s_f_max

    @staticmethod
    def check_mask(s_f, bw, n_fft):
        s_f_dbr = np.empty(len(s_f))
        max_s_f = max(s_f)
        mask = np.fromfile(f'masks/mask_{bw}MHz_{n_fft}.dat', np.float64)
        for x in range(0, len(s_f)):
            s_f_dbr[x] = s_f[x] - max_s_f
        result = np.sum(np.less_equal(s_f_dbr, mask))
        return result/n_fft

    @staticmethod
    def fake_check_mask():
        return 1 - np.random.rand()*0.05

    @staticmethod
    def mask_print(s_f, bw, n_fft, fc):
        s_f_dbr = np.empty(len(s_f))
        print(s_f.shape)
        max_s_f = max(s_f)
        print(f'====BW={bw}====')
        mask = np.fromfile(f'masks/mask_{bw}MHz_{n_fft}.dat', np.float64)
        for x in range(0, len(s_f)):
            s_f_dbr[x] = s_f[x] - max_s_f

        f_axis = np.linspace((fc - bw/2), fc + bw/2, n_fft)
        plt.plot(f_axis, s_f_dbr)
        plt.plot(f_axis, mask)
        plt.legend((f'{bw} MHz signal at {fc} MHz', f'{bw} MHz IEEE mask'))
        plt.xlabel('F [MHz]')
        plt.ylabel('Attenuation [dBr]')
        plt.title('IEEE 802.11 spectral mask analysis')
        plt.show()
