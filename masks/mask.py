#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 18:28:31 2019

@author: pedrohames
"""

import numpy as np
import matplotlib.pyplot as plt

fc = 0
BW = 20e6

Nfft = 512

p28n_5 = int(np.ceil((5e6/BW)*Nfft))
p20n_5 = int(np.ceil((7.25e6/BW)*Nfft))
p0n_5 = int(np.ceil((7.75e6/BW)*Nfft))
p0p_5 = int(np.floor((12.25e6/BW)*Nfft))
p20p_5 = int(np.floor((12.75e6/BW)*Nfft))
p28p_5 = int(np.floor((15e6/BW)*Nfft))

p28n_10 = int(0)
p20n_10 = int(np.ceil((4.5e6/BW)*Nfft))
p0n_10 = int(np.ceil((5.5e6/BW)*Nfft))
p0p_10 = int(np.floor((14.5e6/BW)*Nfft))
p20p_10 = int(np.floor((15.5e6/BW)*Nfft))
p28p_10 = int(Nfft)

p10n_20 = int(0)
p0n_20 = int(np.ceil((1e6/BW)*Nfft))
p0p_20 = int(np.floor((19e6/BW)*Nfft))
p10p_20 = int(Nfft)

step =  BW/Nfft

f_axis = np.linspace((fc-BW/2)-Nfft,fc+BW/2,Nfft)
f_gain5 = np.zeros(Nfft)
f_gain10 = np.zeros(Nfft)
f_gain10[0] = -28
f_gain10[-1] = -28

f_gain20 = np.zeros(Nfft)
f_gain20[0] = -10
f_gain20[-1] = -10

for x in range(0, p28n_5):
    f_gain5[x] = -28

for x in range(p28n_5, p20n_5):
    f_gain5[x] = f_gain5[x-1] + (8/(p20n_5-p28n_5))
    
for x in range(p20n_5, p0n_5):
    f_gain5[x] = f_gain5[x-1] + (20/(p0n_5-p20n_5))
    
for x in range(p0p_5, p20p_5):
    f_gain5[x] = f_gain5[x-1] - (20/(p20p_5-p0p_5))
    
for x in range(p20p_5, p28p_5):
    f_gain5[x] = f_gain5[x-1] - (8/(p28p_5-p20p_5))

for x in range(p28p_5, Nfft):
    f_gain5[x] = -28


for x in range(p28n_10, p20n_10):
    f_gain10[x] = f_gain10[x-1] + (8/(p20n_10-p28n_10))
    
for x in range(p20n_10, p0n_10):
    f_gain10[x] = f_gain10[x-1] + (20/(p0n_10-p20n_10))
    
for x in range(p0p_10, p20p_10):
    f_gain10[x] = f_gain10[x-1] - (20/(p20p_10-p0p_10))
    
for x in range(p20p_10, p28p_10):
    f_gain10[x] = f_gain10[x-1] - (8/(p28p_10-p20p_10))
    
    
    
for x in range(p10n_20, p0n_20):
    f_gain20[x] = f_gain20[x-1] + (10/(p0n_20-p10n_20))
    
for x in range(p0p_20, p10p_20):
    f_gain20[x] = f_gain20[x-1] - (10/(p10p_20-p0p_20))
    

print(type(f_gain10[0]))
f_gain5.tofile(f'mask_5MHz_{Nfft}.dat')
f_gain10.tofile(f'mask_10MHz_{Nfft}.dat')
f_gain20.tofile(f'mask_20MHz_{Nfft}.dat')

plt.plot(f_axis/1e6, f_gain5)
plt.hold(True)
plt.plot(f_axis/1e6, f_gain10)
plt.plot(f_axis/1e6, f_gain20)
plt.legend(('5 MHz mask','10 MHz mask','20 MHz mask'))
plt.xlabel('F [MHz]')
plt.ylabel('Attenuation [dBr]')
plt.title('IEEE 802.11 spectral mask applied on 20 MHz of bandwidth')
plt.show()