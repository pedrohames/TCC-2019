import sys
from time import sleep


from Shell_interact import shell


class connect:

    def __init__(self, ssid='__keep_out__', ip_address='0.0.0.0/0', ip_gw='0.0.0.0', wireless_int='wlp2s0', dns_address='8.8.8.8'):
        self.ssid = ssid
        self.ip_address = ip_address
        self.ip_gw = ip_gw
        self.wireless_int = wireless_int
        self.dns_address = dns_address

    def run(self):

        try:
            result = connect.connect_ssid(self)
            print(result)
            if result == self.ssid:
                print("conectado no SSID:", result)
                result = connect.ip_config(self)
                return True
            else:
                print("Não conectou no SSID:", result, "suppose to be:", self.ssid)
                counter = 0
                while counter < 6:
                    print("in While not connected yet")
                    result = connect.connect_ssid(self)
                    counter = counter + 1
                    sleep(2)

                    if result == self.ssid and counter < 6:
                        print("conectado no SSID:", result, " took "+str(counter), " time to connect")
                        result = connect.ip_config(self)
                        return True
                    elif result != self.ssid and counter == 5:
                        print("in While, was not able to connect on:", self.ssid)
                        return False

        except:
            print("Something went wrong module SSID in:", sys.exc_info()[0], sys.exc_info()[1])

    def connect_ssid(self):

        shell("systemctl stop network-manager").run()
        shell("rfkill unblock all").run()
        shell("ifconfig " + str(self.wireless_int) + " up").run()
        shell("iw dev " + str(self.wireless_int) + " connect \'" + str(self.ssid) + "\'").run()
        sleep(5)
        result = shell("iwconfig " + str(self.wireless_int) +" | grep \"" + str(self.wireless_int) + "\" | awk \'{ print $4 }\' | sed \'s/ESSID://\' | xargs").run()
        return result

    def try_connect(self):

        result = shell("iw dev " + str(self.wireless_int) + " connect \'" + str(self.ssid) + "\'").run()
        result = shell("iwconfig " + str(self.wireless_int) +" | grep \"" + str(self.wireless_int) + "\" | awk \'{ print $4 }\' | sed \'s/ESSID://\' | xargs").run()
        return result

    def ip_config(self):

        result = shell("ifconfig " + self.wireless_int + " " + self.ip_address).run()
        result = shell("route add default gw " + str(self.ip_gw)).run()
        result = shell("echo \"nameserver " + str(self.dns_address) + "\" > /etc/resolv.conf").run()
        return result

