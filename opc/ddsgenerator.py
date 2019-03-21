import time
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu


class Generator:
    '''самодельный трехканальный генератор'''
    def __init__(self, port=None, dev=100, timeout=0.5, delay=0.1, verbose=False):
        self.port = port
        self.dev = dev
        self.timeout = timeout
        self._delay = delay
        self.verbose = verbose
        if port:
            self.port.set_timeout(timeout)
            self.port.set_verbose(verbose)
        self.time = time.time()
        self.value = [0, 0, 0]
        self._resp = []

    def _read_data(self):
        if self.port:
            return self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 0, 6)
        else:
            return [0] * 6

    @staticmethod
    def _unpack_data(data):
        value = [0] * 3
        for i in range(3):
            value[i] = data[i * 2] * 65536 + data[i * 2 + 1]
        return value

    def _write_data(self, data):
        if self.port:
            self.port.execute(self.dev, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=data)

    @staticmethod
    def _pack_data(data):
        value = [0] * 6
        for i in range(3):
            value[i * 2] = data[i] // 65536
            value[i * 2 + 1] = data[i] % 65536
        return value

    def update(self):
        if not self.port: return True
        try:
            data = self._pack_data(self.value)
            self._write_data(data)
            self.quality = True
            # time.sleep(self._delay)
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

    def write(self):
        while not self.update(): pass
        return self.read()

    def update_status(self):
        if not self.port: return True
        try:
            data = self._read_data()
            self.value = self._unpack_data(data)
            self.quality = True
            # time.sleep(self._delay)
        except Exception as exc:
            self.quality = False
            if self.quality == 0: raise exc
            time.sleep(self._delay)
            return False
        # self._update_time()
        return True

    @property
    def quality(self):
        return 10 - self._resp.count(False)

    @quality.setter
    def quality(self, value):
        if len(self._resp) >= 10:
            self._resp = self._resp[1:]
        self._resp.append(value)

    def _update_time(self):
        self.time = time.time()
