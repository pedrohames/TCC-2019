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

print('Token:\n', my_dut.token)

#winterfaces = get_wireless_interfaces(DUT, token)
#print(winterfaces)
#print('Resultado do get wireless interfaces\n','Número de interfaces = ',len(winterfaces), winterfaces[0]['mode_ieee'], winterfaces[1]['mode_ieee'])

#channels = get_channels(DUT, token)
#channels_keys = channels.keys()
#for channel in channels:
#    print(channel)

#print('Resultado do get channels\n', channels)

#device_info = get_device_info(DUT, token)
#print('Resultado do get device info\n', device_info)

#mac_address = get_mac_address(DUT, token)
#print('Resultado do get MAC\n', mac_address)

#mcs_enable = get_mcs_enable(DUT, token)
#print('Resultado do mcs_enable\n', mcs_enable)

#freq = get_freq(DUT, token)
#print('Resultado do get_freq\n', freq)

#r_enable_ssh = enable_ssh(DUT, token)
#print('Resultado do get enable ssh\n', r_enable_ssh)

#print('Resultado dos set channel')
#set_channel_2g(DUT, token, '5')
#set_channel_5g(DUT, token, '36')

#apply(DUT,token)
#get_freq(DUT, token)
#print('ping DUT: ',check_online(DUT))
#print('ping GTW: ',check_online('192.168.15.1'))
#print('ping NOK: ',check_online('172.16.8.1'))