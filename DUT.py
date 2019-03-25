class DUT():

    def __init__(self, IP, user, password):
        self.token = self.login(IP,user,password)
        device_info = self.get_device_info(IP,self.token)
        self.api_version = device_info[0]
        self.fw_version = device_info[1]
        self.model = device_info[2]
        self.mac_address = self.get_mac_address(IP,self.token)
        self.enable_ssh(IP,self.token)

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
            return False

    def get_mac_address(self, DUT_IP, token):
        try:
            r_get_wireless = requests.get('http://' + DUT_IP + '/cgi-bin/api/v3/interface/lan/1/status',
                                          headers=token, timeout=3)
            mac_address = json.loads(r_get_wireless.content.decode())['data']['mac_address']
            return mac_address
        except Exception as e:
            return False

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
            return False

    def apply(self, DUT_IP, token):
        try:
            r_post_ra0 = requests.post('http://' + DUT_IP + '/cgi-bin/api/v3/system/apply',
                                       headers=token, timeout=3)
            return r_post_ra0.content.decode()
        except Exception as e:
            return False