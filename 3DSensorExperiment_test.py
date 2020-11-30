import sys
import time
import struct
import threading
import serial
from serial.tools import list_ports

ports = list_ports.comports()
devices = [info.device for info in ports]
if len(devices) == 0:
        print("error: device not found")
else:
        print("found: device %s" % devices[0])
comdev = serial.Serial(devices[0], baudrate=115200, parity=serial.PARITY_NONE)
#comdev = serial.Serial('COM1', baudrate=115200, parity=serial.PARITY_NONE)

def rev_thread_func():
    while not rcv_thread_stop.is_set():
        bytesA = comdev.read(1)
        mark = int.from_bytes(bytesA, 'little')
        if mark == 36:
            bytesB = comdev.read(5)
            bytesC = comdev.read(2)
            psize = int.from_bytes(bytesC, 'little')
            bytesD = comdev.read(psize)
            bytesE = comdev.read(1)
            if psize == 5:
                val1 = int.from_bytes(bytesD[0:1], 'little')
                val2 = int.from_bytes(bytesD[1:5], 'little', signed=True)
                val3 = 0
                tabs = '\t\t'
            elif psize == 9:
                val1 = int.from_bytes(bytesD[0:1], 'little')
                val2 = int.from_bytes(bytesD[1:5], 'little', signed=True)
                val3 = int.from_bytes(bytesD[5:8], 'little', signed=True)
                tabs = '\t'
            else:
                continue
            viewtext1 = str(bytesA.hex()) + ' : ' + str(bytesB.hex()) + ' : ' + str(bytesC.hex()) + ' : ' + str(bytesD.hex()) + ' : ' + str(bytesE.hex())
            viewtext2 = '(' + str(val1) + ',' + str(val2) + ',' + str(val3) + ')'
            print(viewtext1, tabs, viewtext2)
    comdev.close()
    return

rcv_thread_stop = threading.Event()
rcv_thread = threading.Thread(target = rev_thread_func)
rcv_thread.daemon = True
rcv_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    rcv_thread_stop.is_set()
    rcv_thread.join(1)
    print("done")
