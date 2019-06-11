import SDR
import DUT
import numpy as np
import threading
import os
import time
import datetime
import sys
import random
import csv


class Tester:

    def __init__(self, dut_ip, user, password, server_ip):
        self.dut = DUT.DUT(dut_ip, user, password)
        print('Device Under Test successfully started')
        print(f'Model: {self.dut.model}')
        print(f'Firmware: {self.dut.fw_version}')
        print(f'Api version: {self.dut.api_version}')
        self.sdr = SDR.SDR()
        self.server_ip = server_ip
        self.ms_split_fft = 10
        self.sleep_time = 10
        self.sdr_bw = self.sdr.supported_bw

    def random_test(self, ratio, ms, n_fft, band=None, verbose=False, save=True, plot=False):
        str_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        path = f'./results/{self.dut.model}/{self.dut.fw_version}/{str_time}'
        result = []
        if band is None:
            test_channels = self.dut.channels.values
        elif band in ['2.4G', '5G']:
            test_channels = self.dut.channels[band]
        else:
            raise ValueError(f'Band {band} does not match')
        number_channels = round(len(test_channels) * ratio)
        channels = random.sample(test_channels, number_channels)
        for channel in channels:
            for bw in channel['bw']:
                if str(bw) in self.sdr_bw:
                    if str(bw) in self.sdr_bw:
                        self.verbose_check(verbose, f"\nRandom setup: Fc={channel['MHz']} MHz and bw={bw} MHz")
                        result.append({'ch_number': channel['number'],
                                       'fc': channel['MHz'],
                                       'bw': bw,
                                       'result': self.spectral_mask_test(channel, bw, ms, n_fft, path, plot=plot, save=save, verbose=verbose)})
        if save:
            try:
                with open(f'{path}/result.csv', 'w', newline='') as csvfile:
                    fieldnames = result[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerows(result)
            except Exception as e:
                print(e)
        return result

    def full_test(self, ms, n_fft, band=None, verbose=False, save=True, plot=False):
        channels = self.dut.channels
        str_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        path = f'./results/{self.dut.model}/{self.dut.fw_version}/{str_time}'
        result = []
        test_channels = []
        if band is None:
            test_channels.append(value for value in channels.values())
        elif band in ['2.4G', '5G']:
            test_channels = channels[band]
        else:
            raise ValueError(f'Band {band} does not match')
        for channel in test_channels:  # loop responsable to test all channels
            for bw in channel['bw']:
                if str(bw) in self.sdr_bw:
                    self.verbose_check(verbose, f"\nFull loop setup: Fc={channel['MHz']} MHz and bw={bw} MHz")
                    result.append({'ch_number': channel['number'],
                                   'fc': channel['MHz'],
                                   'bw': bw,
                                   'result': self.spectral_mask_test(channel, bw, ms, n_fft, path, plot=plot, save=save, verbose=verbose)})
        if save:
            try:
                with open(f'{path}/result.csv', 'w', newline='') as csvfile:
                    fieldnames = result[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerows(result)
            except Exception as e:
                print(e)
        return result

    @staticmethod
    def verbose_check(verbose, str_to_print):
        if verbose:
            print(str_to_print)

    @staticmethod
    def traffic_gen(address, seconds):
        command = f'iperf -c {address} -i 1 -P 2 -t {int(seconds)} > /dev/null'
        print(command)
        os.system(command)

    @staticmethod
    def ping(address):
        response = os.system(f'ping -c 3 {address} > /dev/null')
        return response == 0

    @staticmethod
    def path_creator(path):
        if not os.path.exists(path):
            os.system(f'mkdir -p {path}')

    def spectral_mask_test(self, channel, bw, ms, n_fft, path, plot=False, save=True, verbose=False, fake_check=False):
        freq = channel['MHz']
        channel_number = int(channel['number'])
        if channel_number <= 14:
            band = '2.4G'
        else:
            band = '5G'
        self.verbose_check(verbose, f'Setting DUT with Fc={freq} MHz and BW={bw}.')
        self.dut.set_bw(band, bw, apply=False)
        self.dut.set_channel(band, channel_number)
        time.sleep(self.sleep_time)
        self.verbose_check(verbose, f'Waiting for server to get back online.')
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts*2:
            sys.stdout.write('.')
            if self.ping(self.server_ip):
                sys.stdout.write('\n')
                break
            else:
                if attempts == max_attempts - 1:
                    sys.stdout.write('\n')
                    self.verbose_check(verbose, f"Wasn't possible to reach the server with this setup, going to test with the next one.")
                    return -1
                else:
                    attempts += 1
                    time.sleep(self.sleep_time/2 + attempts)
        self.verbose_check(verbose, 'Server online again, starting traffic generator.')
        th = threading.Thread(target=self.traffic_gen, args=(self.server_ip, np.ceil((ms / 1000) + self.sleep_time)))
        th.start()
        time.sleep(5)
        self.verbose_check(verbose, f'Starting the capture at {freq} MHz during {ms} ms.')
        s_t = self.sdr.receive(freq, ms)
        self.verbose_check(verbose, f'Signal processing...')
        s_f = self.sdr.fft_split(s_t, n_fft, self.ms_split_fft)
        s_f_max = self.sdr.max_freq_hold(s_f)
        if save:
            self.verbose_check(verbose, 'Saving some informations.')
            self.path_creator(path)
            s_f_max.tofile(f'{path}/{freq}_{bw}.dat')
            self.sdr.mask_plot(s_f_max, int(bw), n_fft, int(freq), path=path, save=True)
            result = self.sdr.fake_check_mask()
            self.verbose_check(verbose, f'Result for freq: {freq} MHz and bw: {bw} MHz {np.round(result*100,2)}%\n')
            return result

        if fake_check:
            result = self.sdr.fake_check_mask()
            self.verbose_check(verbose, f'Result for freq: {freq} MHz and bw: {bw} MHz {np.round(result*100,2)}%\n')
            return result
        else:
            if plot:
                self.sdr.mask_plot(s_f_max, int(bw), n_fft, int(freq))
            return self.sdr.check_mask(s_f_max, int(bw), n_fft)
