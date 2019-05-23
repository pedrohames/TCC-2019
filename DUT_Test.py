#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 20:40:53 2018

@author: pedrohames
"""
import DUT

dut_Address = '192.168.15.5'
user = 'admin'
password = 'admin01'

my_dut = DUT.DUT(dut_Address, user, password)

my_dut.print_status()
my_dut.set_channel('2.4G', 1)
my_dut.set_channel('5G', 36)
my_dut.set_bw('2.4G', 40)
my_dut.set_bw('5G', 40)
my_dut.print_status()

