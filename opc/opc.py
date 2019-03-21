from PyQt5 import QtCore
import serial
from modbus_tk import modbus_rtu
import time
import opc
import opc.auxiliary as auxilitary
import opc.ddsgenerator as ddsgenerator
import opc.electropribor as electropribor
import opc.icpdas as icpdas
import opc.owenio as owenio
import opc.owenpchv as owenpchv


class Communucate(QtCore.QObject):
    updated = QtCore.pyqtSignal()
    updated_quality = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    suspended = QtCore.pyqtSignal()


class Server(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.c = Communucate()
        self.running = False
        self.count = 0
        self.err = False

        self.read_list = []
        self.write_list = []

        self._suspended = False

        self.master1, self.err = self.port_open('COM1', 38400, timeout=0.3)
        self.master2, self.err = self.port_open('COM2', 38400, timeout=0.3)
        self.master3, self.err = self.port_open('COM3', 115200, timeout=0.5)
        self.master4, self.err = self.port_open('COM7', 38400, timeout=0.3)

        # self.master1 = None
        # self.master2 = None
        # self.master3 = None
        # self.master4 = None

        self.connect_primary()
        self.connect_auxiliary()

        self.read_list = [self.di, self.freq]

    def connect_auxiliary(self):
        """подключение не самостоятельных приборов"""
        self.btnBack = auxilitary.Btn(self.di, 6)
        self.btnUp = auxilitary.Btn(self.di, 4)
        self.btnDown = auxilitary.Btn(self.di, 7)
        self.btnOk = auxilitary.Btn(self.di, 5)
        self.br2 = auxilitary.Encoder(self.freq, 0)
        self.br3 = auxilitary.Encoder(self.freq, 2)
        self.pida = auxilitary.PidA(25, 3, 0.1, self.pa3, self.ao, 2)

    def connect_primary(self):
        """подключение первичных приборов"""
        self.ai = owenio.AI8(self.master1, 8)
        self.ao = owenio.AO8I(self.master1, 6)
        self.di = owenio.DI16(self.master1, 9)
        self.do1 = owenio.DO32(self.master1, 1)
        self.do2 = owenio.DO32(self.master1, 5)
        self.gen = ddsgenerator.Generator(self.master3, 100)
        self.freq = icpdas.M7084(self.master4, 3)
        self.freqE = icpdas.M7084onlyE(self.master4, 3)
        self.pv1 = electropribor.ElMultimeter(self.master1, 11)
        self.pv2 = electropribor.ElMultimeter(self.master1, 12)
        self.pa1 = electropribor.ElMultimeter(self.master1, 21)
        self.pa2 = electropribor.ElMultimeter(self.master1, 22)
        self.pa3 = electropribor.ElMultimeter(self.master1, 23, 0.001)
        self.pchv = owenpchv.Pchv(self.master2, 2, 1565, 1.333)
        self.pchv_only_speed = owenpchv.PchvOnlySpeed(self.master2, 2, 1565, 1.333)

    def port_open(self, *args, **kwargs):
        """обертка открытия порта"""
        try:
            v = modbus_rtu.RtuMaster(serial.Serial(*args, **kwargs))
            return v, None
        except Exception as e:
            print(e)
            return None, e

    @QtCore.pyqtSlot()
    def run(self):
        #self.f=open('d:\\1.txt','w')
        self.running = True
        self.c.started.emit()

        while self.running:
            self.count += 1
            if self.isSuspended(): continue
            if not self.write_all(): break
            if not self.read_all(): break
            self.read_auxiliary()
            self.c.updated_quality.emit(self.get_qmsg())
            self.c.updated.emit()
            #if self.pida in self.write_list:
            #    print('v:{} u:{} p:{} i:{} d:{}'.format(self.pida.value, self.pida.u, self.pida.kp, self.pida.ki,
            #                                            self.pida.kd),file=self.f)

        self.switch_off()
        self.port_close()

        self.c.finished.emit()
        print('finished opc')
        #self.f.close()

    def isSuspended(self):
        """проверка на паузу сервера"""
        if not self.running: return False
        if self._suspended:
            self.c.suspended.emit()
            self.thread().msleep(100)
            return True

    def port_close(self):
        """закрытие сом-портов"""
        if self.master1: self.master1.close()
        if self.master2: self.master2.close()
        if self.master3: self.master3.close()
        if self.master4: self.master4.close()

    def switch_off(self):
        """отключение всех реле и контакторов, сброс аналоговых и частотных каналов"""
        self.do1.value = [0] * 32
        self.do1.write()
        self.do2.value = [0] * 32
        self.do2.write()
        self.ao.value = [0] * 8
        self.ao.write()
        self.gen.value = [0] * 3
        self.gen.write()

    def get_qmsg(self):
        """"подготовка строки статуса"""
        qmsg = 'ai:{} ao:{} di:{} do1:{} do2:{} gen:{} freq:{} pv1:{} pv2:{} pa1:{} pa2:{} pa3:{} pchv:{}'
        qmsg = qmsg.format(self.ai.quality, self.ao.quality, self.di.quality, self.do1.quality,
                           self.do2.quality, self.gen.quality, self.freq.quality, self.pv1.quality,
                           self.pv2.quality, self.pa1.quality, self.pa2.quality, self.pa3.quality,
                           self.pchv.quality)
        if not self.master1:
            qmsg += ' port1:off'
        if not self.master2:
            qmsg += ' port2:off'
        if not self.master3:
            qmsg += ' port3:off'
        if not self.master4:
            qmsg += ' port4:off'

        return qmsg

    def read_auxiliary(self):
        """процедура проверки впомогательных устройств и генерации сигналов"""
        self.btnBack.read()
        self.btnUp.read()
        self.btnDown.read()
        self.btnOk.read()
        self.br2.read()
        self.br3.read()

    def read_all(self):
        """последовательно читает все устройства в списке read_list"""
        for dev in self.read_list:
            if not self.running: return False
            if self._suspended: return True
            try:
                dev.read()
            except Exception as exc:
                self.c.error.emit(str(exc))
                print(exc)
        return True

    def write_all(self):
        """выполняет процедуру записи для всех устройств из списка write_list"""
        for dev in self.write_list:
            if not self.running: return False
            if self._suspended: return True
            try:
                dev.write()
            except Exception as exc:
                self.c.error.emit(str(exc))
                print(exc)
        return True

    @QtCore.pyqtSlot(bool)
    def suspend(self, value):
        self._suspended = value
