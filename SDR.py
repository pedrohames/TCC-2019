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

    def receive(self, time):
        Nsamp = int(self.FS * time)  # Number of samples
        # Initialising capture stream, but still disable
        rxStream = self.hackrf.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32, [0])

        # Activating capture stream
        self.hackrf.activateStream(rxStream)

        # Buffer
        buffer = np.empty(Nsamp, np.complex64)

        # Loop that capture the samples
        while Nsamp > 0:
            sr = self.hackrf.readStream(rxStream, buffer, buffer.size, timeoutUs=int(1e6))
            assert sr.ret > 0
            Nsamp -= sr.ret
        # After finishing this loop, the samples will be on buffer

        # Disabling capture stream
        self.hackrf.deactivateStream(rxStream)
        # Closing capture stream
        self.hackrf.closeStream(rxStream)

        return buffer

    def fft(self, z_t, window, N_fft, split):
        return True