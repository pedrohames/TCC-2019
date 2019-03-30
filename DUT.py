import requests
import json
import os
import wifi
from paramiko import SSHClient, AutoAddPolicy
import threading


class DUT:

    def __init__(self, ip, user, password):
        self.ip = ip
        self._user = user
        self._password = password
        self.token = self.login()
        device_info = self.get_device_info()
        self.api_version = device_info[0]
        self.fw_version = device_info[1]
        self.model = device_info[2]
        self.mac_address = self.get_mac_address()
        self.interface_2_4g = None
        self.interface_5g = None
        self.get_freq()
        self.mcs_enable = self.get_mcs_enable()
        self.enable_ssh()
        self.setup_wifi()
        self.channels = self.get_channel_list()

    def login(self):
        data = {'data': {'username': self._user, 'password': self._password}}
        headers = {}
        try:
            r_auth = requests.post('http://' + self.ip + '/cgi-bin/api/v3/system/login',
                                   data=json.dumps(data), timeout=10)
            if r_auth.status_code == 200:
                dict_auth = json.loads(r_auth.content.decode())
                headers['Authorization'] = 'Token ' + dict_auth['data']['Token']
                headers['Content-Type'] = 'application/json'
                return headers
            else:
                raise ValueError('Wrong username or password')
        except Exception as e:
            print(e.args)

    def status(self):
        print('Model: ', self.model)
        print('Firmware version: ', self.fw_version)
        print('API version: ', self.api_version)
        print('MAC address: ', self.mac_address)
        print('2.4 GHz interface : ', (not (self.interface_2_4g is None)))
        print('2.4 channel: ', self.get_channel_2g())
        print('5 GHz interface : ', (not (self.interface_5g is None)))
        print('5 GHz channel: ', self.get_channelinterface_5g())
        print('MCS enable: ', self.mcs_enable)
        print('Channel List:\n', self.channels)

    def get_device_info(self):
        try:
            r_get_wireless = requests.get('http://' + self.ip + '/cgi-bin/api/v3/system/device',
                                          headers=self.token, timeout=10)
            if r_get_wireless.status_code == 200:
                device_info = json.loads(r_get_wireless.content.decode())['data']
                api_version = device_info['api_version']
                fw_version = device_info['version']
                model = device_info['model']
                return api_version, fw_version, model
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def check_online(self):
        response = os.system('ping -c 1 ' + self.ip + ' > /dev/null')
        return response == 0

    def _ssh_worker(self, address, seconds=10, throughput=10):
        print('Coisinha', address, seconds, throughput)

    def wifi_connect(self, ssid, password=None):
        try:
            if password is None:
                cell = list(wifi.Cell.all('wlp3s0'))[0]
                scheme = wifi.Scheme('wlp3s0', ssid, cell)
                scheme.activate()
            else:
                cell = list(wifi.Cell.all('wlp3s0'))[0]
                scheme = wifi.Scheme('wlp3s0', ssid, cell, password)
                scheme.activate()
        except Exception as e:
            print(e.args)

    def traffic_gen(self, interface, address, seconds=10, throughput=10):
        if interface == self.interface_2_4g:
            if self.wifi_connect(self.model, self.mac_address):
                th = threading.Thread(target=self._ssh_worker, args=(address, seconds, throughput,))
                th.start()
            else:
                raise ValueError('Cannot connect on Wi-Fi')
        elif interface == self.interface_5g:
            if self.wifi_connect(self.model + ' 5G', self.mac_address):
                th = threading.Thread(target=self._ssh_worker, args=(address, seconds, throughput,))
                th.start()
            else:
                raise ValueError('Cannot connect on Wi-Fi')

    def get_wireless_interfaces(self):
        try:
            r_get_wireless = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless',
                                          headers=self.token, timeout=10)
            if r_get_wireless.status_code == 200:
                interfaces = json.loads(r_get_wireless.content.decode())
                return interfaces['data']
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def get_mcs_enable(self):
        try:
            r_get_wireless = requests.get('http://' + self.ip + '/cgi-bin/api/v3/system/device/features',
                                          headers=self.token, timeout=10)
            if r_get_wireless.status_code == 200:
                mcs_enable = json.loads(r_get_wireless.content.decode())['data']['wireless'][
                    'enabled_wireless_client_mode']
                return mcs_enable
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def get_freq(self):
        try:
            interfaces = self.get_wireless_interfaces()
            for interface in interfaces:
                if interface['mode_ieee'] == 'b/g/n':
                    self.interface_2_4g = interface['id']
                elif interface['mode_ieee'] == 'a/n':
                    self.interface_5g = interface['id']
                elif interface['mode_ieee'] == 'a/n/ac':
                    self.interface_5g = interface['id']
        except Exception as e:
            print(e.args)

    def get_channel_list(self):
        id_interfaces = []
        regdb = {}
        channels = []
        try:
            interfaces = self.get_wireless_interfaces()
            for interface in interfaces:
                id_interfaces.append(interface['id'])
            for id_interface in id_interfaces:
                r_get_channel = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/'
                                             + id_interface + '/channels/BR', headers=self.token, timeout=10)
                if r_get_channel.status_code == 200:
                    regdb[id_interface] = json.loads(r_get_channel.content.decode())['data']
                else:
                    raise ValueError('Token expired, please re-login')
            for key in regdb.keys():
                for channel in regdb[key]:
                    if channel['channel'] == 'auto':
                        continue
                    channels.append({'channel': channel['channel'],
                                     'frequency': channel['mhz'],
                                     'bw': channel['supported_bw']})

            return channels
        except Exception as e:
            print(e.args)

    def set_channelinterface_5g(self, channel):
        try:
            r_get = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_5g,
                                 headers=self.token, timeout=10)
            if r_get.status_code == 200:
                config = json.loads(r_get.content.decode())
                config['data']['channel'] = str(channel)
                r_post_ra0 = requests.put(
                    'http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_5g,
                    data=json.dumps(config), headers=self.token, timeout=10, verify=False)
                if r_post_ra0.status_code == 204:
                    self.apply()
                else:
                    raise ValueError('Cannot apply changes, error: ', r_post_ra0.status_code)
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def get_channelinterface_5g(self):
        try:
            r_get = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_5g,
                                 headers=self.token, timeout=10)
            if r_get.status_code == 200:
                return json.loads(r_get.content.decode())['data']['channel']
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def set_channel_2g(self, channel):
        try:
            r_get = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_2_4g,
                                 headers=self.token, timeout=10)
            if r_get.status_code == 200:
                config = json.loads(r_get.content.decode())
                config['data']['channel'] = str(channel)
                r_post_ra0 = requests.put(
                    'http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_2_4g,
                    data=json.dumps(config), headers=self.token, timeout=10, verify=False)
                if r_post_ra0.status_code == 204:
                    self.apply()
                else:
                    raise ValueError('Cannot apply changes, error: ', r_post_ra0.status_code)
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def get_channel_2g(self):
        try:
            r_get = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_2_4g,
                                 headers=self.token, timeout=10)
            if r_get.status_code == 200:
                return json.loads(r_get.content.decode())['data']['channel']
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def get_mac_address(self):
        try:
            r_get_status = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/lan/1/status',
                                        headers=self.token, timeout=10)
            if r_get_status.status_code == 200:
                mac_address = json.loads(r_get_status.content.decode())['data']['mac_address']
                return mac_address
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def enable_ssh(self, port=22):
        config = {
            'data': {
                'enabled': True,
                'port': port,
                'wan_access': False
            }
        }
        try:
            r_post_ssh = requests.put('http://' + self.ip + '/cgi-bin/api/v3/service/ssh',
                                      data=json.dumps(config), headers=self.token, timeout=10, verify=False)
            if r_post_ssh.status_code == 204:
                return self.apply()
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def setup_wifi(self):
        try:
            r_get_2g = requests.get(
                'http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_2_4g + '/ssid/ssid1',
                headers=self.token, timeout=10)
            if r_get_2g.status_code == 200:
                config = json.loads(r_get_2g.content.decode())
                config['data']['ssid'] = self.model
                config['data']['security'] = {'password': self.mac_address, 'encryption': "psk2+ccmp"}
                r_post_ra0 = requests.put(
                    'http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_2_4g + '/ssid/ssid1',
                    data=json.dumps(config), headers=self.token, timeout=10, verify=False)
                if r_post_ra0.status_code == 204:
                    self.apply()
                else:
                    raise ValueError('Cannot apply changes, error: ', r_post_ra0.status_code)
            else:
                raise ValueError('Token expired, please re-login. Error:', r_get_2g.status_code)

            r_getinterface_5g = requests.get(
                'http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_5g + '/ssid/ssid2',
                headers=self.token, timeout=10)
            if r_getinterface_5g.status_code == 200:
                config = json.loads(r_getinterface_5g.content.decode())
                config['data']['ssid'] = self.model + ' 5G'
                config['data']['security'] = {'password': self.mac_address, 'encryption': "psk2+ccmp"}
                r_post_ra0 = requests.put(
                    'http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self.interface_5g + '/ssid/ssid2',
                    data=json.dumps(config), headers=self.token, timeout=10, verify=False)
                if r_post_ra0.status_code == 204:
                    self.apply()
                else:
                    raise ValueError('Cannot apply changes, error: ', r_post_ra0.status_code)
            else:
                raise ValueError('Token expired, please re-login. Error:', r_getinterface_5g.status_code)
        except Exception as e:
            print(e.args)

    def apply(self):
        try:
            r_post = requests.post('http://' + self.ip + '/cgi-bin/api/v3/system/apply',
                                   headers=self.token, timeout=10)
            if r_post.status_code == 200:
                return True
            else:
                raise ValueError('Cannot apply configurations')
        except Exception as e:
            print(e.args)
