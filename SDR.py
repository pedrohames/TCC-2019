import SoapySDR
import numpy as np


class SDR:

    def __init__(self, FS, BW, Fc):
        # Initialising HackRF One
        self.hackrf = SoapySDR.Device(dict(driver='hackrf'))

        self.FS = FS  # Sample frequency [Hz]
        self.BW = BW  # Bandwidth [Hz]
        self.Fc = Fc  # Central frequency  [Hz]

        # HackRF Setup
        self.hackrf.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, FS)
        self.hackrf.setBandwidth(SoapySDR.SOAPY_SDR_RX, 1, BW)
        self.hackrf.setFrequency(SoapySDR.SOAPY_SDR_RX, 1, Fc)
        self.maxSamples = 131072

    def receive(self, msec):
        Nsamp = int(self.FS * msec/1000)  # Number of samples
        assert Nsamp > self.maxSamples, f'Capture too short, must be more than {self.maxSamples*1000/self.FS} ms'

        # Initialising capture stream, but still disable
        rxStream = self.hackrf.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32, [0])

        # Activating capture stream
        self.hackrf.activateStream(rxStream)

        # Buffer
        buffer = np.empty(Nsamp*2, np.complex64)
        s_t = []

        # Loop that capture the samples
        while Nsamp > self.maxSamples:
            sr = self.hackrf.readStream(rxStream, [buffer], buffer.size, timeoutUs=int(10e6))
            assert sr.ret > 0, 'Error during capture'
            Nsamp -= sr.ret
            s_t.append(buffer[:sr.ret+1])
        # After finishing this loop, the samples will be on s_t

        # Disabling capture stream
        self.hackrf.deactivateStream(rxStream)
        # Closing capture stream
        self.hackrf.closeStream(rxStream)

        return s_t

    def fft(self, s_t, n_fft):
        freqs = np.fft.fft(s_t, n_fft)
        return np.fft.fftshift(freqs)

    def max_freq_hold(self, s_f_list):
        max = np.zeros(s_f_list[0].size)
        for s_f in s_f_list:
            max = np.maximum(max, s_f)
        return np.abs(max)
