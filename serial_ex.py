import serial
import pexpect


class SerialWrapper:
    def __init__(self, mac_address):
        self.mac_address = mac_address
        print(f'Binding device {mac_address} to rfcomm0')
        pexpect.spawn(f'rfcomm bind rfcomm0 {mac_address}')
        print('Opening port')
        self.ser = serial.Serial('/dev/rfcomm0')
        print(f'Port {self.ser.name} open')

    def __del__(self):
        print(f'Ubinding device {mac_address}')
        pexpect.spawn(f'rfcomm unbind rfcomm0 {mac_address} from rfcomm0')
        print('Closing port')
        self.ser.close()

    def readline(self):
        return self.ser.readline().decode().strip()


mac_address = '00:20:12:08:B6:73'
ser = SerialWrapper(mac_address)
for i in range(10):
    print(ser.readline())
