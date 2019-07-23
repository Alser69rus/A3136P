import serial
from modbus_tk import modbus_rtu
import opc.owenio as owenio
from opc.electropribor import ElMultimeter
from opc.owenpchv import Pchv
from opc.icpdas import M7084

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


@QtCore.pyqtSlot(bool, bool)
def connect_pchv(self, start=True, reverse=True):
    self.do2.value[0] = True
    if reverse:
        self.do2.setValue(False, 1)
        self.do2.setValue(start, 2)
    else:
        self.do2.setValue(start, 1)
        self.do2.setValue(False, 2)
    self.pchv.setActive(start)
