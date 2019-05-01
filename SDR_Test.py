import SDR
import matplotlib.pyplot as plt
import numpy as np

Fc = 5180e6
Fs = 20e6
msec = 4e3
N_fft = 4096

my_SDR = SDR.SDR()

s_t = my_SDR.receive(Fc, Fs, msec)
print(f'len(s_t) = {len(s_t)}')

max_freq = my_SDR.fft(s_t, N_fft)
f = np.linspace(Fc-Fs/2, Fc+Fs/2, N_fft)
plt.plot(f/1e6, np.abs(max_freq))
plt.show()
