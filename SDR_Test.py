import SDR
import matplotlib.pyplot as plt
import numpy as np

Fc = 5660e6
Fs = 20e6
msec = 3e3
N_fft = 4096
BW = 20e6

my_SDR = SDR.SDR()

# s_t = my_SDR.receive(Fc, Fs, msec, gain='LNA=16')  # To real time capture
s_t = my_SDR.receive_from_file(f'samples/{int(BW/1e6)}MHz_{int(Fc/1e6)}_g18.dat')

# print(f'len(s_t) = {len(s_t)}')
# print(f'type(s_t[0]) = {type(s_t[0])}')

# s_f = my_SDR.fft(s_t, N_fft)
s_f_list = my_SDR.fft_split(s_t,N_fft, 10)
s_f_max = my_SDR.max_freq_hold(s_f_list)

print(f'Mask check: {my_SDR.check_mask(s_f_max,BW,N_fft)*100}%')

my_SDR.mask_print(s_f_max, BW, N_fft, Fc)

