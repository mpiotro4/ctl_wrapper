import serial
import pexpect


class SerialWrapper:
    def __init__(self, mac_address, port):
        self.mac_address = mac_address
        self.port = port
        print(f'Binding device {mac_address} to rfcomm{self.port}')
        pexpect.spawn(f'rfcomm bind rfcomm{self.port} {mac_address}')
        print('Opening port')
        self.ser = serial.Serial(f'/dev/rfcomm{self.port}')
        print(f'Port {self.ser.name} opened')

    def __del__(self):
        self.ser.close()
        print(f'Unbinding device {self.mac_address}')
        pexpect.spawn(
            f'rfcomm unbind rfcomm0 {self.mac_address} from rfcomm{self.port}')
        print('Closing port')

    def readline(self):
        output = None
        try:
            output = self.ser.readline().decode().strip()
        except:
            return None
        else:
            return output
