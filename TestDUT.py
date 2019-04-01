#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 20:40:53 2018

@author: pedrohames
"""
import DUT

dut_Address = '192.168.15.4'
user = 'admin'
password = 'admin01'

my_dut = DUT.DUT(dut_Address, user, password)

my_dut.status()
my_dut.traffic_gen(my_dut.interface_5g, '192.168.15.132', 20, 20)
#my_dut.set_channel_2g(1)
#my_dut.set_channel_5g(36)
#my_dut.status()

