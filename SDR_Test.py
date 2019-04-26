import SDR
import matplotlib.pyplot as plt
import numpy as np

Fc = 100.9e6
Bw = 3e6
Fs = 10e6
msec = 10e3
N_fft = 2048

my_SDR = SDR.SDR(Fs, Bw, Fc)

s_t_list = my_SDR.receive(msec)

s_f_list = []
for s_t in s_t_list:
    s_f_list.append(my_SDR.fft(s_t, N_fft))


max_freq = my_SDR.max_freq_hold(s_f_list)
f = np.linspace(Fc-Bw/2, Fc+Bw/2, N_fft)
plt.plot(f, max_freq)
plt.show()
