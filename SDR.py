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
        self.hackrf.setSampleRate(SOAPY_SDR_RX, 0, FS)
        self.hackrf.setBandwidth(SOAPY_SDR_RX, 1, BW)
        self.hackrf.setFrequency(SOAPY_SDR_RX, 1, Fc)

    def receive(self, time):
        time = 5  # Time capturing [s]
        Nsamp = int(self.FS * time)  # Number of samples
        # Inicia o stream de captura ainda desativado
        rxStream = hackrf.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32, [0])

        # Ativa o stream de captura
        hackrf.activateStream(rxStream)

        # Buffer em que serão armazenadas as amostras
        buff = np.zeros(Nsamp, np.complex64)

        # Loop de captura das amostras
        while Nsamp > 0:
            sr = hackrf.readStream(rxStream, [buff], buff.size, timeoutUs=int(1e6))
            assert sr.ret > 0  # Para o caso de erros na obtenção das amostras
            Nsamp -= sr.ret
        # Ao término do loop tem-se em buff as amostras.

        # Desativa o stream de captura
        hackrf.deactivateStream(rxStream)
        # Encerra o stream de captura
        hackrf.closeStream(rxStream)
