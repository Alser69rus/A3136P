import time
from abc import ABC, abstractmethod
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

try:
    from . import bitwise
except Exception as exc:
    import bitwise


class OwenIOModule(ABC):
    def __init__(self, port=None, dev=1, timeout=0.3, delay=0.005, verbose=False):
        self.port = port
        self.dev = dev
        self._timeout = timeout
        self._verbose = verbose
        self._delay = delay
        if self.port:
            self.port.set_timeout(timeout)
            self.port.set_verbose(verbose)

        self.time = time.time()
        self.value = []
        self._resp = []

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def update_status(self):
        pass

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


class OwenInputModule(OwenIOModule):

    @abstractmethod
    def _read_data(self):
        pass

    @abstractmethod
    def _unpack_data(self, data):
        pass

    def update(self):
        self.update_status()

    def update_status(self):
        if not self.port: return True
        try:
            data = self._read_data()
            self.value = self._unpack_data(data)
            self.quality = True
        except Exception as exc:
            self.quality = False
            if self.quality == 0: raise exc
            time.sleep(self._delay)
            return False
        # self._update_time()
        # time.sleep(self._delay)
        return True

    def read(self):
        while not self.update_status(): pass
        return self.value


class OwenOutputModule(OwenIOModule):
    @abstractmethod
    def _read_data(self):
        pass

    @abstractmethod
    def _write_data(self, data):
        pass

    @abstractmethod
    def _unpack_data(self, data):
        pass

    @abstractmethod
    def _pack_data(self, data):
        pass

    def update(self):
        if not self.port: return True
        try:
            data = self._pack_data(self.value)
            self._write_data(data)
            self.quality = True
        except Exception as exc:
            self.quality = False
            if self.quality == 0: raise exc
            time.sleep(self._delay)
            return False
        # self._update_time()
        # time.sleep(self._delay)
        return True

    def update_status(self):
        if not self.port: return True
        try:
            data = self._read_data()
            self.value = self._unpack_data(data)
            self.quality = True
        except Exception as exc:
            self.quality = False
            if self.quality == 0: raise exc
            time.sleep(self._delay)
            return False
        # self._update_time()
        # time.sleep(self._delay)
        return True

    def read(self):
        while not self.update_status(): pass
        return self.value

    def write(self):
        while not self.update(): pass
        return True


class DI16(OwenInputModule):
    def _read_data(self):
        if self.port:
            return self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 51, 1)
        else:
            return [0]

    def _unpack_data(self, data):
        value = []
        for i in range(16):
            value.append(bitwise.get(data[0], i))
        return value


class AI8(OwenInputModule):
    def _read_data(self):
        if self.port:
            return self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 256, 8)
        else:
            return [0] * 8

    def _unpack_data(self, data):
        return data


class DO32(OwenOutputModule):
    def __init__(self, port=None, dev=1, timeout=0.3, delay=0.005, verbose=False):
        super().__init__(port, dev, timeout, delay, verbose)
        self.value = [0] * 32

    def _read_data(self):
        if self.port:
            return self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 97, 2)
        else:
            return [0] * 2

    def _unpack_data(self, data):
        value = []
        value2 = []

        for i in range(16):
            value.append(bitwise.get(data[0], i))
            value2.append(bitwise.get(data[1], i))
        value.extend(value2)
        return value

    def _pack_data(self, data):
        pack = [0, 0]
        if not data: return pack

        for i in range(16):
            pack[0] = bitwise.override(pack[0], i, data[i + 16])
            pack[1] = bitwise.override(pack[1], i, data[i])
        return pack

    def _write_data(self, data):
        if self.port:
            self.port.execute(self.dev, cst.WRITE_MULTIPLE_REGISTERS, 97, output_value=data)


class AO8I(OwenOutputModule):
    def __init__(self, port=None, dev=1, timeout=0.3, delay=0.005, verbose=False):
        super().__init__(port, dev, timeout, delay, verbose)
        self.value = [0] * 8

    def _read_data(self):
        if self.port:
            return self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 0, 8)
        else:
            return [0] * 8

    def _unpack_data(self, data):
        return list(data)

    def _pack_data(self, data):
        return [int(i) for i in data]

    def _write_data(self, data):
        if self.port:
            self.port.execute(self.dev, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=data)
