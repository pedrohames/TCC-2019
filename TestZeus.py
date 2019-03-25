#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 20:40:53 2018

@author: pedrohames
"""
import requests
import json
import pprint

DUT = '192.168.15.4'
headers = {}
interfaces = {}
channel = '3'
bandwidth = '20'
user = 'admin'
password = 'admin01'


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


def get_wireless_interfaces(DUT_IP, token):
    interfaces = {}
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless', 
                                      headers=token, timeout = 3)
        interfaces = json.loads(r_get_wireless.content.decode())
        return interfaces['data']
    except Exception as e:
        return False


def get_channels(DUT_IP, token):
    id_interfaces = []
    channels = {}
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless',
                                      headers=token, timeout = 3)
        interfaces = json.loads(r_get_wireless.content.decode())['data']
        for interface in interfaces:
            id_interfaces.append(interface['id'])
        for id_interface in id_interfaces:
            r_get_channel = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + id_interface + '/channels/BR',
                                      headers=token, timeout = 3)
            channels[id_interface] = json.loads(r_get_channel.content.decode())['data']
        return channels
    except Exception as e:
        return False


def get_device_info(DUT_IP, token):
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/system/device',
                                      headers=token, timeout = 3)
        device_info = json.loads(r_get_wireless.content.decode())['data']
        api_version = device_info['api_version']
        fw_version = device_info['version']
        model = device_info['model']
        return api_version, fw_version, model
    except Exception as e:
        return False


def get_mac_address(DUT_IP, token):
    try:
        r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/lan/1/status',
                                      headers=token, timeout = 3)
        mac_address = json.loads(r_get_wireless.content.decode())['data']['mac_address']
        return mac_address
    except Exception as e:
        return False


def update_wireless_config(self, DUT_IP, token, config):
    try:
        r_post_ra0 = requests.put('http://' + DUT + '/cgi-bin/api/v3/interface/wireless/radio0',
                               data=json.dumps(config), headers = token, timeout=3, verify=False)
        return r_post_ra0.status_code
    except Exception as e:
        return False


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
        return False


def apply(DUT_IP, token):
    try:
        r_post_ra0 = requests.post('http://' + DUT_IP + '/cgi-bin/api/v3/system/apply',
                                   headers = token, timeout=3)
        return r_post_ra0.content.decode()
    except Exception as e:
        return False


token = login(DUT,user, password)
# print('Resultado do login:\n',token)

winterfaces = get_wireless_interfaces(DUT, token)
print('Resultado do get wireless interfaces\n','Número de interfaces = ',len(winterfaces), winterfaces[0]['mode_ieee'], winterfaces[1]['mode_ieee'])

channels = get_channels(DUT, token)
print('Resultado do get channels\n', channels)

device_info = get_device_info(DUT, token)
print('Resultado do get device info\n', device_info)

mac_address = get_mac_address(DUT, token)
print('Resultado do get MAC\n', mac_address)

r_enable_ssh = enable_ssh(DUT, token)
print('Resultado do get enable ssh\n', r_enable_ssh)

print(apply(DUT,token))
