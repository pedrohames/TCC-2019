import SDR
import DUT
import numpy as np
from subprocess import PIPE, run
import threading
import os
import time


class Tester:

    def __init__(self, dut_ip, user, password, server_ip):
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

    def random_test(self, ratio, ms, n_fft, band=None, verbose=False):
        result = []
        if band is None:
            test_channels = self.dut.channels.values
        elif band in ['2.4G', '5G']:
            test_channels = self.dut.channels[band]
        else:
            raise ValueError(f'Band {band} does not match')
        number_channels = round(len(test_channels) * ratio)
        indexes = np.random.randint(0, len(test_channels) - 1, number_channels)
        print(indexes)
        print(f'testing with {[test_channels[n] for n in indexes]}')
        for index in indexes:
            channel = test_channels[index]
            print(channel)
            for bw in channel['bw']:
                if bw in self.supported_bw:
                    result.append({'ch_number': channel['number'],
                                   'fc': channel['MHz'],
                                   'bw': bw,
                                   'result': self.spectral_mask_test(channel, bw, ms, n_fft, printable=verbose)})
        return result

    def full_test(self, ms, n_fft, band=None, verbose=False):
        channels = self.dut.channels.values()
        result = []

        for band in channels:  # loop responsable to use both interfaces: 2.4 GHz and 5 GHz

            for channel in band:  # loop responsable to test all channels
                for bw in channel['bw']:
                    if bw in self.supported_bw:
                        result.append({'ch_number': channel['number'],
                                       'fc': channel['MHz'],
                                       'bw': bw,
                                       'result': self.spectral_mask_test(channel, bw, ms, n_fft, printable=verbose)})
        return result

    @staticmethod
    def traffic_gen(address, seconds):
        command = f'iperf -c {address} -i 1 -w 256k -P 3 -t {int(seconds)} > /dev/null'
        print(command)
        os.system(command)

    @staticmethod
    def ping(address):
        response = os.system(f'ping -c 3 {address} > /dev/null')
        return response == 0

    def spectral_mask_test(self, channel, bw, ms, n_fft, printable=False, fake_check=False):
        freq = channel['MHz']
        channel_number = int(channel['number'])
        if channel_number <= 14:
            band = '2.4G'
        else:
            band = '5G'

        self.dut.set_bw(band, bw, apply=False)
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
        s_f_max = self.sdr.max_freq_hold(s_f)
        if fake_check:
            return self.sdr.fake_check_mask()
        else:
            if printable:
                self.sdr.mask_print(s_f_max, int(bw), n_fft, int(freq))
            return self.sdr.check_mask(s_f_max, int(bw), n_fft)
