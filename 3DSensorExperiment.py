import sys
import time
import struct
import tkinter as tki
from scrolledtext import ScrolledText
import threading
import serial
from serial.tools import list_ports

title = 'Start 3DSensorExperiment'
print(title)
win = tki.Tk()
win.title(title)

def winClose():
    rcv_thread_stop.is_set()
    rcv_thread.join(1)
    win.quit()
    return

win.wm_protocol("WM_DELETE_WINDOW", winClose)

distance_val = 0
distance_str = tki.StringVar()
distance_str.set('Distance : No Sense')
distance_indicate = tki.Label(textvariable=distance_str, width=15, anchor=tki.W, justify='left',
                                         foreground='#ffffff', background='#00007f', font=("",32))
distance_indicate.pack(fill="both", anchor=tki.W)

illuminance_val = 0
illuminance_str = tki.StringVar()
illuminance_str.set('Illuminance : No Sense')
illuminance_indicate = tki.Label(textvariable=illuminance_str, width=15, anchor=tki.W, justify='left',
                                         foreground='#ffffff', background='#000000', font=("",32))
illuminance_indicate.pack(fill="both", anchor=tki.W)

xmove_val = 0
xmove_str = tki.StringVar()
xmove_str.set('  X move : No Sense')
xmove_indicate = tki.Label(textvariable=xmove_str, width=15, anchor=tki.W, justify='left',
                                         foreground='#ffffff', background='#7f0000', font=("",32))
xmove_indicate.pack(fill="both", anchor=tki.W)

ymove_val = 0
ymove_str = tki.StringVar()
ymove_str.set('  Y move : No Sense')
ymove_indicate = tki.Label(textvariable=ymove_str, width=15, anchor=tki.W, justify='left',
                                         foreground='#ffffff', background='#007f00', font=("",32))
ymove_indicate.pack(fill="both", anchor=tki.W)

txtbox_lines = 0
txtbox = ScrolledText()
txtbox.pack()

ports = list_ports.comports()
devices = [info.device for info in ports]
if len(devices) == 0:
        print("error: device not found")
else:
        print("found: device %s" % devices[0])
comdev = serial.Serial(devices[0], baudrate=115200, parity=serial.PARITY_NONE)
#comdev = serial.Serial('COM1', baudrate=115200, parity=serial.PARITY_NONE)

def set_distance(arg):
    if arg > 0 and arg < 100000:
        distance_val = arg
        str_val = 'Distance : ' + str(distance_val) + ' [mm]'
    else:
        str_val = 'Distance : No Sense'
    distance_str.set(str_val)
    return

def set_illuminance(arg):
    if arg != 0:
        illuminance_val = arg
        str_val = 'Illuminance : ' + str(illuminance_val)
        illuminance_str.set(str_val)
    return

def set_xmove(arg):
    if arg != 0:
        xmove_val = arg
        str_val = '  X move : ' + str(xmove_val) + ' [pix]'
        xmove_str.set(str_val)
    return

def set_ymove(arg):
    if arg != 0:
        ymove_val = arg
        str_val = '  Y move : ' + str(ymove_val) + ' [pix]'
        ymove_str.set(str_val)
    return

def rev_thread_func():
    while not rcv_thread_stop.is_set():
        bytesA = comdev.read(1)
        mark = int.from_bytes(bytesA, 'little')
        if mark == 36:
            bytesB = comdev.read(5)
            bytesC = comdev.read(2)
            psize = int.from_bytes(bytesC, 'little')
            bytesD = comdev.read(psize+1)
            if psize == 5:
                val1 = int.from_bytes(bytesD[0:1], 'little')
                val2 = int.from_bytes(bytesD[1:5], 'little', signed=True)
                val3 = 0
            elif psize == 9:
                val1 = int.from_bytes(bytesD[0:1], 'little')
                val2 = int.from_bytes(bytesD[1:5], 'little', signed=True)
                val3 = int.from_bytes(bytesD[5:8], 'little', signed=True)
            else:
                val1 = 0
                val2 = 0
                val3 = 0
            if psize == 5:
                set_distance(val2)
            if psize == 9:
                set_illuminance(val1)
                set_xmove(val2)
                set_ymove(val3)

            viewtext = str(bytesA.hex()) + ' : ' + str(bytesB.hex()) + ' : ' + str(bytesC.hex()) + ' : ' + str(bytesD.hex())
#           print(viewtext)
            global txtbox_lines
            if txtbox_lines >= 100:
                txtbox.delete('1.0', '2.0')
            txtbox.insert('end', viewtext + '\n')
            txtbox_lines += 1
            txtbox.see('end')
            txtbox.focus_set()
    comdev.close()
    return

rcv_thread_stop = threading.Event()
rcv_thread = threading.Thread(target = rev_thread_func)
rcv_thread.daemon = True
rcv_thread.start()

win.mainloop()
