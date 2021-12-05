# Based on ReachView code from Egor Fedorov (egor.fedorov@emlid.com)
# Updated for Python 3.6.8 on a Raspberry  Pi
from os import device_encoding
import time
import pexpect
import subprocess
import sys
import logging
logger = logging.getLogger("btctl")


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        subprocess.check_output("rfkill unblock bluetooth", shell=True)
        self.process = pexpect.spawnu("bluetoothctl", echo=False)

    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["bluetooth", pexpect.EOF]):
            raise Exception(f"failed after {command}")

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.send(*args, **kwargs)
        return self.process.before.split("\r\n")

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            self.send("scan on")
        except Exception as e:
            logger.error(e)

    def stop_scan(self):
        """Start bluetooth scanning process."""
        try:
            self.send("scan off")
        except Exception as e:
            logger.error(e)

    def make_discoverable(self):
        """Make device discoverable."""
        try:
            self.send("discoverable on")
        except Exception as e:
            logger.error(e)

    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        if not any(keyword in info_string for keyword in block_list):
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(
                        " ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2],
                    }
        return device

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        available_devices = []
        try:
            out = self.get_output("devices")
        except Exception as e:
            logger.error(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)
        return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        paired_devices = []
        try:
            out = self.get_output("paired-devices")
        except Exception as e:
            logger.error(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)
        return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()
        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output(f"info {mac_address}")
        except Exception as e:
            logger.error(e)
            return False
        else:
            return out

    def pair_with_pin(self, mac_address, pin_code):
        self.process.sendline(f'pair {mac_address}')
        time.sleep(2)
        self.process.sendline(f'{pin_code}')
        time.sleep(5)
        if self.process.expect(["bluetooth", pexpect.EOF]):
            raise Exception(f"failed after")

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            self.send(f"pair {mac_address}", 4)
        except Exception as e:
            logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to pair", "Pairing successful", pexpect.EOF]
            )
            return res == 1

    def trust(self, mac_address):
        try:
            self.send(f"trust {mac_address}", 4)
        except Exception as e:
            logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to trust", "trust succeeded", pexpect.EOF]
            )
            return res == 1

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            self.send(f"remove {mac_address}", 1)
        except Exception as e:
            logger.error(e)
            return False
        # else:
        #     res = self.process.expect(
        #         ["not available", "Device has been removed", pexpect.EOF]
        #     )
        #     return res == 1

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            self.send(f"connect {mac_address}", 2)
        except Exception as e:
            logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to connect", "Connection successful", pexpect.EOF]
            )
            return res == 1

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            self.send(f"disconnect {mac_address}", 2)
        except Exception as e:
            logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to disconnect", "Successful disconnected", pexpect.EOF]
            )
            return res == 1

    def find(self, mac_address):
        avaiable_devices = self.get_available_devices()
        module = any
        try:
            module = next(item for item in avaiable_devices
                          if item['mac_address'] == mac_address)
        except Exception as e:
            print(f"Module {mac_address} not found")
            return any
        else:
            print(f"Module found: {module}")
            return module

    def find_and_pair(self, mac_address, pin):
        device_info = self.get_device_info(mac_address)
        if 'Trusted: yes' in str(device_info) and 'Paired: yes' in str(device_info):
            return True
        else:
            self.remove(mac_address)
            print('Scanning...')
            self.start_scan()
            time.sleep(10)
            self.stop_scan()
            print('Scanning finished')
            module = self.find(mac_address)
            if(module == any):
                return False
            else:
                print("pairing...")
                self.pair_with_pin(mac_address, pin)
                print("pairing done")
                print("trusting...")
                self.trust(mac_address)
                print("device trusted")
                device_info = self.get_device_info(mac_address)
                if 'Trusted: yes' in str(device_info) and 'Paired: yes' in str(device_info):
                    return True
                else:
                    return False
