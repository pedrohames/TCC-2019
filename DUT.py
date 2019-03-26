class DUT():

    def __init__(self, IP, user, password):
        self.token = self.login(IP,user,password)
        device_info = self.get_device_info(IP,self.token)
        self.api_version = device_info[0]
        self.fw_version = device_info[1]
        self.model = device_info[2]
        self.mac_address = self.get_mac_address(IP,self.token)
        self._2_4g = None
        self._5g = None
        self.get_freq(IP,self.token)
        self.mcs_enable = self.get_mcs_enable(IP,token)
        self.enable_ssh(IP,self.token)
        self. channels = self.get_channels(IP, self.token)

    def login(self, DUT_IP, user, password):
        data = {'data': {'username': user, 'password': password}}
        headers = {}
        try:
            r_auth = requests.post('http://' + DUT_IP + '/cgi-bin/api/v3/system/login',
                                   data=json.dumps(data), timeout=3)
            dict_auth = json.loads(r_auth.content.decode())
            print(dict_auth)
            headers['Authorization'] = 'Token ' + dict_auth['data']['Token']
            headers['Content-Type'] = 'application/json'
            return headers
        except Exception as e:
            print(e.args)

    def get_device_info(self, DUT_IP, token):
        try:
            r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/system/device',
                                          headers=token, timeout=3)
            device_info = json.loads(r_get_wireless.content.decode())['data']
            api_version = device_info['api_version']
            fw_version = device_info['version']
            model = device_info['model']
            return api_version, fw_version, model
        except Exception as e:
            print(e.args)

    def check_online(self, DUT_IP):
        response = os.system('ping -c 1 ' + DUT_IP + ' > /dev/null')
        if response == 0:
            return True
        else:
            return False

    def get_wireless_interfaces(self, DUT_IP, token):
        interfaces = {}
        try:
            r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless',
                                          headers=token, timeout=3)
            interfaces = json.loads(r_get_wireless.content.decode())
            return interfaces['data']
        except Exception as e:
            print(e.args)

    def get_mcs_enable(DUT_IP, token):
        try:
            r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/system/device/features',
                                          headers=token, timeout=3)
            mcs_enable = json.loads(r_get_wireless.content.decode())['data']['wireless']['enabled_wireless_client_mode']
            return mcs_enable
        except Exception as e:
            print(e.args)

    def get_freq(self, DUT_IP, token):
        try:
            interfaces = get_wireless_interfaces(DUT_IP, token)
            for interface in interfaces:
                if (interface['mode_ieee'] == 'b/g/n'):
                    self._2_4g = interface['id']
                elif (interface['mode_ieee'] == 'a/n'):
                    self._5g = interface['id']
                elif (interface['mode_ieee'] == 'a/n/ac'):
                    self._5g = interface['id']
        except Exception as e:
            print(e.args)

    def get_channels(self, DUT_IP, token):
        id_interfaces = []
        regdb = {}
        channels = []
        try:
            interfaces = self.get_wireless_interfaces(DUT_IP, token)
            for interface in interfaces:
                id_interfaces.append(interface['id'])
            for id_interface in id_interfaces:
                r_get_channel = requests.get(
                    'http://' + DUT_IP + '/cgi-bin/api/v3/interface/wireless/' + id_interface + '/channels/BR',
                    headers=token, timeout=3)
                regdb[id_interface] = json.loads(r_get_channel.content.decode())['data']
            regdb_keys = regdb.keys()
            for key in regdb_keys:
                for channel in regdb[key]:
                    if (channel['channel'] == 'auto'):
                        continue
                    channels.append({'channel': channel['channel'],
                                     'frequency': channel['mhz'],
                                     'bw': channel['supported_bw']})

            return channels
        except Exception as e:
            print(e.args)

    def get_mac_address(self, DUT_IP, token):
        try:
            r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/lan/1/status',
                                          headers=token, timeout=3)
            mac_address = json.loads(r_get_wireless.content.decode())['data']['mac_address']
            return mac_address
        except Exception as e:
            print(e.args)

    def enable_ssh(self, DUT_IP, token, port = 22):
        config = {
            'data': {
                'enabled': True,
                'port': port,
                'wan_access': False
            }
        }
        try:
            r_post_ssh = requests.put('http://' + DUT + '/cgi-bin/api/v3/service/ssh',
                                      data=json.dumps(config), headers=token, timeout=3, verify=False)
            if(r_post_ssh.status_code == 204):
                return = self.apply(DUT_IP, token)['data']['sucess']
            else:
                return False
        except Exception as e:
            print(e.args)

    def apply(self, DUT_IP, token):
        try:
            r_post_ra0 = requests.post('http://' + DUT_IP + '/cgi-bin/api/v3/system/apply',
                                       headers=token, timeout=3)
            return r_post_ra0.content.decode()
        except Exception as e:
            print(e.args)