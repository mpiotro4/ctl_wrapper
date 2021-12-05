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
        print(f'Port {self.ser.name} open')

    def __del__(self):
        print(f'Unbinding device {self.mac_address}')
        pexpect.spawn(
            f'rfcomm unbind rfcomm0 {self.mac_address} from rfcomm{self.port}')
        print('Closing port')
        self.ser.close()

    def readline(self):
        return self.ser.readline().decode().strip()

    def DUPA(self):
        print('dupa')


# mac_address = '00:20:12:08:B6:73'
# ser = SerialWrapper(mac_address)
# for i in range(10):
#     print(ser.readline())
