import SDR

Fc = 100.9e6
Bw = 1e6
Fs = 2e6
sec = 1

my_SDR = SDR.SDR(Fs, Bw, Fc)

s_t = my_SDR.receive(sec)


