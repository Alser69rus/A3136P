from PyQt5 import QtCore

import modbus_tk.defines as cst

from opc.monad import Maybe
import opc.bitwise as bitwise


class OwenModule(QtCore.QObject):
    updated = QtCore.pyqtSignal()
    warning = QtCore.pyqtSignal(str)
    changed = QtCore.pyqtSignal()
    active_change = QtCore.pyqtSignal(bool)

    def __init__(self, port=None, dev=None, name=None, parent=None):
        super().__init__(parent)
        self.value = None
        self.error = None
        self.port = port
        self.dev = dev
        self.active = False
        self.name = name

    def _read_data(self, data):
        pass

    def _unpack_data(self, pack):
        pass

    def _pack_data(self, data):
        pass

    def _write_data(self, pack):
        pass

    def _emit_warning(self, data, error):
        self.error = error
        self.warning.emit('{} warning: {}'.format(self.name, self.error))
        return data

    @QtCore.pyqtSlot(bool)
    def setActive(self, value=True):
        if self.active != value:
            self.active = value
            self.active_change.emit(value)


class OwenInputModule(OwenModule):
    def __init__(self, port=None, dev=None, name=None, parent=None):
        super().__init__(port=port, dev=dev, name=name, parent=parent)

    def update(self):
        if self.active:
            Maybe(self.port)(self._read_data)(self._unpack_data)(self._emit_updated).or_else(self._emit_warning)

    def _emit_updated(self, data):
        if data != self.value:
            self.value = data
            self.changed.emit()
        self.updated.emit()
        return data


class OwenOutputModule(OwenModule):
    def __init__(self, port=None, dev=None, name=None, parent=None):
        super().__init__(port=port, dev=dev, name=name, parent=parent)

    def update(self):
        if self.active:
            Maybe(self.value)(self._pack_data)(self._write_data)(self._read_data)(self._check_data)(self._emit_updated)(
                self._write_done).or_else(
                self._emit_warning)

    def _emit_updated(self, data):
        if self.active:
            self.changed.emit()
        self.updated.emit()
        return data

    def _write_done(self, data):
        self.setActive(False)
        return data

    def setValue(self, value, n=-1):
        if n >= 0:
            self.value[n] = value
        else:
            self.value = value
        self.setActive()


class DI16(OwenInputModule):
    def __init__(self, port=None, dev=None, name='DI', parent=None):
        super().__init__(port=port, dev=dev, name=name, parent=parent)
        self.value = [0] * 16

    def _read_data(self, port):
        return port.execute(self.dev, cst.READ_INPUT_REGISTERS, 51, 1)

    def _unpack_data(self, pack):
        value = []
        for i in range(16):
            value.append(bitwise.get(pack[0], i))
        return value


class AI8(OwenInputModule):
    def __init__(self, port=None, dev=None, name='AI', parent=None):
        super().__init__(port=port, dev=dev, name=name, parent=parent)
        self.value = [0] * 8
        self.k = [1] * 8
        self.off = [0] * 8
        self.eps = [1] * 8

    def _read_data(self, port):
        return port.execute(self.dev, cst.READ_INPUT_REGISTERS, 256, 8)

    def _unpack_data(self, data):
        values = [i if i < 32768 else 655536 - i for i in data]
        values = [values[i] * self.k[i] + self.off[i] for i in range(8)]
        values = [i if i != 32768 else None for i in values]
        return values

    def _emit_updated(self, values):
        if any([abs(self.value[i] - values[i]) > self.eps[i] for i in range(8)]):
            self.value = values
            self.changed.emit()
        self.updated.emit()
        return values


class DO32(OwenOutputModule):

    def __init__(self, port=None, dev=None, name='DO', parent=None):
        super().__init__(port=port, dev=dev, name=name, parent=parent)
        self.value = [0] * 32

    def _pack_data(self, data):
        pack = [0, 0]
        for i in range(16):
            pack[0] = bitwise.override(pack[0], i, data[i + 16])
            pack[1] = bitwise.override(pack[1], i, data[i])
        return pack

    def _write_data(self, pack):
        self.thread().msleep(2)
        return self.port.execute(self.dev, cst.WRITE_MULTIPLE_REGISTERS, 97, output_value=pack)

    def _read_data(self, data):
        self.thread().msleep(2)
        return self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 97, 2)

    def _check_data(self, data):
        v = [0] * 32
        for i in range(16):
            v[i] = bitwise.get(data[1], i)
            v[i + 16] = bitwise.get(data[0], i)
        if v == self.value:
            return v
        return None


class AO8I(OwenOutputModule):

    def __init__(self, port=None, dev=None, name='AO', parent=None):
        super().__init__(port=port, dev=dev, name=name, parent=parent)
        self.value = [0] * 8

    def _pack_data(self, data):
        return [int(i) for i in data]

    def _write_data(self, data):
        self.thread().msleep(2)
        return self.port.execute(self.dev, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=data)

    def _read_data(self, data):
        self.thread().msleep(2)
        v = self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 0, 8)
        return v

    def _check_data(self, data):
        if list(data) == self.value:
            return data
        return None
