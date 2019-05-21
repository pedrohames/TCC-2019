import SDR
import matplotlib.pyplot as plt
import numpy as np

Fc = 5660e6
Fs = 20e6
msec = 3e3
N_fft = 4096
BW = 10e6

my_SDR = SDR.SDR()

# s_t = my_SDR.receive(Fc, Fs, msec, gain='LNA=16')  # To real time capture
s_t = my_SDR.receive_from_file(f'samples/{int(BW/1e6)}MHz_{int(Fc/1e6)}_g18.dat')

print(f'len(s_t) = {len(s_t)}')
print(f'type(s_t[0]) = {type(s_t[0])}')

# s_f = my_SDR.fft(s_t, N_fft)
s_f_list = my_SDR.fft_split(s_t,N_fft, 10, Fs)
s_f_max = my_SDR.max_freq_hold(s_f_list)

my_SDR.mask_print(s_f_max,BW, N_fft,Fc)


# max_s_f = max(s_f)
# s_f_dbr = np.empty(len(s_f))
# for x in range(0, len(s_f)):
#     s_f_dbr[x] = s_f[x] - max_s_f
#
# f = np.linspace(Fc-Fs/2, Fc+Fs/2, N_fft)
# plt.plot(f/1e6, s_f_dbr)
# plt.show()
