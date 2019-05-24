import SDR
import DUT
import numpy as np
from subprocess import PIPE, run
import threading
import os
import time


class Tester:

    def __init__(self, dut_ip, user, password, server_ip):
        try:
            self.dut = DUT.DUT(dut_ip, user, password)
            print('Device under test successfully started')
            print(f'Model: {self.dut.model}')
            print(f'Firmware: {self.dut.fw_version}')
            print(f'Api version: {self.dut.api_version}')
            self.sdr = SDR.SDR()
            self.server_ip = server_ip
            self.ms_split_fft = 10
            self.sleep_time = 5
            self.supported_bw = [5, 10, 20]
        except Exception as e:
            print(e)

    def random_test(self, ratio, ms, n_fft, band=None):
        test_channels = []
        result = []
        if band is None:
            test_channels.append(self.dut.channels.values)
        elif band == '2.4G' or '5G':
            test_channels.append(self.dut.channels[band])
        else:
            raise ValueError(f'Band {band} does not match')
        number_channels = len(test_channels)*ratio
        indexes = np.random.randint(0, len(test_channels)-1,  number_channels)
        print(f'testing with {[test_channels[n] for n in indexes]}')
        for channel in test_channels:
            for bw in channel['supported_bw']:
                if bw in self.supported_bw:
                    result.append({'ch_number': channel['ch_number'],
                                   'fc': channel['mhz'],
                                   'bw': bw,
                                   'result': self.spectral_mask_test(channel, bw, ms, n_fft)})
        return result

    def full_test(self, ms, n_fft):
        channels = self.dut.channels.values()
        result = []

        for band in channels: # loop responsable to use both interfaces: 2.4 GHz and 5 GHz

            for channel in band: # loop responsable to test all channels
                ch_number = channel['channel']
                fc = channel['mhz']
                for bw in channel['supported_bw']:
                    if bw in self.supported_bw:
                        result.append({'ch_number': ch_number,
                                       'fc': fc,
                                       'bw': bw,
                                       'result': self.spectral_mask_test()})
        return result

    @staticmethod
    def traffic_gen(address, seconds):
        command = f'iperf -c {address} -i 1 -w 256k -p 3 -t {seconds} '
        run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)

    @staticmethod
    def ping(address):
        response = os.system(f'ping -c 3 {address} > /dev/null')
        return response == 0

    def spectral_mask_test(self, channel, bw, ms, n_fft, printable=False, fake_check=False):
        freq = channel['MHz']
        channel_number = channel['number']
        if channel_number <= 14:
            band = '2.4G'
        else:
            band = '5G'

        self.dut.set_bw(band, bw)
        self.dut.set_channel(band, channel_number)
        time.sleep(self.sleep_time)
        attempts = 0
        while attempts < 10:
            if self.ping(self.server_ip):
                break
            else:
                if attempts == 9:
                    raise ValueError('Server is not online, please check.')
                else:
                    attempts += 1
                    time.sleep(self.sleep_time)

        th = threading.Thread(target=self.traffic_gen, args=(self.server_ip, np.ceil((ms / 1000) + self.sleep_time)))
        th.start()
        s_t = self.sdr.receive(freq, ms)
        s_f = self.sdr.fft_split(s_t, n_fft, self.ms_split_fft)
        if fake_check:
            return self.sdr.fake_check_mask()
        else:
            if printable:
                self.sdr.mask_print(s_f, bw, n_fft, freq)
            return self.sdr.check_mask(s_f, bw, n_fft)
