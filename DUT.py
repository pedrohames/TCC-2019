import json
import os
import paramiko
import requests
import threading


class DUT:

    def __init__(self, ip, user, password, tx_power=17):
        self.ip = ip
        self.timeout = 30
        self.user = user
        self.password = password
        self.interface = {'2.4G': None, '5G': None}
        self.token = self.login()
        device_info = self.get_device_info()
        self.api_version = device_info['api_version']
        self.fw_version = device_info['version']
        self.model = device_info['model'].replace(' ', '_')
        self.mac_address = self.get_mac_address()
        self.setup_freq()
        self.mcs_enable = self.get_mcs_enable()
        self.enable_ssh()
        self.enable_dfs_channels()
        self.setup_ssid()
        self.set_tx_power(tx_power)
        self.channels = self.get_channel_list()

    def login(self):
        data = {'data': {'username': self.user, 'password': self.password}}
        r_auth = requests.post(f'http://{self.ip}/cgi-bin/api/v3/system/login',
                               data=json.dumps(data), timeout=self.timeout)
        if r_auth.status_code == 200:
            dict_auth = json.loads(r_auth.content.decode())['data']
            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Token ' + dict_auth['Token']}
            return headers
        else:
            raise ValueError(f'HTTP error code: {r_auth.status_code}')

    def print_status(self):
        print('Model:', self.model)
        print('Firmware version:', self.fw_version)
        print('API version:', self.api_version)
        print('MAC address:', self.mac_address)
        print('2.4 GHz interface:', self.interface['2.4G'] is not None)
        print('2.4 GHz channel:', self.get_channel('2.4G'))
        print('5 GHz interface:', self.interface['5G'] is not None)
        print('5 GHz channel:', self.get_channel('5G'))
        print('MCS enable:', self.mcs_enable)
        print('Channel list:', self.channels)

    def _request_get(self, tail):
        r_get = requests.get(f'http://{self.ip}/cgi-bin/api/v3/{tail}',
                             headers=self.token, timeout=self.timeout)
        if r_get.status_code == 200:
            return json.loads(r_get.content.decode())['data']
        else:
            raise ValueError(f'Error: Request tail: {tail}, Error code: {r_get.status_code}')

    def _request_put(self, tail, data, apply=True):
        r_put = requests.put(f'http://{self.ip}/cgi-bin/api/v3/{tail}',
                             data=json.dumps({'data': data}), verify=False,
                             headers=self.token, timeout=self.timeout)
        if r_put.status_code == 204:
            if apply:
                r_post = requests.post(f'http://{self.ip}/cgi-bin/api/v3/system/apply',
                                       headers=self.token, timeout=self.timeout)
                if r_post.status_code == 200:
                    return True
                raise ValueError(f'Error: Could not apply: Request tail: {tail}, Error code: {r_post.status_code}')
            else:
                return True
        raise ValueError(f'Error: Request tail: {tail}, Error code: {r_put.status_code}')

    def get_device_info(self):
        return self._request_get('system/device')

    def get_mac_address(self):
        return self._request_get('interface/lan/1/status')['mac_address']

    def get_wireless_interfaces(self):
        return self._request_get('interface/wireless')

    def get_mcs_enable(self):
        return self._request_get('system/device/features')['wireless']['enabled_wireless_client_mode']

    def check_online(self):
        response = os.system(f'ping -c 1 {self.ip} > /dev/null')
        return response == 0

    def _ssh_worker(self, address, seconds, throughput):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.ip, username=self.user, password=self.password)
            ssh.exec_command(f'iperf -c {address} -t {seconds} -U -b {throughput} M')
        except Exception as e:
            print(e)

    def traffic_gen(self, address, seconds=10, throughput=10):
        th = threading.Thread(target=self._ssh_worker, args=(address, seconds, throughput))
        th.start()

    def setup_freq(self):
        interfaces = self.get_wireless_interfaces()
        for interface in interfaces:
            if interface['mode_ieee'] == 'b/g/n':
                self.interface['2.4G'] = interface['id']
            elif interface['mode_ieee'] in ['a/n', 'a/n/ac']:
                self.interface['5G'] = interface['id']

    def get_channel_list(self):
        interfaces = self.get_wireless_interfaces()

        regdb = {}
        for interface in interfaces:
            regdb[interface['id']] = self._request_get(f"interface/wireless/{interface['id']}/channels/BR")

        channels = {'2.4G': [], '5G': []}
        for value in regdb.values():
            for channel in value:
                if channel['channel'] != 'auto':
                    key = '2.4G' if int(channel['channel']) <= 14 else '5G'
                    channels[key].append({'number': channel['channel'],
                                          'MHz': channel['mhz'],
                                          'bw': channel['supported_bw']})
        return channels

    def get_channel(self, band):
        return self._request_get(f'interface/wireless/{self.interface[band]}')['channel']

    def set_channel(self, band, channel, apply=True):
        tail = f'interface/wireless/{self.interface[band]}'
        config = self._request_get(tail)
        config['channel'] = str(channel)
        self._request_put(tail, config, apply)

    def enable_dfs_channels(self, band='5G', apply=True):
        tail = f'interface/wireless/{self.interface[band]}'
        config = self._request_get(tail)
        config['enable_dfs_channels'] = True
        self._request_put(tail, config, apply)

    def set_bw(self, band, bw, apply=True):
        tail = f'interface/wireless/{self.interface[band]}'
        config = self._request_get(tail)
        config['bandwidth'] = str(bw)
        self._request_put(tail, config, apply)

    def set_tx_power(self, tx_power=17, apply=True):
        tail = f'interface/wireless/{self.interface["2.4G"]}'
        config = self._request_get(tail)
        config['txpower'] = int(tx_power)
        self._request_put(tail, config, apply)

        tail = f'interface/wireless/{self.interface["5G"]}'
        config = self._request_get(tail)
        config['txpower'] = int(tx_power)
        self._request_put(tail, config, apply)

    def enable_ssh(self, port=22, apply=True):
        config = self._request_get('service/ssh')
        config.update({'enabled': True, 'port': port, 'wan_access': False})
        self._request_put('service/ssh', config, apply)

    def setup_ssid(self, apply=True):
        for band, ssid in [('2.4G', 'ssid1'), ('5G', 'ssid2')]:
            tail = f'interface/wireless/{self.interface[band]}/ssid/{ssid}'
            config = self._request_get(tail)
            config['ssid'] = f'{self.model}_{band}'
            config['security'] = {'encryption': 'none'}  # {'password': password, 'encryption': "psk2+ccmp"}
            self._request_put(tail, config, apply)
