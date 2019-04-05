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


class Com(QtCore.QObject):
    pass


com = Com()


class Worker(QtCore.QObject):
    """opc-сервер"""
    finished = QtCore.pyqtSignal()

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        global com
        super().__init__(parent)
        self.running = False
        self.name = port
        self.port = Maybe(port)(self.open_serial, baud)(self.modbus_master)(self.set_timeout, timeout)
        if self.port.value is None:
            print(self.port.error)
        self.port = self.port.value
        self.com = com
        self.dev = []

    def run(self):
        if self.port is not None:
            print('Запущен сервер {}'.format(self.name))
            self.running = True

        while self.running:
            for dev in self.dev:
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

        self.dev = [self.ai, self.di, self.do1, self.do2, self.ao, self.pv1, self.pv2, self.pa1, self.pa2, self.pa3]
        for dev in self.dev:
            dev.setActive()


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
        self.freq.k = [0.0078125, 0.0078125, 1, 1, 0, 1, 1, 1]
        self.freq.eps = [0.05, 0.05, 1, 1, 0, 5, 5, 5]
        self.dev = [self.freq]
        self.freq.setActive()


class Server(QtCore.QObject):
    """класс запускающий и останавливающий opc-сервера"""
    finished = QtCore.pyqtSignal()

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

    def start(self):
        print('Запуск сервера')
        for th in self.pool:
            th.start()

    def stop(self):
        for worker in self.workers:
            worker.running = False
        for th in self.pool:
            th.wait(5000)
        self.finished.emit()
        print('Сервер остановлен')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QWidget()
    win.show()
    win.s = Server()
    win.s.start()

    app.exec_()
