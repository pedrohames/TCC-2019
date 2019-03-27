#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 20:40:53 2018

@author: pedrohames
"""
import requests
import json
import os
import pprint

DUT = '192.168.15.4'
headers = {}
interfaces = {}
user = 'admin'
password = 'admin01'
freq_2_4 = None
freq_5 = None


def login(DUT_IP, user, password):

    data = {'data': {'username': user,'password':password}}
    headers = {}
    try:
        r_auth = requests.post('http://'+DUT_IP + '/cgi-bin/api/v3/system/login',
                               data=json.dumps(data), timeout=3)
        dict_auth = json.loads(r_auth.content.decode())
        headers['Authorization'] = 'Token '+dict_auth['data']['Token']
        headers['Content-Type']= 'application/json'
    except Exception as e:
        print(e.args)
    return headers

def check_online(DUT_IP):
    response = os.system('ping -c 1 ' + DUT_IP + ' > /dev/null')
    if response == 0:
        return True
    else:
        return False

def get_wireless_interfaces(DUT_IP, token):
    interfaces = {}
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless', 
                                      headers=token, timeout = 3)
        interfaces = json.loads(r_get_wireless.content.decode())
        return interfaces['data']
    except Exception as e:
        print(e.args)

def get_freq(DUT_IP, token):

    try:
        interfaces = get_wireless_interfaces(DUT_IP, token)
        for interface in interfaces:
            print(interface)
            if(interface['mode_ieee'] == 'b/g/n'):
                freq_2_4 = True
            elif(interface['mode_ieee'] == 'a/n'):
                freq_5 = True
            elif(interface['mode_ieee'] == 'a/n/ac'):
                freq_5 = True
    except Exception as e:
        print(e.args)

def get_channels(DUT_IP, token):
    id_interfaces = []
    regdb = {}
    channels = []
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless',
                                      headers=token, timeout = 3)
        interfaces = json.loads(r_get_wireless.content.decode())['data']
        for interface in interfaces:
            id_interfaces.append(interface['id'])
        for id_interface in id_interfaces:
            r_get_channel = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + id_interface + '/channels/BR',
                                      headers=token, timeout = 3)
            regdb[id_interface] = json.loads(r_get_channel.content.decode())['data']
        regdb_keys = regdb.keys()
        for key in regdb_keys:
            for channel in regdb[key]:
                if(channel['channel'] == 'auto'):
                    continue
                channels.append({'channel' : channel['channel'],
                                 'frequency' : channel['mhz'],
                                 'bw' : channel['supported_bw']})

        return channels
    except Exception as e:
        print(e.args)


def get_device_info(DUT_IP, token):
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/system/device',
                                      headers=token, timeout = 3)
        device_info = json.loads(r_get_wireless.content.decode())['data']
        print(device_info)
        api_version = device_info['api_version']
        fw_version = device_info['version']
        model = device_info['model']
        return api_version, fw_version, model
    except Exception as e:
        print(e.args)

def get_mcs_enable(DUT_IP, token):
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/system/device/features',
                                      headers=token, timeout = 3)
        mcs_enable = json.loads(r_get_wireless.content.decode())['data']['wireless']['enabled_wireless_client_mode']
        return mcs_enable
    except Exception as e:
        print(e.args)


def get_mac_address(DUT_IP, token):
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/lan/1/status',
                                      headers=token, timeout = 3)
        mac_address = json.loads(r_get_wireless.content.decode())['data']['mac_address']
        return mac_address
    except Exception as e:
        print(e.args)


def set_channel_5g(DUT_IP, token, channel):
    try:
        r_get_ra0 = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + freq_5,
                                      headers=token, timeout=3)
        config = json.loads(r_get_ra0.content.decode())
        config['data']['channel'] = channel
        print(config)
        r_post_ra0 = requests.put('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + freq_5,
                                  data=json.dumps(config), headers=token, timeout=3, verify=False)
        if r_post_ra0.status_code == 204:
            apply(DUT_IP, token)
        else:
            raise ValueError('Cannot apply changes, try again later...')
    except Exception as e:
        print(e.args)


def set_channel_2g(DUT_IP, token, channel):
    try:
        r_get_ra0 = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + freq_2_4,
                                      headers=token, timeout=3)
        config = json.loads(r_get_ra0.content.decode())
        config['data']['channel'] = channel
        print(config)
        r_post_ra0 = requests.put('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + freq_2_4,
                              data=json.dumps(config), headers = token, timeout=3, verify=False)
        if r_post_ra0.status_code == 204:
            apply(DUT_IP, token)
        else:
            raise ValueError('Cannot apply changes, try again later...')
    except Exception as e:
        print(e.args)


def enable_ssh(DUT_IP, token, port = 22):
    config = {
        'data': {
            'enabled': True,
            'port': port,
            'wan_access': False
        }
    }
    try:
        r_post_ssh = requests.put('http://' + DUT + '/cgi-bin/api/v3/service/ssh',
                               data=json.dumps(config), headers = token, timeout=3, verify=False)
        return r_post_ssh.status_code
    except Exception as e:
        print(e.args)


def apply(DUT_IP, token):
    try:
        r_post_ra0 = requests.post('http://' + DUT_IP + '/cgi-bin/api/v3/system/apply',
                                   headers = token, timeout=3)
        return r_post_ra0.content.decode()
    except Exception as e:
        print(e.args)


token = login(DUT,user, password)
print('Resultado do login:\n',token)

token1 = {'Authorization': 'Token f1473fab1977fbccp2ef26460cghe34b', 'Content-Type': 'application/json'}

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

mac_address = get_mac_address(DUT, token)
print('Resultado do get MAC\n', mac_address)

mcs_enable = get_mcs_enable(DUT, token)
print('Resultado do mcs_enable\n', mcs_enable)

freq = get_freq(DUT, token)
print('Resultado do get_freq\n', freq)

#r_enable_ssh = enable_ssh(DUT, token)
#print('Resultado do get enable ssh\n', r_enable_ssh)

print('Resultado dos set channel')
set_channel_2g(DUT, token, '5')
set_channel_5g(DUT, token, '36')

#apply(DUT,token)
#get_freq(DUT, token)
#print('ping DUT: ',check_online(DUT))
#print('ping GTW: ',check_online('192.168.15.1'))
#print('ping NOK: ',check_online('172.16.8.1'))