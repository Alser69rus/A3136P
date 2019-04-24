import modbus_tk.defines as cst
from PyQt5 import QtCore
import opc.bitwise as bitwise
from opc.monad import Maybe


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
        self.port = port
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

    def _cmd_send_done(self, data):
        self.send_cmd = False
        self.task_changed.emit(self.task)
        return data

    def _emit_warning(self, data, error):
        self.error = error
        self.warning.emit('{} warning: {}'.format(self.name, self.error))
        return data

    def _emit_stw_signals(self, stw):
        alarm = stw & 0b1111000011011000
        if alarm:
            msg = self.err_msg(stw)
            self.alarmed.emit(msg)

        ready = stw & 3
        if self.ready != ready:
            self.get_ready.emit(ready)

        br = not bitwise.get(stw, 2)
        if self.breaking != br:
            self.break_on.emit(br)

        speed_reached = bitwise.get(stw, 8)
        if speed_reached:
            self.speed_reached.emit(True)

        return stw

    def _upd_stw(self, stw):
        self.stw = stw
        return stw

    def _upd_fb(self, fb):
        self.fb = fb
        return fb

    def _speed_changed(self, fb):
        speed = fb * self.fb_k + self.fb_off
        if speed < 0: speed = 0
        if abs(self.speed - speed) > self.eps:
            self.speed_changed.emit(speed)
        return fb

    def _upd_mav(self, mav):
        self.mav = mav
        return mav

    def _delay(self, value, delay=2):
        self.thread().msleep(delay)
        return value

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
            Maybe(self.ref)(self._write_ref)(self._delay).ret(self.ctw)(self._write_ctw)(self._cmd_send_done)(
                self._delay).or_else(self._emit_warning)
        if self.active:
            Maybe(self.port)(self._read_stw)(self._emit_stw_signals)(self._upd_stw)(self._delay).or_else(
                self._emit_warning)
            Maybe(self.port)(self._read_fb)(self._speed_changed)(self._upd_fb)(self._delay).or_else(self._emit_warning)
            Maybe(self.port)(self._read_mav)(self._upd_mav).or_else(self._emit_warning)
            self.updated.emit()

    def _write_ref(self, value):
        self.port.execute(self.dev, cst.WRITE_SINGLE_REGISTER, 50009, output_value=value)
        return value

    def _write_ctw(self, value):
        self.port.execute(self.dev, cst.WRITE_SINGLE_REGISTER, 49999, output_value=value)
        return value

    def _read_stw(self, port):
        return port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 50199, 1)[0]

    def _read_mav(self, port):
        return port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 50209, 1)[0]

    def _read_fb(self, port):
        return port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 16679, 1)[0]
