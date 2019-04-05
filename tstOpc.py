from PyQt5 import QtCore, QtWidgets
import opc.opc2


class Main(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.warning = QtWidgets.QTextEdit()
        self.di = QtWidgets.QLabel()
        self.ai = QtWidgets.QLabel()
        self.do1 = QtWidgets.QLabel()
        self.do2 = QtWidgets.QLabel()
        self.ao = QtWidgets.QLabel()
        self.pv1 = QtWidgets.QLabel()
        self.pv2 = QtWidgets.QLabel()
        self.pa1 = QtWidgets.QLabel()
        self.pa2 = QtWidgets.QLabel()
        self.pa3 = QtWidgets.QLabel()
        self.gen = QtWidgets.QLabel()
        self.freq = QtWidgets.QLabel()
        self.pchv = QtWidgets.QWidget()
        self.hbox = QtWidgets.QHBoxLayout()
        self.pchv_start = QtWidgets.QPushButton('старт')
        self.pchv_stop = QtWidgets.QPushButton('стоп')
        self.pchv_speed = QtWidgets.QLabel('Скорость: 0000')
        self.pchv_set_task = QtWidgets.QPushButton('Задать скорость')
        self.pchv_task = QtWidgets.QLineEdit('500')
        self.pchv_ready = QtWidgets.QCheckBox('Ready')
        self.pchv_break = QtWidgets.QCheckBox('Break')
        self.pchv_on_task = QtWidgets.QCheckBox('on_task')
        self.pchv.setLayout(self.hbox)
        self.hbox.addWidget(self.pchv_start)
        self.hbox.addWidget(self.pchv_stop)
        self.hbox.addWidget(self.pchv_speed)
        self.hbox.addWidget(self.pchv_set_task)
        self.hbox.addWidget(self.pchv_task)
        self.hbox.addWidget(self.pchv_ready)
        self.hbox.addWidget(self.pchv_break)
        self.hbox.addWidget(self.pchv_on_task)

        self.setLayout(self.vbox)
        self.resize(1024, 700)
        self.vbox.addWidget(self.di)
        self.vbox.addWidget(self.ai)
        self.vbox.addWidget(self.do1)
        self.vbox.addWidget(self.do2)
        self.vbox.addWidget(self.ao)
        self.vbox.addWidget(self.pv1)
        self.vbox.addWidget(self.pv2)
        self.vbox.addWidget(self.pa1)
        self.vbox.addWidget(self.pa2)
        self.vbox.addWidget(self.pa3)
        self.vbox.addWidget(self.gen)
        self.vbox.addWidget(self.freq)
        self.vbox.addWidget(self.pchv)

        self.vbox.addWidget(self.warning)

        self.server = opc.opc2.Server()

        self.w1 = self.server.workers[0]
        self.w1.di.changed.connect(self.di_changed)
        self.w1.di.warning.connect(self.on_warning)
        self.w1.ai.changed.connect(self.ai_changed)
        self.w1.ai.warning.connect(self.on_warning)
        self.w1.ao.changed.connect(self.ao_changed)
        self.w1.ao.warning.connect(self.on_warning)
        self.w1.do1.changed.connect(self.do1_changed)
        self.w1.do1.warning.connect(self.on_warning)
        self.w1.do2.changed.connect(self.do2_changed)
        self.w1.do2.warning.connect(self.on_warning)

        self.w1.pv1.changed.connect(self.pv1_changed)
        self.w1.pv1.warning.connect(self.on_warning)
        self.w1.pv2.changed.connect(self.pv2_changed)
        self.w1.pv2.warning.connect(self.on_warning)
        self.w1.pa1.changed.connect(self.pa1_changed)
        self.w1.pa1.warning.connect(self.on_warning)
        self.w1.pa2.changed.connect(self.pa2_changed)
        self.w1.pa2.warning.connect(self.on_warning)
        self.w1.pa3.changed.connect(self.pa3_changed)
        self.w1.pa3.warning.connect(self.on_warning)

        self.w2 = self.server.workers[1]
        self.pchv_start.clicked.connect(self.w2.pchv.start)
        self.pchv_stop.clicked.connect(self.w2.pchv.stop)
        self.pchv_set_task.clicked.connect(self.set_pchv_task)
        self.w2.pchv.speed_reached.connect(self.pchv_on_task.setChecked)
        self.w2.pchv.break_on.connect(self.pchv_break.setChecked)
        self.w2.pchv.get_ready.connect(self.pchv_ready.setChecked)
        self.w2.pchv.speed_changed.connect(self.speed_changed)
        self.w2.pchv.alarmed.connect(self.on_warning)
        self.w2.pchv.warning.connect(self.on_warning)

        self.w3 = self.server.workers[2]
        self.w3.gen.changed.connect(self.gen_changed)
        self.w3.gen.warning.connect(self.on_warning)

        self.w4 = self.server.workers[3]
        self.w4.freq.changed.connect(self.freq_changed)
        self.w4.freq.warning.connect(self.on_warning)

        self.server.start()

        self.w1.do2.value = [1, 1] + [0] * 7 + [1] * 6 + [0] * 17
        self.w1.do2.setActive()

        self.w3.gen.value = [2000, 4000, 8000]
        self.w3.gen.setActive()

    def closeEvent(self, e):
        self.server.stop()
        e.accept()

    @QtCore.pyqtSlot(str)
    def on_warning(self, msg):
        self.warning.append(msg)

    @QtCore.pyqtSlot()
    def di_changed(self):
        self.di.setText('di: {}'.format(self.w1.di.value))

    @QtCore.pyqtSlot()
    def ai_changed(self):
        self.ai.setText('ai: {}'.format(self.w1.ai.value))

    @QtCore.pyqtSlot()
    def ao_changed(self):
        self.ao.setText('ao: {}'.format(self.w1.ao.value))

    @QtCore.pyqtSlot()
    def do1_changed(self):
        self.do1.setText('do1: {}'.format(self.w1.do1.value))

    @QtCore.pyqtSlot()
    def do2_changed(self):
        self.do2.setText('do2: {}'.format(self.w1.do2.value))

    @QtCore.pyqtSlot()
    def pv1_changed(self):
        self.pv1.setText('pv1: {}'.format(self.w1.pv1.value))

    @QtCore.pyqtSlot()
    def pv2_changed(self):
        self.pv2.setText('pv2: {}'.format(self.w1.pv2.value))

    @QtCore.pyqtSlot()
    def pa1_changed(self):
        self.pa1.setText('pa1: {}'.format(self.w1.pa1.value))

    @QtCore.pyqtSlot()
    def pa2_changed(self):
        self.pa2.setText('pa2: {}'.format(self.w1.pa2.value))

    @QtCore.pyqtSlot()
    def pa3_changed(self):
        self.pa3.setText('pa3: {}'.format(self.w1.pa3.value))

    @QtCore.pyqtSlot()
    def gen_changed(self):
        self.gen.setText('gen: {}'.format(self.w3.gen.value))

    @QtCore.pyqtSlot()
    def freq_changed(self):
        v = self.w4.freq.value[2]
        self.w3.gen.value = [v, v * 2, v * 3]
        self.w3.gen.setActive()
        self.freq.setText('freq: {}'.format(self.w4.freq.value))

    @QtCore.pyqtSlot(float)
    def speed_changed(self, speed):
        self.pchv_speed.setText('Скорость: {:4.0f}'.format(speed))

    def set_pchv_task(self):
        try:
            speed = float(self.pchv_task.text())
            if speed < 0: speed = 0
            if speed > 1500: speed = 1500
        except Exception:
            pass
        self.w2.pchv.speed = speed


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Main()
    win.show()
    app.exec_()
