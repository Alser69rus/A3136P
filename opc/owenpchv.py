import time
import modbus_tk.defines as cst
from PyQt5 import QtCore, QtWidgets

try:
    from . import bitwise
except Exception:
    import bitwise


def waitsuccess(func):
    def wrapper(self, *args):
        try:
            func(self, *args)
            self.quality = True
            # time.sleep(self._delay)
            return True
        except Exception as exc:
            self.quality = False
            if self.quality == 0: raise exc
            time.sleep(self._delay)
            return False

    return wrapper


class Pchv(QtCore.QObject):
    speed_updated = QtCore.pyqtSignal(float)
    on_task_signal = QtCore.pyqtSignal()
    speed_task_changed = QtCore.pyqtSignal(float)

    def __init__(self, port=None, dev=1, max_speed=1380, feedback_k=1.33333333333, timeout=0.3,
                 delay=0.005, verbose=False, parent=None):
        super().__init__(parent)
        self.port = port
        self.dev = dev
        self.max_speed = max_speed
        self.feedback_k = feedback_k
        self._delay = delay
        self._timeout = timeout
        self._verbose = verbose
        if self.port:
            self.port.set_timeout(timeout)
            self.port.set_verbose(verbose)

        self.time = time.time()
        self._resp = []

        self.ctw = 0  # командное слово
        self.ref = 0  # задание
        self.stw = 0  # состояние
        self.mav = 0  # текущее значение

        self.feedback_freq = 0
        self.only_speed = False

    def _update_time(self):
        self.time = time.time()

    @property
    def quality(self):
        return 10 - self._resp.count(False)

    @quality.setter
    def quality(self, value):
        if len(self._resp) >= 10:
            self._resp = self._resp[1:]
        self._resp.append(value)

    @property
    def preset_task(self):
        return self.ctw & 3

    @preset_task.setter
    def preset_task(self, value):
        self.ctw = self.ctw & (~3)
        self.ctw = self.ctw | (value & 3)

    @property
    def dc_breaking(self):
        return bitwise.get(self.ctw, 2)

    @dc_breaking.setter
    def dc_breaking(self, value):
        self.ctw = bitwise.override(self.ctw, 2, value)

    @property
    def coast_breaking(self):
        return bitwise.get(self.ctw, 3)

    @coast_breaking.setter
    def coast_breaking(self, value):
        self.ctw = bitwise.override(self.ctw, 3, value)

    @property
    def fast_breaking(self):
        return bitwise.get(self.ctw, 4)

    @fast_breaking.setter
    def fast_breaking(self, value):
        self.ctw = bitwise.override(self.ctw, 4, value)

    @property
    def frequency_fixing(self):
        return bitwise.get(self.ctw, 5)

    @frequency_fixing.setter
    def frequency_fixing(self, value):
        self.ctw = bitwise.override(self.ctw, 5, value)

    @property
    def starting(self):
        return bitwise.get(self.ctw, 6)

    @starting.setter
    def starting(self, value):
        self.ctw = bitwise.override(self.ctw, 6, value)

    @property
    def resetting(self):
        return bitwise.get(self.ctw, 7)

    @resetting.setter
    def resetting(self, value):
        self.ctw = bitwise.override(self.ctw, 7, value)

    @property
    def working_on_task(self):
        return bitwise.get(self.ctw, 8)

    @working_on_task.setter
    def working_on_task(self, value):
        self.ctw = bitwise.override(self.ctw, 8, value)

    @property
    def acc_curve(self):
        return bitwise.get(self.ctw, 9)

    @acc_curve.setter
    def acc_curve(self, value):
        self.ctw = bitwise.override(self.ctw, 9, value)

    @property
    def valid(self):
        return bitwise.get(self.ctw, 10)

    @valid.setter
    def valid(self, value):
        self.ctw = bitwise.override(self.ctw, 10, value)

    @property
    def relay(self):
        return bitwise.get(self.ctw, 11)

    @relay.setter
    def relay(self, value):
        self.ctw = bitwise.override(self.ctw, 11, value)

    @property
    def active_set(self):
        return bitwise.get(self.ctw, 14)

    @active_set.setter
    def active_set(self, value):
        self.ctw = bitwise.override(self.ctw, 14, value)

    @property
    def reversing(self):
        return bitwise.get(self.ctw, 15)

    @reversing.setter
    def reversing(self, value):
        self.ctw = bitwise.override(self.ctw, 15, value)

    @property
    def control_ready(self):
        return bitwise.get(self.stw, 0)

    @property
    def drive_ready(self):
        return bitwise.get(self.stw, 1)

    @property
    def breaking_off(self):
        return bitwise.get(self.stw, 2)

    @property
    def alarm(self):
        return bitwise.get(self.stw, 3)

    @property
    def lpo_err(self):
        return bitwise.get(self.stw, 4)

    @property
    def critical_err(self):
        return bitwise.get(self.stw, 6)

    @property
    def warning(self):
        return bitwise.get(self.stw, 7)

    @property
    def on_task(self):
        return bitwise.get(self.stw, 8)

    @property
    def auto(self):
        return bitwise.get(self.stw, 9)

    @property
    def on_range(self):
        return bitwise.get(self.stw, 10)

    @property
    def working(self):
        return bitwise.get(self.stw, 11)

    @property
    def drive_check_err(self):
        return bitwise.get(self.stw, 12)

    @property
    def voltage_warning(self):
        return bitwise.get(self.stw, 13)

    @property
    def current_warning(self):
        return bitwise.get(self.stw, 14)

    @property
    def overheat(self):
        return bitwise.get(self.stw, 15)

    @property
    def speed_task(self):
        return self.max_speed * self.ref / 16384

    @property
    def speed(self):
        return self.feedback_speed

    @speed.setter
    def speed(self, value):
        self.ref = int(value * 16384 / self.max_speed)
        if self.ref < 0:
            self.ref = 0
        if self.ref > 16383:
            self.ref = 16383
        self.valid = True
        self.speed_task_changed.emit(value)

    @property
    def current_speed(self):
        return self.mav * self.max_speed / 16384

    @property
    def feedback_speed(self):
        return self.feedback_freq * self.feedback_k

    def start(self, reverse=False):
        self.dc_breaking = True
        self.coast_breaking = True
        self.fast_breaking = True
        self.frequency_fixing = True
        self.starting = True
        self.resetting = False
        self.working_on_task = False
        self.valid = True
        self.reversing = reverse
        while not self.update(): pass

    def stop(self, fast=False, dc=False, coast=False):
        self.dc_breaking = not dc
        self.fast_breaking = not fast
        self.coast_breaking = not coast
        self.starting = False
        self.frequency_fixing = True
        self.working_on_task = False
        self.resetting = False
        self.valid = True
        while not self.update(): pass

    def reset(self):
        self.resetting = True
        self.valid = True
        while not self.update(): pass

    def wait_ready(self, timeout=30):
        t = time.time()
        if not self.port: return False
        while True:
            try:
                self.stw = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 50199, 1)[0]
                return True
            except Exception:
                time.sleep(0.5)
            if (time.time() - t) > timeout:
                raise Exception('Таймаут запуска ПЧВ')

    def update(self):
        if not self.port: return True
        while not self._write_ref(self.ref): pass
        while not self._write_ctw(self.ctw): pass
        return True

    def write(self):
        self.update()
        return self.update_status()

    def update_status(self):
        if not self.port: return True
        if not self.only_speed:
            while not self._read_ref(): pass
            while not self._read_ctw(): pass
            while not self._read_stw(): pass
            while not self._read_mav(): pass
        while not self._read_feedback(): pass

        self.speed_updated.emit(self.speed)
        if self.on_task: self.on_task_signal.emit()
        return True

    def read(self):
        return self.update_status()

    @waitsuccess
    def _read_ref(self):
        if self.port:
            self.ref = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 50009, 1)[0]

    @waitsuccess
    def _write_ref(self, value):
        if self.port:
            self.port.execute(self.dev, cst.WRITE_SINGLE_REGISTER, 50009, output_value=value)

    @waitsuccess
    def _read_ctw(self):
        if self.port:
            self.ctw = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 49999, 1)[0]

    @waitsuccess
    def _write_ctw(self, value):
        if self.port:
            self.port.execute(self.dev, cst.WRITE_SINGLE_REGISTER, 49999, output_value=value)

    @waitsuccess
    def _read_stw(self):
        if self.port:
            self.stw = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 50199, 1)[0]

    @waitsuccess
    def _read_mav(self):
        if self.port:
            self.mav = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 50209, 1)[0]

    @waitsuccess
    def _read_feedback(self):
        if self.port:
            self.feedback_freq = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 16679, 1)[0]
