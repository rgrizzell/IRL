import serial
import time

with serial.serial_for_url('/dev/ttyACM1', baudrate=115200, timeout=0.1) as trinket:
    trinket.write(b'\r\n')
    time.sleep(1)  # give the connection a second to settle
    print(trinket)
    txt = b'help\r\n'

    i = 0
    while True:
        if i == 0:
            trinket.write(txt)

        data = trinket.readline()
        if data:
            print(data.decode('utf-8'), end='')

        i = (i + 1) % 64
