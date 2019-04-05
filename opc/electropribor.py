import time
import modbus_tk.defines as cst
from PyQt5 import QtCore

from opc.monad import Maybe


class ElMultimeter(QtCore.QObject):
    changed = QtCore.pyqtSignal(float)
    updated = QtCore.pyqtSignal()
    warning = QtCore.pyqtSignal(str)
    active_change = QtCore.pyqtSignal(bool)
    '''амперметры и вольтметры Электроприбор'''

    def __init__(self, port=None, dev=1, k=1, offset=0, eps=1, name='PX', parent=None):
        super().__init__(parent)
        self.name = name
        self.port = port
        self.dev = dev
        self.value = 0
        self.error = None
        self.active = False
        self.k = k
        self.off = offset
        self.eps = eps

    def _read_data(self, port):
        return port.execute(self.dev, cst.READ_INPUT_REGISTERS, 4, 1)

    def _unpack_data(self, data):
        value = data[0]
        if value == 32768:
            raise Exception('{}. Выход за пределы диапазона'.format(self.name))

        if value > 32768:
            value = 65536 - value
        value = value * self.k - self.off
        return value

    def _emit_warning(self, data, error):
        self.error = error
        self.warning.emit('{} warning: {}'.format(self.name, self.error))
        return data

    def _emit_updated(self, value):
        if abs(value - self.value) > self.eps:
            self.value = value
            self.changed.emit(value)
        self.updated.emit()
        return value

    def update(self):
        if self.active:
            Maybe(self.port)(self._read_data)(self._unpack_data)(self._emit_updated).or_else(self._emit_warning)

    @QtCore.pyqtSlot(bool)
    def setActive(self, value=True):
        self.active = value
        self.active_change.emit(value)
