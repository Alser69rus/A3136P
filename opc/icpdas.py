from PyQt5 import QtCore
import modbus_tk.defines as cst
import opc.bitwise as bitwise
from opc.monad import Maybe


class M7084(QtCore.QObject):
    """частотомер icp das M7084"""

    updated = QtCore.pyqtSignal()
    warning = QtCore.pyqtSignal(str)
    changed = QtCore.pyqtSignal()
    active_change = QtCore.pyqtSignal(bool)
    enabled = QtCore.pyqtSignal()
    cleared = QtCore.pyqtSignal()

    def __init__(self, port=None, dev=1, name='Частотомер', parent=None):
        super().__init__(parent)
        self.name = name
        self.port = port
        self.dev = dev
        self.value = [0] * 8
        self.k = [1] * 8
        self.off = [0] * 8
        self.eps = [1] * 8
        self.error = None
        self.active = False
        self._clear_cmd = False
        self._clear_ch = 0
        self._enable_cmd = False
        self._enable_ch = 0
        self._enable_value = True

    def _read_data(self, port):
        v = port.execute(self.dev, cst.READ_INPUT_REGISTERS, 0, 16)
        self.thread().msleep(2)
        return v

    def _unpack_data(self, data):
        value = [0] * 8
        for i in range(8):
            value[i] = data[i * 2] + 65536 * data[i * 2 + 1]
            value[i] = bitwise.to_signed32(value[i])
        return value

    def _clear(self, port, n):
        self.thread().msleep(5)
        v = port.execute(self.dev, cst.WRITE_SINGLE_COIL, 512 + n, output_value=1)
        self.thread().msleep(100)
        return v

    def _clear_done(self, data, n):
        data = list(data)
        if data[n * 2] == 0 and data[n * 2 + 1] == 0:
            self._clear_cmd = False
            self.cleared.emit()
            self.changed.emit()
        return data

    def _enable(self, data, n, value):
        data = bitwise.override(data, n, value)
        v = self.port.execute(self.dev, cst.WRITE_SINGLE_REGISTER, 489, output_value=data)
        self.thread().msleep(100)
        return v

    def _read_enable(self, port):
        v=port.execute(self.dev, cst.READ_INPUT_REGISTERS, 489, 1)
        self.thread().msleep(2)
        return v

    def _enable_done(self, data):
        self._enable_cmd = False
        self.enabled.emit()
        return data

    def _emit_updated(self, data):
        value = [data[i] * self.k[i] + self.off[i] for i in range(8)]
        if any([abs(value[i] - self.value[i]) > self.eps[i] for i in range(8)]):
            self.value = value
            self.changed.emit()
        self.updated.emit()
        return data

    def _emit_warning(self, data, error):
        self.error = error
        self.warning.emit('{} warning: {}'.format(self.name, self.error))
        self.thread().msleep(20)
        return data

    def update(self):
        if self._clear_cmd:
            Maybe(self.port)(self._clear, self._clear_ch).ret(self.port)(self._read_data)(self._clear_done,
                                                                                          self._clear_ch)
        if self._enable_cmd:
            Maybe(self.port)(self._read_enable)(self._enable, self._enable_ch, self._enable_value)(self._enable_done)
        if self.active:
            Maybe(self.port)(self._read_data)(self._unpack_data)(self._emit_updated).or_else(self._emit_warning)

    @QtCore.pyqtSlot(bool)
    def setActive(self, value=True):
        if self.active != value:
            self.active = value
            self.active_change.emit(value)

    @QtCore.pyqtSlot(int, bool)
    def setEnable(self, n, value):
        self._enable_ch = n
        self._enable_value = value
        self._enable_cmd = True

    @QtCore.pyqtSlot(int)
    def setClear(self, n):
        self._clear_ch = n
        self._clear_cmd = True
