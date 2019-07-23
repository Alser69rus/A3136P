import serial
from modbus_tk import modbus_rtu
import opc.owenio as owenio
from opc.electropribor import ElMultimeter
from opc.owenpchv import Pchv
from opc.icpdas import M7084
import time

port1 = serial.Serial('COM1', 38400)
master1 = modbus_rtu.RtuMaster(port1)
master1.set_timeout(0.05)
ao = owenio.AO8I(master1, 6)
pa3 = ElMultimeter(master1, 23, k=0.001, eps=0.001, name='PA3')
do2 = owenio.DO32(master1, 5, name='DO2')

port2 = serial.Serial('COM2', 38400)
master2 = modbus_rtu.RtuMaster(port2)
master2.set_timeout(0.05)
pchv = Pchv(master2, dev=2, max_speed=1565, fb_k=1.258)

port3 = serial.Serial('COM7', 38400)
master3 = modbus_rtu.RtuMaster(port3)
master3.set_timeout(0.05)
freq = M7084(master3, 3)
freq.k = [0.0078125, 0.0078125, 1, 1, 0, 1, 1, 0.001]
freq.eps = [0.05, 0.05, 1, 1, 0, 5, 5, 0.005]


def connect_pchv(start=True, reverse=True):
    do2.value[0] = True
    if reverse:
        do2.setValue(False, 1)
        do2.setValue(start, 2)
    else:
        do2.setValue(start, 1)
        do2.setValue(False, 2)
    pchv.setActive(start)


def connect_pe(value=True):
    do2.setValue(value, 4)
    do2.setValue(value, 5)
    do2.setValue(value, 15)


def connect_dp(value=True):
    do2.setValue(value, 15)


connect_pchv(True, False)
connect_pe()
connect_dp()
print('dev_connected')
pa3.setActive(True)
pchv.setActive(True)
freq.setActive(True)
ao.setActive(True)

while True:
    try:
        pchv.set_speed (500)
        pchv.setActive(True)
        do2.update()
        pchv.update()
        if pchv.current_speed>100:break
    except Exception:
        pass

print('PCHV Started')

while pchv.current_speed < 400:
    try:
        pchv.set_speed (500)
        pchv.update()
        print(f'pchv speed {pchv.current_speed}')
    except Exception:
        pass

print('speed ok')

cur = 0
u = []
dp = []
i = []
a = []


print('повышение тока')
while cur < 1000:
    try:
        ao.setValue(cur, 2)
        ao.update()
        pa3.update()
        freq.update()
        u.append(cur)
        dp.append(freq.value[7])
        i.append(pa3.value)
        a.append(freq.value[0])
        print(f'cur {cur}, dp {freq.value[7]:6.3f}, I {pa3.value:5.3f}, a{freq.value[0]:4.2f}')
        if pa3.value >= 2.5 or freq.value[0]>9:
            print("break up")
            break
        cur += 1
        time.sleep(0.05)
    except Exception:
        pass

print('снижение тока')
while cur > 50:
    try:
        ao.setValue(cur, 2)
        ao.update()
        pa3.update()
        freq.update()
        u.append(cur)
        dp.append(freq.value[7])
        i.append(pa3.value)
        a.append(freq.value[0])
        print(f'cur {cur}, dp {freq.value[7]:6.3f}, I {pa3.value:5.3f}, a{freq.value[0]:4.2f}')
        if pa3.value <0.05:
            break
        cur -= 1
        time.sleep(0.05)
    except Exception:
        pass
print('запись')
with open('temp.txt', 'w') as f:
    for n in range(len(u)):
        f.write(f'{u[n]} {dp[n]:6.3f} {i[n]:5.3f} {a[n]:4.2f}\n')

print('stop pchv')
while pchv.current_speed > 40:
    try:
        pchv.set_speed (0)
        pchv.setActive(True)
        pchv.update()
        print(f'pchv speed {pchv.current_speed}')
    except Exception:
        pass
do2.setValue([0]*32)
do2.update()