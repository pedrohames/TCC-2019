import os
import numpy as np
import matplotlib.pyplot as plt
from subprocess import PIPE, run

from scipy import signal


class SDR:

    def __init__(self, fs=20e6, supported_bw=None, driver='driver=hackrf', rx_sdr_path=None):
        self.fs = fs
        self.supported_bw = ['5', '10', '20'] if supported_bw is None else supported_bw
        self.driver = driver
        self._rx_sdr_path = './rx_sdr' if rx_sdr_path is None else rx_sdr_path
        self._tmp_ramfile_path = '/dev/shm/samples.dat'
        try:
            os.remove(self._tmp_ramfile_path)
        except OSError:
            pass

    def _receive_to_ram(self, fc, msec, gain):
        Nsamp = int(self.fs * msec / 1000)  # Number of samples
        size_bytes = Nsamp*128/8
        max_ram = 1024**3
        if size_bytes > max_ram:
            raise ValueError('Sorry, too many samples.')
        command = f'{self._rx_sdr_path} -f {int(fc)*1e6} -s {int(self.fs)} -d {self.driver} -n {Nsamp} -F CF32 -g {gain} {self._tmp_ramfile_path}'
        # Using run because I do not want that the output being printed
        run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)

    def receive(self, fc, msec, gain='LNA=20'):
        self._receive_to_ram(fc, msec, gain)
        return np.fromfile(self._tmp_ramfile_path, np.complex64)

    def receive_to_file(self, path, fc, msec, gain='LNA=20'):
        self._receive_to_ram(fc, msec, gain)
        command = f'cp {self._tmp_ramfile_path} {path}'
        os.system(command)

    @staticmethod
    def receive_from_file(path):
        return np.fromfile(path, np.complex64)

    def fft_split2(self, s_t, n_fft):
        f, t, a = signal.spectrogram(s_t, fs=self.fs, nperseg=n_fft, nfft=n_fft, return_onesided=False, mode='magnitude')
        return 20*np.log10(np.fft.fftshift(a.T, axes=(1,)))

    def fft_split(self, s_t, n_fft, time_ms):
        split_samples = int(self.fs * time_ms/1000)
        split_n = s_t.size // split_samples
        s_t -= np.mean(s_t)  # Remove DC.
        s_t_trunc = s_t[:split_samples * split_n]
        s_t_split = np.reshape(s_t_trunc, newshape=(split_n, split_samples))
        s_f_split = np.fft.fft(s_t_split, n_fft, axis=1)
        return 20 * np.log10(np.abs(np.fft.fftshift(s_f_split, axes=(1,))))

    @staticmethod
    def max_freq_hold(s_f_list):
        return np.amax(s_f_list, axis=0)

    @staticmethod
    def fake_check_mask():
        return 1 - np.random.rand() * 0.05

    @staticmethod
    def check_mask(s_f, bw, n_fft):
        mask = np.fromfile(f'masks/mask_{bw}MHz_{n_fft}.dat', np.float64)
        s_f_dbr = s_f - np.max(s_f)
        return np.mean(s_f_dbr <= mask)

    @staticmethod
    def mask_plot(s_f, bw, n_fft, fc, path=None, save=False):
        mask = np.fromfile(f'masks/mask_{bw}MHz_{n_fft}.dat', np.float64)
        s_f_dbr = s_f - np.max(s_f)

        f_axis = np.linspace(fc - bw/2, fc + bw/2, n_fft)
        plt.plot(f_axis, s_f_dbr, f_axis, mask)
        plt.legend((f'{bw} MHz signal at {fc} MHz', f'{bw} MHz IEEE mask'))
        plt.xlabel('F [MHz]')
        plt.ylabel('Attenuation [dBr]')
        plt.title('IEEE 802.11 spectral mask analysis')
        if save and path is not None:
            if not os.path.exists(path):
                os.system(f'mkdir -p {path}')
                plt.savefig(f'{path}/Fc={fc}MHz_BW={bw}MHz.png', format='png')
            else:
                plt.savefig(f'{path}/Fc={fc}MHz_BW={bw}MHz.png', format='png')
        else:
            plt.show()
        plt.close()
