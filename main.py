import serial_wrapper
import bluetoothctl_wrapper


def get_measurement(mac_address, pin, port):
    bt = bluetoothctl_wrapper.Bluetoothctl()
    if(bt.find_and_pair(mac_address, pin)):
        hc05 = serial_wrapper.SerialWrapper(mac_address, port)
        for i in range(0, 10):
            print(hc05.readline())
    else:
        print(f'Module {mac_address} not found')


print('Test of bluetooth serial wrapper')
print('================================================')
mac_address = '00:20:12:08:B6:73'
pin = '1234'
port = 0
get_measurement(mac_address, pin, port)
print('================================================')
