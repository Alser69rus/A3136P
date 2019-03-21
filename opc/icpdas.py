import time
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

try:
    from . import bitwise
except Exception as exc:
    import bitwise


class M7084onlyE(M7084):
    """быстроопрашиваемый частотомер - только первый и третий каналы (2 энкодера)"""


class M7084:
    """частотомер icp das M7084"""

    def __init__(self, port=None, dev=1, timeout=0.3, delay=0.005, verbose=False):
        self.port = port
        self.dev = dev
        self._delay = delay
        self._timeout = timeout
        self._verbose = verbose
        if self.port:
            self.port.set_timeout(timeout)
            self.port.set_verbose(verbose)

        self.time = time.time()
        self.value = [0] * 8
        self._resp = []
        self.chanel_03 = True
        self.chanel_47 = True

    def _read_data(self):
        if self.port:
            if self.chanel_03 and self.chanel_47:
                return self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 0, 16)
            elif self.chanel_03:
                a = self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 0, 2)
                b = self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 4, 2)
                c = [0] * 16
                c[0] = c[2] = a[0]
                c[1] = c[3] = a[1]
                c[4] = c[6] = b[0]
                c[5] = c[7] = b[1]
                return c
            elif self.chanel_47:
                a = self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 8, 8)
                c = [0] * 8
                return c + a
            return [0] * 16
        else:
            return [0] * 16

    def _unpack_data(self, data):
        value = [0] * 8
        for i in range(8):
            value[i] = data[i * 2] + 65536 * data[i * 2 + 1]
            value[i] = bitwise.to_signed32(value[i])
        return value

    def _update_time(self):
        self.time = time.time()

    def clear(self, n):
        """сервисная функция очистки регистров счетчиков"""
        if not self.port:
            return
        while True:
            try:
                self.port.execute(self.dev, cst.WRITE_SINGLE_COIL, 512 + n, output_value=1)
                self.quality = True
                time.sleep(self._delay)
                return
            except Exception as exc:
                self.quality = False
                if self.quality == 0: raise exc
                time.sleep(self._delay)

    def enable(self, n, value):
        """сервисная функция включения/выключения счетчиков"""
        if not self.port: return
        while True:
            try:
                data = self.port.execute(self.dev, cst.READ_INPUT_REGISTERS, 489, 1)
                time.sleep(self._delay)
                data = data[0]
                data = bitwise.override(data, n, value)
                self.port.execute(self.dev, cst.WRITE_SINGLE_REGISTER, 489, output_value=data)
                time.sleep(self._delay)
                self.quality = True
                return
            except Exception as exc:
                self.quality = False
                if self.quality == 0: raise exc
                time.sleep(self._delay)

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
