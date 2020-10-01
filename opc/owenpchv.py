import modbus_tk.defines as cst
from PyQt5 import QtCore
import opc.bitwise as bitwise
from opc.monad import Maybe
from pymodbus.client.sync import ModbusSerialClient as Client


class Pchv(QtCore.QObject):
    task_changed = QtCore.pyqtSignal(float)
    speed_changed = QtCore.pyqtSignal(float)
    warning = QtCore.pyqtSignal(str)
    updated = QtCore.pyqtSignal()
    alarmed = QtCore.pyqtSignal(str)
    get_ready = QtCore.pyqtSignal(bool)
    break_on = QtCore.pyqtSignal(bool)
    speed_reached = QtCore.pyqtSignal(bool)
    active_change = QtCore.pyqtSignal(bool)

    def __init__(self, port=None, dev=1, max_speed=1380, fb_k=1.33333333333, fb_off=0, eps=2, name='ПЧВ', parent=None):
        super().__init__(parent)
        self.name = name
        self.port: Client = port
        self.dev = dev
        self.max_speed = max_speed
        self.fb_k = fb_k
        self.fb_off = fb_off
        self.eps = eps

        self.ctw = 0  # командное слово
        self.ref = 0  # задание
        self.stw = 0  # состояние
        self.mav = 0  # текущее значение
        self.fb = 0  # значение частоты от датчика обратной связи

        self.active = False
        self.send_cmd = False

    @property
    def ready(self):
        return self.stw & 3

    @property
    def breaking(self):
        return not bitwise.get(self.stw, 2)

    @property
    def on_task(self):
        return bitwise.get(self.stw, 8)

    @property
    def working(self):
        return bitwise.get(self.stw, 11)

    @property
    def task(self):
        return self.max_speed * self.ref / 16384

    @property
    def speed(self):
        speed = self.fb * self.fb_k + self.fb_off
        return speed if speed > 0 else 0

    @speed.setter
    def speed(self, speed):
        self.set_speed(speed)

    @property
    def current_speed(self):
        return self.mav * self.max_speed / 16384

    @QtCore.pyqtSlot()
    def start(self):
        self.ctw = 0b0000010001111100
        self.send_cmd = True

    @QtCore.pyqtSlot()
    def stop(self):
        self.ctw = 0b0000010000101100
        self.send_cmd = True

    @QtCore.pyqtSlot(float)
    def set_speed(self, speed):
        if speed == 0:
            self.ref = 0
            self.stop()
        else:
            self.stw = bitwise.override(self.stw, 8, 0)
            ref = int(speed * 16384 / self.max_speed)
            if ref < 0:
                ref = 0
            if ref > 16383:
                ref = 16383
            self.ref = ref
            self.start()

    @QtCore.pyqtSlot(bool)
    def setActive(self, value=True):
        if self.active != value:
            self.active = value
            self.active_change.emit(value)

    def emit_warning(self, txt, error):
        self.warning.emit(f'{self.name} {txt} warning: {error}')
        print(f'{self.name} {txt} warning: {error}')

    def emit_stw_signals(self):
        stw = self.stw
        alarm = stw & 0b1111000011011000
        if alarm:
            msg = self.err_msg(stw)
            if not (msg.count('лпо') or msg.count('напряжение')):
                self.alarmed.emit(msg)
            else:
                self.warning.emit(msg)

        ready = stw & 3
        if self.ready != ready:
            self.get_ready.emit(ready)

        br = not bitwise.get(stw, 2)
        if self.breaking != br:
            self.break_on.emit(br)

        # speed_reached = bitwise.get(stw, 8)
        if self.task - 5 <= self.speed <= self.task + 5:
            self.speed_reached.emit(True)

        return stw

    def speed_change(self):
        fb = self.fb
        speed = fb * self.fb_k + self.fb_off
        if speed < 0: speed = 0
        if abs(self.speed - speed) > self.eps:
            self.speed_changed.emit(speed)
        return fb

    def err_msg(self, stw):
        msg = ''
        if bitwise.get(stw, 3): msg += 'тревога '
        if bitwise.get(stw, 4): msg += 'лпо '
        if bitwise.get(stw, 6): msg += 'лпо '
        if bitwise.get(stw, 7): msg += 'внимание '
        if bitwise.get(stw, 12): msg += 'привод '
        if bitwise.get(stw, 13): msg += 'напряжение '
        if bitwise.get(stw, 14): msg += 'ток '
        if bitwise.get(stw, 15): msg += 'перегрев '
        return msg

    def update(self):
        if self.send_cmd:
            req = self.write_ref()
            if req.isError():
                self.emit_warning('write ref', req)
                return False
            req = self.write_ctw()
            if req.isError():
                self.emit_warning('write ctw', req)
                return False
            self.send_cmd = False
            self.task_changed.emit(self.task)

        if self.active:
            req = self.read_stw()
            if req.isError():
                self.emit_warning('read stw', req)
                return False
            self.stw = req.registers[0]
            self.emit_stw_signals()

            req = self.read_mav()
            if req.isError():
                self.emit_warning('read mav', req)
                return False
            self.mav = req.registers[0]

            req = self.read_fb()
            if req.isError():
                self.emit_warning('read fb', req)
                return False
            self.fb = req.registers[0]
            self.speed_change()

            self.updated.emit()
            return True

    def write_ref(self):
        return self.port.write_register(50009, self.ref, unit=self.dev)

    def write_ctw(self):
        return self.port.write_register(49999, self.ctw, unit=self.dev)

    def read_stw(self):
        return self.port.read_holding_registers(50199, 1, unit=self.dev)

    def read_mav(self):
        return self.port.read_holding_registers(50209, 1, unit=self.dev)

    def read_fb(self):
        return self.port.read_holding_registers(16679, 1, unit=self.dev)
