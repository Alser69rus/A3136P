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


class Current(QtCore.QObject):
    def __init__(self, pida=None, pidc=None, freq=None, ao=None, parent=None):
        super().__init__(parent)
        self.pida = pida
        self.pidc = pidc
        self.freq = freq
        self.ao = ao
        self.active = False
        self.pida_value = pida.u
        self.pidc_value = pidc.u
        self.br3_value = freq.value[2]
        self.br3_zero = freq.value[2]
        self.manual_value = 0
        freq.updated.connect(self.on_freq_update, QtCore.Qt.QueuedConnection)
        pida.changed.connect(self.set_pida, QtCore.Qt.QueuedConnection)
        pidc.changed.connect(self.set_pidc, QtCore.Qt.QueuedConnection)
        pida.task_reached.connect(self.on_task_reached, QtCore.Qt.QueuedConnection)
        pidc.task_reached.connect(self.on_task_reached, QtCore.Qt.QueuedConnection)
        ao.updated.connect(self.on_ao_update, QtCore.Qt.QueuedConnection)

    def setActive(self, value, task=-1):
        self.active = value
        if 'pida' == value:
            self.pida.setActive(True)
            self.pidc.setActive(False)
            self.pida_value = self.pida.u
            if task >= 0: self.pida.setTask(task)
        elif 'pidc' == value:
            self.pida.setActive(False)
            self.pidc.setActive(True)
            self.pidc_value = self.pidc.u
            if task >= 0: self.pidc.setTask(task)
        elif 'br3' == value:
            self.pida.setActive(False)
            self.pidc.setActive(False)
            if task >= 0:
                self.br3_zero = self.freq.value[2] - task
            else:
                self.br3_zero = self.freq.value[2] - self.ao.value[2]
        elif 'manual' == value:
            self.pida.setActive(False)
            self.pidc.setActive(False)
            if task >= 0: self.set_manual(task)
        else:
            self.active = False
            self.pida.setActive(False)
            self.pidc.setActive(False)
            self.ao.setActive(False)
        self.ao.setActive()

    @QtCore.pyqtSlot(float)
    def set_pida(self, value):
        self.pida_value = value

    @QtCore.pyqtSlot(float)
    def set_pidc(self, value):
        self.pidc_value = value

    @QtCore.pyqtSlot(float)
    def set_manual(self, value):
        self.manual_value = value

    @QtCore.pyqtSlot(float)
    def set_br3(self, value):
        self.br3_value = value

    @QtCore.pyqtSlot()
    def on_freq_update(self):
        v = self.freq.value[2]
        if v != self.br3_value:
            self.set_br3(v)

    @QtCore.pyqtSlot()
    def on_ao_update(self):
        if 'pida' == self.active:
            self.setValue(self.pida_value)
        elif 'pidc' == self.active:
            self.setValue(self.pidc_value)
        elif 'br3' == self.active:
            self.setValue(self.br3_value - self.br3_zero)
        elif 'manual' == self.active:
            self.setValue(self.manual_value)
        else:
            self.ao.setActive(False)

    @QtCore.pyqtSlot(float)
    def setValue(self, value):
        v = round(value)
        if v < 0: v = 0
        if v > 1000: v = 1000
        self.ao.setValue(v, 2)

    def on_task_reached(self):
        self.setActive(False)


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
        master=None
        try:
            master = modbus_rtu.RtuMaster(serial_port, *args, **kwargs)
            return master
        except Exception:

            if not (master is None):
                master._serial.close()
            raise

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
        self.do1 = owenio.DO32(self.port, 1, name='DO1')
        self.do2 = owenio.DO32(self.port, 5, name='DO2')
        self.ao = owenio.AO8I(self.port, 6)

        self.pv1 = ElMultimeter(self.port, 11, k=0.01, eps=0.01, name='PV1')
        self.pv2 = ElMultimeter(self.port, 12, name='PV2')
        self.pa1 = ElMultimeter(self.port, 21, name='PA1')
        self.pa2 = ElMultimeter(self.port, 22, name='PA2')
        self.pa3 = ElMultimeter(self.port, 23, k=0.001, eps=0.001, name='PA3')

        self.pida = PID(0.7, 4, -0.25, 0.2)
        self.pidc = PID(10, 50, -2.5, 0.02)

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
        self.pchv.setActive(False)


class Worker3(Worker):
    """сервер генератора"""

    def __init__(self, port=None, baud=9600, timeout=0.05, parent=None):
        super().__init__(port=port, baud=baud, timeout=timeout, parent=parent)
        self.gen = Generator(self.port, 100)
        self.dev = [self.gen]
        self.gen.setActive()


class Worker4(Worker):
    """сервер частотомера"""

    def __init__(self, port=None, baud=9600, timeout=0.1, parent=None):
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
    dp_changed = QtCore.pyqtSignal(float)
    br2_changed = QtCore.pyqtSignal(float)
    br3_changed = QtCore.pyqtSignal(float)
    pressure_change = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = []
        self.workers = [Worker1('COM1', 38400), Worker2('COM2', 38400), Worker3('COM4', 115200), Worker4('COM7', 38400)]
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
        self.br2 = self.freq.value[0]
        self.br3 = self.freq.value[2]
        self.dp = self.freq.value[7]
        self.pressure = self.ai.value[1]
        self.current = Current(self.pida, self.pidc, self.freq, self.ao)

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
        self.freq.updated.connect(self.on_freq_update, QtCore.Qt.QueuedConnection)
        self.freq.changed.connect(self.on_freq_change, QtCore.Qt.QueuedConnection)
        self.ao.changed.connect(self.on_ao_change, QtCore.Qt.QueuedConnection)
        self.ai.changed.connect(self.on_ai_change, QtCore.Qt.QueuedConnection)

    def start(self):
        print('Запуск сервера')
        for th in self.pool:
            th.start()
        self.started.emit()

    def stop(self):
        self.pchv.stop()
        self.thread().msleep(1000)
        self.do1.setValue([0] * 32)
        self.do2.setValue([0] * 32)
        self.ao.setValue([0] * 8)
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
    def connect_pchv(self, start=True, reverse=True):
        self.do2.value[0] = True
        if reverse:
            self.do2.setValue(False, 1)
            self.do2.setValue(start, 2)
        else:
            self.do2.setValue(start, 1)
            self.do2.setValue(False, 2)
        self.pchv.setActive(start)

    @QtCore.pyqtSlot(bool, bool)
    def connect_bu_power(self, value=True, reserve=False):
        if reserve:
            self.do1.setValue(False, 24)
            self.do1.setValue(value, 25)
        else:
            self.do1.setValue(value, 24)
            self.do1.setValue(False, 25)

    def connect_bu_di_power(self, value=True, voltage=75):
        if voltage == 110:
            self.do1.value = self.do1.value[:16] + [0, 0, 0, value, 0, 0] + self.do1.value[22:]
            self.do1.setValue(False, 27)
        elif voltage == -110:
            self.do1.value = self.do1.value[:16] + [0, 0, value, 0, 0, 0] + self.do1.value[22:]
            self.do1.setValue(True, 27)
        elif voltage == 75:
            self.do1.value = self.do1.value[:16] + [0, 0, 0, value, 0, value] + self.do1.value[22:]
            self.do1.setValue(False, 27)
        elif voltage == 48:
            self.do1.value = self.do1.value[:16] + [value, 0, 0, 0, 0, 0] + self.do1.value[22:]
            self.do1.setValue(False, 27)
        elif voltage == 24:
            self.do1.value = self.do1.value[:16] + [0, value, 0, 0, 0, 0] + self.do1.value[22:]
            self.do1.setValue(False, 27)
        else:
            self.do1.value = self.do1.value[:16] + [0, 0, 0, 0, 0, 0] + self.do1.value[22:]
            self.do1.setValue(False, 27)

        if value:
            self.do1.setValue(True, 22)
            self.do1.setValue(True, 20)
        else:
            self.do1.setValue(False, 22)
            self.do1.setValue(False, 20)

    @QtCore.pyqtSlot(bool)
    def connect_pe(self, value=True):
        self.do2.setValue(value, 4)
        self.do2.setValue(value, 5)
        self.do2.setValue(value, 15)

    @QtCore.pyqtSlot(bool)
    def connect_gen(self, value=True):
        self.do2.value[9:15] = [value] * 6
        self.do2.setValue(value, 14)

    @QtCore.pyqtSlot(bool)
    def connect_dp(self, value=True):
        self.do2.setValue(value, 15)

    @QtCore.pyqtSlot()
    def on_pa3_update(self):
        self.pidc.setVin(self.pa3.value)

    @QtCore.pyqtSlot()
    def on_freq_update(self):
        self.pida.setVin(self.freq.value[0])

    @QtCore.pyqtSlot()
    def on_ao_change(self):
        self.pida.setVout(self.ao.value[2])
        self.pidc.setVout(self.ao.value[2])

    @QtCore.pyqtSlot()
    def on_freq_change(self):
        v = self.freq.value[0]
        if v != self.br2:
            self.br2 = v
            self.br2_changed.emit(v)
        v = self.freq.value[2]
        if v != self.br3:
            self.br3 = v
            self.br3_changed.emit(v)
        v = self.freq.value[7]
        if v != self.dp:
            self.dp = v
            self.dp_changed.emit(v)

    @QtCore.pyqtSlot()
    def on_ai_change(self):
        v = self.ai.value[1]
        if self.pressure != v:
            self.pressure = v
            self.pressure_change.emit(v)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QWidget()
    win.show()
    win.s = Server()
    win.s.start()

    app.exec_()
