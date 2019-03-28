import requests
import json
import os


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
        self._2_4g = None
        self._5g = None
        self.get_freq()
        self.mcs_enable = self.get_mcs_enable()
        self.enable_ssh()
        self.channels = self.get_channels()

    def login(self):
        data = {'data': {'username': self._user, 'password': self._password}}
        headers = {}
        try:
            r_auth = requests.post('http://' + self.ip + '/cgi-bin/api/v3/system/login',
                                   data=json.dumps(data), timeout=3)
            if r_auth.status_code == 200:
                dict_auth = json.loads(r_auth.content.decode())
                print(dict_auth)
                headers['Authorization'] = 'Token ' + dict_auth['data']['Token']
                headers['Content-Type'] = 'application/json'
                return headers
            else:
                raise ValueError('Wrong username or password')
        except Exception as e:
            print(e.args)

    def get_device_info(self):
        try:
            r_get_wireless = requests.get('http://' + self.ip + '/cgi-bin/api/v3/system/device',
                                          headers=self.token, timeout=3)
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

    def get_wireless_interfaces(self):
        try:
            r_get_wireless = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless',
                                          headers=self.token, timeout=3)
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
                                          headers=self.token, timeout=3)
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
                    self._2_4g = interface['id']
                elif interface['mode_ieee'] == 'a/n':
                    self._5g = interface['id']
                elif interface['mode_ieee'] == 'a/n/ac':
                    self._5g = interface['id']
        except Exception as e:
            print(e.args)

    def get_channels(self):
        id_interfaces = []
        regdb = {}
        channels = []
        try:
            interfaces = self.get_wireless_interfaces()
            for interface in interfaces:
                id_interfaces.append(interface['id'])
            for id_interface in id_interfaces:
                r_get_channel = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/'
                                             + id_interface + '/channels/BR', headers=self.token, timeout=3)
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

    def set_channel_5g(self, channel):
        try:
            r_get_ra0 = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self._5g,
                                     headers=self.token, timeout=3)
            config = json.loads(r_get_ra0.content.decode())
            config['data']['channel'] = channel
            print(config)
            r_post_ra0 = requests.put('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self._5g,
                                      data=json.dumps(config), headers=self.token, timeout=3, verify=False)
            if r_post_ra0.status_code == 204:
                self.apply()
            else:
                raise ValueError('Cannot apply changes, try again later...')
        except Exception as e:
            print(e.args)

    def set_channel_2g(self, channel):
        try:
            r_get_ra0 = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self._2_4g,
                                     headers=self.token, timeout=3)
            config = json.loads(r_get_ra0.content.decode())
            print(type(config))
            config['data']['channel'] = channel
            print('TESTE\n', config)
            r_post_ra0 = requests.put('http://' + self.ip + '/cgi-bin/api/v3/interface/wireless/' + self._2_4g,
                                      data=json.dumps(config), headers=self.token, timeout=3, verify=False)
            if r_post_ra0.status_code == 204:
                self.apply()
            else:
                raise ValueError('Cannot apply changes, try again later...')
        except Exception as e:
            print('Erro no get_channel_2g', e.args)

    def get_mac_address(self):
        try:
            r_get_status = requests.get('http://' + self.ip + '/cgi-bin/api/v3/interface/lan/1/status',
                                        headers=self.token, timeout=3)
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
                                      data=json.dumps(config), headers=self.token, timeout=3, verify=False)
            print('Código de retorno do ssh_enable', r_post_ssh.status_code)
            if r_post_ssh.status_code == 204:
                return self.apply()
            else:
                raise ValueError('Token expired, please re-login')
        except Exception as e:
            print(e.args)

    def apply(self):
        try:
            r_post = requests.post('http://' + self.ip + '/cgi-bin/api/v3/system/apply',
                                       headers=self.token, timeout=3)
            if r_post.status_code == 200:
                return json.loads(r_post.content.decode())['data']['success']
            else:
                raise ValueError('Cannot apply configurations')
        except Exception as e:
            print(e.args)
