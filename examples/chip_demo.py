# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# The file provides an example of using Cirque Flask Service to:
# 1. create cirque virtual home
# 2. create several devices in virtual home
# 3. form a Thread network
# 4. how devices scan for virtual wifi ap
# 5. how devices request ip address from virtual wifi ap
# 6. test network connectivities between devices
#
# Run test:
# a. in a terminal, bring up flask cirque service:
#    $ cd ~/cirque-core
#    $ sudo bazel run //cirque/restservice:service
# b. in another terminal, run test
#    $ cd ~/cirque-core
#    $ python3 example/test_flask_virtual_home.py
#

import logging
import unittest
import os
import re
import requests
import time

from urllib.parse import urljoin

SERVICE_URL = 'http://127.0.0.1:5000'

DEVICE_CONFIG = {
    'device0': {
        'type': 'Generic Node',
        'base_image': 'chip_demo',
        'capability': ['WiFi', 'Interactive'],
        'rcp_mode': True,
    },
    'device1': {
        'type': 'GenericNode',
        'base_image': 'chip_demo',
        'capability': ['WiFi', 'Thread', 'Interactive'],
        'rcp_mode': True,
    },
    'device2': {
        'type': 'GenericNode',
        'base_image': 'chip_demo',
        'capability': ['Thread', 'Interactive'],
        'rcp_mode': True,
    },
    'wifi-ap': {
        'type': 'wifi_ap',
        'base_image': 'mac80211_ap_image'
    }
}


class TestFlaskVirtualHome(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if hasattr(cls, 'logger') and cls.logger:
            return
        cls.logger = logging.getLogger('FlaskVirtualHome')
        cls.logger.setLevel(logging.INFO)
        sh = logging.StreamHandler()
        sh.setFormatter(
            logging.Formatter(
                '%(asctime)s [%(name)s] %(levelname)s %(message)s'))
        cls.logger.addHandler(sh)

    @classmethod
    def tearDownClass(cls):
        cls.logger.info('tearing down test class')

        home_ids = list(
            requests.get(
                urljoin(SERVICE_URL, 'get_homes')).json())

        cls.logger.info('home_ids: {}'.format(home_ids))

        for home_id in home_ids:
            cls.logger.info('deleting devices under home: {}'.format(home_id))
            requests.get(
                urljoin(SERVICE_URL, 'destroy_home/{}'.format(home_id)))

    def setUp(self):
        pass

    def test_001_created_home(self):
        home_id = requests.post(
            urljoin(SERVICE_URL, 'create_home'), json=DEVICE_CONFIG).json()
        self.logger.info("\ncreated home id: {}".format(home_id))

    def test_002_created_devices(self):
        home_id = list(
            requests.get(
                urljoin(SERVICE_URL, 'get_homes')).json())[0]
        home_devices = requests.get(
            urljoin(
                SERVICE_URL,
                'home_devices/{}'.format(home_id))).json().values()

    def test_005_connect_to_desired_wifi_network(self):
        home_id = list(
            requests.get(
                urljoin(SERVICE_URL, 'get_homes')).json())[0]
        ssid, psk = requests.get(
            urljoin(SERVICE_URL, 'wifi_ssid_psk/{}'.format(home_id))).json()
        self.logger.info("\nwifi ap ssid: {}, psk: {}".format(ssid, psk))
        home_devices = requests.get(
            urljoin(
                SERVICE_URL,
                'home_devices/{}'.format(home_id))).json().values()
        device_ids = [device['id'] for device in home_devices
                      if device['type'] != 'wifi_ap' and 
                      'WiFi' in device['capability']]
        for device_id in device_ids:
            self.logger.info(
                "\ndevice: {}\n connecting to desired ssid: {}".format(
                    device_id, ssid))
            ret = write_psk_to_wpa_supplicant_config(
                self.logger, home_id, device_id, ssid, psk)
            self.assertEqual(
                ret['return_code'],
                '0',
                "failed writing ssid, psk to wpa_supplicant config!!")
            ret = kill_existing_wpa_supplicant(
                self.logger, home_id, device_id)
            self.assertEqual(ret['return_code'], '0',
                             "failed kill existing wpa_supplicant")
            ret = start_wpa_supplicant(self.logger, home_id, device_id)
            self.assertEqual(ret['return_code'], '0',
                             "unable to start wpa_supplicant!!")
        time.sleep(2)

    def test_006_device_connectivity(self):
        home_id = list(
            requests.get(
                urljoin(SERVICE_URL, 'get_homes')).json())[0]
        home_devices = requests.get(
            urljoin(
                SERVICE_URL,
                'home_devices/{}'.format(home_id))).json().values()
        device_ids = [device['id'] for device in home_devices
                      if device['type'] != 'wifi_ap' and 
                      'WiFi' in device['capability']]
        dev_addrs = list()
        request_addr_command = 'dhcpcd wlan0'
        for device_id in device_ids:
            self.logger.info(
                "\nrequesting ip address from wifi ap by\ndevice:{}".format(
                    device_id))
            ret = requests.get(
                urljoin(SERVICE_URL, 'device_cmd/{}/{}/{}?stream={}'.format(
                    home_id,
                    device_id,
                    request_addr_command,
                    False)), stream=False).json()
            self.assertEqual(ret['return_code'], '0',
                             "unable to request ip address from wifi ap")
            ipaddr = re.search(
                r'wlan0: leased (\d+\.\d+\.\d+\.\d+) for (\d+) seconds',
                ret['output']).group(1)

            self.logger.info("\nip address requested: {}".format(ipaddr))
            dev_addrs.append((device_id, ipaddr))
        from IPython import embed; embed()


def start_wpa_supplicant(logger, home_id, device_id):
    logger.info("\ndevice id: {}\nstarting wpa_supplicant on device"
                .format(device_id))
    start_wpa_supplicant_command = "".join(
        ["wpa_supplicant -B -i wlan0 ",
         "-c /etc/wpa_supplicant/wpa_supplicant.conf ",
         "-f /var/log/wpa_supplicant.log -t -dd"])
    return requests.get(
        urljoin(SERVICE_URL, 'device_cmd/{}/{}/{}?stream={}'.format(
            home_id,
            device_id,
            start_wpa_supplicant_command,
            False)), stream=False).json()


def write_psk_to_wpa_supplicant_config(logger, home_id, device_id, ssid, psk):
    logger.info("\ndevice id: {}\nwriting ssid, psk to wpa_supplicant config"
                .format(device_id))
    write_psk_command = "".join(
        ["sh -c 'wpa_passphrase {} {} >> ".format(ssid, psk),
         "/etc/wpa_supplicant/wpa_supplicant.conf'"])
    return requests.get(
        urljoin(SERVICE_URL, 'device_cmd/{}/{}/{}?stream={}'.format(
            home_id,
            device_id,
            write_psk_command,
            False)), stream=False).json()


def kill_existing_wpa_supplicant(logger, home_id, device_id):
    logger.info("\ndevice id: {}\nkill existing wpa_supplicant"
                .format(device_id))
    kill_wpa_supplicant_command = 'killall wpa_supplicant'
    return requests.get(
        urljoin(SERVICE_URL, 'device_cmd/{}/{}/{}?stream={}'.format(
            home_id,
            device_id,
            kill_wpa_supplicant_command,
            False)), stream=False).json()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFlaskVirtualHome)
    unittest.TextTestRunner(verbosity=2).run(suite)
