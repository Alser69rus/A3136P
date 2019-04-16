from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
import serial
from modbus_tk import modbus_rtu
from opc.monad import Maybe
import opc.owenio as owenio
from opc.electropribor import ElMultimeter
from opc.ddsgenerator import Generator
from opc.icpdas import M7084
from opc.owenpchv import Pchv
from opc.pid import PID


class Worker(QtCore.QObject):
    """opc-сервер"""
    finished = QtCore.pyqtSignal()

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        super().__init__(parent)
        self.running = False
        self.name = port
        self.port = Maybe(port)(self.open_serial, baud)(self.modbus_master)(self.set_timeout, timeout)
        if self.port.value is None:
            print(self.port.error)
        self.port = self.port.value
        self.dev = []

    def run(self):

        if self.port is not None:
            print('Запущен сервер {}'.format(self.name))
            self.running = True

        while self.running:
            for dev in self.dev:
                if self.thread() == dev.thread(): print(self.thread(), dev.thread(), dev)
                dev.update()
                self.thread().msleep(2)
                if not self.running:
                    break
            self.thread().msleep(5)

        print('Остановлен сервер {}'.format(self.name))
        self.finished.emit()

    def open_serial(self, port_name, baud_rate, *args, **kwargs):
        return serial.Serial(port_name, baud_rate, *args, **kwargs)

    def modbus_master(self, serial_port, *args, **kwargs):
        return modbus_rtu.RtuMaster(serial_port, *args, **kwargs)

    def set_timeout(self, master, timeout):
        master.set_timeout(timeout)
        return master


class Worker1(Worker):
    """сервер модулей"""

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        super().__init__(port=port, baud=baud, timeout=timeout, parent=parent)
        self.ai = owenio.AI8(self.port, 8)
        self.ai.k = [0, 0.0001, 0, 0, 0, 0, 0, 0]
        self.ai.off = [0, -0.4, 0, 0, 0, 0, 0, 0]
        self.ai.eps = [1, 0.001, 1, 1, 1, 1, 1, 1]
        self.di = owenio.DI16(self.port, 9)
        self.do1 = owenio.DO32(self.port, 1)
        self.do2 = owenio.DO32(self.port, 5)
        self.ao = owenio.AO8I(self.port, 6)

        self.pv1 = ElMultimeter(self.port, 11, k=0.01, eps=0.01, name='PV1')
        self.pv2 = ElMultimeter(self.port, 12, name='PV2')
        self.pa1 = ElMultimeter(self.port, 21, name='PA1')
        self.pa2 = ElMultimeter(self.port, 22, name='PA2')
        self.pa3 = ElMultimeter(self.port, 23, k=0.001, eps=0.001, name='PA3')

        self.pida = PID(1, 5, -0.25, 0.1)
        self.pidc = PID(10, 50, -2.5, 0.005)

        self.dev = [self.ai, self.di, self.do1, self.do2, self.ao, self.pv1, self.pv2, self.pa1, self.pa2, self.pa3]
        for dev in self.dev:
            dev.setActive()

        self.dev.append(self.pida)
        self.dev.append(self.pidc)


class Worker2(Worker):
    """сервер ПЧВ"""

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        super().__init__(port=port, baud=baud, timeout=timeout, parent=parent)
        self.pchv = Pchv(self.port, dev=2, max_speed=1565, fb_k=1.258)
        self.dev = [self.pchv]
        self.pchv.setActive()


class Worker3(Worker):
    """сервер генератора"""

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        super().__init__(port=port, baud=baud, timeout=timeout, parent=parent)
        self.gen = Generator(self.port, 100)
        self.dev = [self.gen]
        self.gen.setActive()


class Worker4(Worker):
    """сервер частотомера"""

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        super().__init__(port=port, baud=baud, timeout=timeout, parent=parent)
        self.freq = M7084(self.port, 3)
        self.freq.k = [0.0078125, 0.0078125, 1, 1, 0, 1, 1, 0.001]
        self.freq.eps = [0.05, 0.05, 1, 1, 0, 5, 5, 0.005]
        self.dev = [self.freq]
        self.freq.setActive()


class Server(QtCore.QObject):
    """класс запускающий и останавливающий opc-сервера"""
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    warning = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    btnUp_clicked = QtCore.pyqtSignal()
    btnDown_clicked = QtCore.pyqtSignal()
    btnOk_clicked = QtCore.pyqtSignal()
    btnBack_clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = []
        self.workers = [Worker1('COM1', 38400), Worker2('COM2', 38400), Worker3('COM3', 115200), Worker4('COM7', 38400)]
        for worker in self.workers:
            thread = QThread()
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit, QtCore.Qt.DirectConnection)
            self.finished.connect(thread.deleteLater)
            self.finished.connect(worker.deleteLater)
            self.pool.append(thread)

        self.ai = self.workers[0].ai
        self.di = self.workers[0].di
        self.do1 = self.workers[0].do1
        self.do2 = self.workers[0].do2
        self.ao = self.workers[0].ao
        self.pv1 = self.workers[0].pv1
        self.pv2 = self.workers[0].pv2
        self.pa1 = self.workers[0].pa1
        self.pa2 = self.workers[0].pa2
        self.pa3 = self.workers[0].pa3
        self.pida = self.workers[0].pida
        self.pidc = self.workers[0].pidc
        self.pchv = self.workers[1].pchv
        self.gen = self.workers[2].gen
        self.freq = self.workers[3].freq

        self.ai.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.di.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.do1.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.do2.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.ao.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pv1.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pv2.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pa1.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pa2.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pa3.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.gen.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.freq.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pchv.warning.connect(self.on_warning, QtCore.Qt.QueuedConnection)
        self.pchv.alarmed.connect(self.error, QtCore.Qt.QueuedConnection)
        self.pa3.updated.connect(self.on_pa3_update, QtCore.Qt.QueuedConnection)
        self.freq.updated.connect(self.on_frec_update, QtCore.Qt.QueuedConnection)
        self.ao.changed.connect(self.on_ao_change, QtCore.Qt.QueuedConnection)
        self.pida.changed.connect(self.setCurrent, QtCore.Qt.QueuedConnection)
        self.pidc.changed.connect(self.setCurrent, QtCore.Qt.QueuedConnection)

    def start(self):
        print('Запуск сервера')
        for th in self.pool:
            th.start()
        self.started.emit()

    def stop(self):
        self.pchv.stop()
        self.thread().msleep(1000)
        self.do1.value = [0] * 32
        self.do1.setActive()
        self.do2.value = [0] * 32
        self.do2.setActive()
        self.ao.value = [0] * 8
        self.ao.setActive()
        self.thread().msleep(1000)

        for worker in self.workers:
            worker.running = False
        for th in self.pool:
            th.wait(5000)
        self.finished.emit()
        print('Сервер остановлен')

    @QtCore.pyqtSlot(str)
    def on_warning(self, msg):
        self.warning.emit(msg)

    @QtCore.pyqtSlot(str)
    def on_error(self, msg):
        self.error.emit(msg)


    @QtCore.pyqtSlot(bool, bool)
    def connect_pchv(self, start=True, forward=True):
        self.do2.value[0] = True
        if forward:
            self.do2.value[1] = start
            self.do2.value[2] = False
        else:
            self.do2.value[1] = False
            self.do2.value[2] = start
        self.do2.setActive()
        self.pchv.setActive(start)

    @QtCore.pyqtSlot(bool)
    def connect_pe(self, value=True):
        self.do2.value[4] = value
        self.do2.value[5] = value
        self.do2.value[15] = value
        self.do2.setActive()

    @QtCore.pyqtSlot(bool)
    def connect_gen(self, value=True):
        self.do2.value[9:15] = [value] * 6
        self.do2.setActive()

    @QtCore.pyqtSlot(bool)
    def connect_dp(self, value=True):
        self.do2.value[15] = value
        self.do2.setActive()

    @QtCore.pyqtSlot()
    def on_pa3_update(self):
        self.pidc.setVin(self.pa3.value)

    @QtCore.pyqtSlot()
    def on_frec_update(self):
        self.pida.setVin(self.freq.value[0])

    @QtCore.pyqtSlot()
    def on_ao_change(self):
        self.pida.setVout(self.ao.value[2])
        self.pidc.setVout(self.ao.value[2])

    @QtCore.pyqtSlot(float)
    def setCurrent(self, value):
        v = int(value)
        if v < 0: v = 0
        if v > 1000: v = 1000
        self.ao.value[2] = v
        self.ao.setActive()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QWidget()
    win.show()
    win.s = Server()
    win.s.start()

    app.exec_()
