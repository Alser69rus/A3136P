from PyQt5 import QtCore
import modbus_tk.defines as cst
from opc.monad import Maybe


class Generator(QtCore.QObject):
    updated = QtCore.pyqtSignal()
    warning = QtCore.pyqtSignal(str)
    changed = QtCore.pyqtSignal()
    active_change = QtCore.pyqtSignal(bool)
    '''самодельный трехканальный генератор'''

    def __init__(self, port=None, dev=100, name='DDS Gen', parent=None):
        super().__init__(parent)
        self.name = name
        self.port = port
        self.dev = dev
        self.value = [0] * 3
        self.error = None
        self.active = False

    def _read_data(self, port):
        return self.port.execute(self.dev, cst.READ_HOLDING_REGISTERS, 0, 6)

    def _unpack_data(self, data):
        value = [0] * 3
        for i in range(3):
            value[i] = data[i * 2] * 65536 + data[i * 2 + 1]
        return value

    def _pack_data(self, value):
        data = [0] * 6
        for i in range(3):
            data[i * 2] = value[i] // 65536
            data[i * 2 + 1] = value[i] % 65536
        return data

    def _write_data(self, data):
        return self.port.execute(self.dev, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=data)


    def _emit_updated(self, data):
        if self.active:
            self.changed.emit()
        self.updated.emit()
        return data

    def _write_done(self, data):
        self.setActive(False)
        return data

    def _emit_warning(self, data, error):
        self.error = error
        self.warning.emit('{} warning: {}'.format(self.name, self.error))
        return data

    @QtCore.pyqtSlot(bool)
    def setActive(self, value=True):
        if self.active != value:
            self.active = value
            self.active_change.emit(value)

    def update(self):
        if self.active:
            Maybe(self.value)(self._pack_data)(self._write_data)(self._emit_updated)(self._write_done).or_else(
                self._emit_warning)
