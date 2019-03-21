import time
import modbus_tk.defines as cst
from PyQt5 import QtCore


class Communicate(QtCore.QObject):
    value_changed = QtCore.pyqtSignal(float)


class ElMultimeter:
    '''амперметры и вольтметры Электроприбор'''

    def __init__(self, port=None, dev=1, k=1, offset=0, timeout=0.3, delay=0.005, verbose=False):
        self.c = Communicate()
        self.port = port
        self.dev = dev
        self._timeout = timeout
        self._delay = delay
        self._verbose = verbose
        if self.port:
            self.port.set_timeout(timeout)
            self.port.set_verbose(verbose)

        self.time = time.time()
        self.value = 0
        self._resp = []
        self.k = k
        self.off = offset

    def _read_data(self):
        if self.port:
            return self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 4, 1)
        else:
            return [0]

    def _unpack_data(self, data):
        if data[0] == 32768:
            return None
        if data[0] > 32768:
            return data[0] - 65536
        return data[0] * self.k - self.off

    def _update_time(self):
        self.time = time.time()

    def update(self):
        self.update_status()

    def update_status(self):
        if not self.port:
            return True
        try:
            data = self._read_data()
            self.value = self._unpack_data(data)
            self.quality = True
            # time.sleep(self._delay)
            self.c.value_changed.emit(self.value)
        except Exception as exc:
            self.quality = False
            if self.quality == 0: raise exc
            time.sleep(self._delay)
            return False
        # self._update_time()
        return True

    def read(self):
        while not self.update_status(): pass
        return self.value

    @property
    def quality(self):
        return 10 - self._resp.count(False)

    @quality.setter
    def quality(self, value):
        if len(self._resp) >= 10:
            self._resp = self._resp[1:]
        self._resp.append(value)
