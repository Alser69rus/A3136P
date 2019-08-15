from PyQt5 import QtCore, QtWidgets
import opc.opc


class Main(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opc = opc.opc.Server()

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

        self.pid = QtWidgets.QWidget()
        self.hbox2 = QtWidgets.QHBoxLayout()
        self.pida_act = QtWidgets.QCheckBox('ПИДа')
        self.pida_act.setChecked(self.opc.pida.active)
        self.pida_task = QtWidgets.QLineEdit(str(self.opc.pida.task))
        self.pida_settask = QtWidgets.QPushButton('Задать угол')
        self.pida_p = QtWidgets.QLineEdit(str(self.opc.pida.kp))
        self.pida_i = QtWidgets.QLineEdit(str(self.opc.pida.ki))
        self.pida_d = QtWidgets.QLineEdit(str(self.opc.pida.kd))
        self.pida_e = QtWidgets.QLineEdit(str(self.opc.pida.eps))
        self.pida_cal = QtWidgets.QPushButton('Калибр. А')
        self.pidc_act = QtWidgets.QCheckBox('ПИДc')
        self.pidc_act.setChecked(self.opc.pidc.active)
        self.pidc_task = QtWidgets.QLineEdit(str(self.opc.pidc.task))
        self.pidc_settask = QtWidgets.QPushButton('Задать ток')
        self.pidc_p = QtWidgets.QLineEdit(str(self.opc.pidc.kp))
        self.pidc_i = QtWidgets.QLineEdit(str(self.opc.pidc.ki))
        self.pidc_d = QtWidgets.QLineEdit(str(self.opc.pidc.kd))
        self.pidc_e = QtWidgets.QLineEdit(str(self.opc.pidc.eps))
        self.pidc_cal = QtWidgets.QPushButton('Калибр. C')
        self.pid.setLayout(self.hbox2)
        self.hbox2.addWidget(self.pida_act)
        self.hbox2.addWidget(self.pida_task)
        self.hbox2.addWidget(self.pida_settask)
        self.hbox2.addWidget(self.pida_p)
        self.hbox2.addWidget(self.pida_i)
        self.hbox2.addWidget(self.pida_d)
        self.hbox2.addWidget(self.pida_e)
        self.hbox2.addWidget(self.pida_cal)
        self.hbox2.addWidget(self.pidc_act)
        self.hbox2.addWidget(self.pidc_task)
        self.hbox2.addWidget(self.pidc_settask)
        self.hbox2.addWidget(self.pidc_p)
        self.hbox2.addWidget(self.pidc_i)
        self.hbox2.addWidget(self.pidc_d)
        self.hbox2.addWidget(self.pidc_e)
        self.hbox2.addWidget(self.pidc_cal)

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
        self.vbox.addWidget(self.pid)

        self.vbox.addWidget(self.warning)

        self.opc.di.changed.connect(self.di_changed)
        self.opc.ai.changed.connect(self.ai_changed)
        self.opc.ao.changed.connect(self.ao_changed)
        self.opc.do1.changed.connect(self.do1_changed)
        self.opc.do2.changed.connect(self.do2_changed)

        self.opc.pv1.changed.connect(self.pv1_changed)
        self.opc.pv2.changed.connect(self.pv2_changed)
        self.opc.pa1.changed.connect(self.pa1_changed)
        self.opc.pa2.changed.connect(self.pa2_changed)
        self.opc.pa3.changed.connect(self.pa3_changed)

        self.pchv_start.clicked.connect(self.opc.pchv.start)
        self.pchv_stop.clicked.connect(self.opc.pchv.stop)
        self.pchv_set_task.clicked.connect(self.set_pchv_task)
        self.opc.pchv.speed_reached.connect(self.pchv_on_task.setChecked)
        self.opc.pchv.break_on.connect(self.pchv_break.setChecked)
        self.opc.pchv.get_ready.connect(self.pchv_ready.setChecked)
        self.opc.pchv.speed_changed.connect(self.speed_changed)

        self.opc.gen.changed.connect(self.gen_changed)

        self.opc.freq.changed.connect(self.freq_changed)

        self.opc.warning.connect(self.on_warning)
        self.opc.error.connect(self.on_warning)

        self.opc.pida.active_change.connect(self.pida_act.setChecked)
        self.opc.pidc.active_change.connect(self.pidc_act.setChecked)
        self.pida_act.toggled.connect(self.opc.pida.setActive)
        self.pidc_act.toggled.connect(self.opc.pidc.setActive)
        self.pida_settask.clicked.connect(self.set_pida_task)
        self.pidc_settask.clicked.connect(self.set_pidc_task)
        self.pida_cal.clicked.connect(self.set_pida_cal)
        self.pidc_cal.clicked.connect(self.set_pidc_cal)

        self.opc.start()

        self.opc.connect_pchv()
        self.opc.connect_pe()
        self.opc.connect_gen()

        self.opc.freq.setClear(0)

        self.opc.gen.setActive()

    def closeEvent(self, e):
        self.hide()
        self.opc.stop()
        e.accept()

    @QtCore.pyqtSlot(str)
    def on_warning(self, msg):
        self.warning.append(msg)

    @QtCore.pyqtSlot()
    def di_changed(self):
        self.di.setText('di: {}'.format(self.opc.di.value))

    @QtCore.pyqtSlot()
    def ai_changed(self):
        self.ai.setText('ai: {}'.format(self.opc.ai.value))

    @QtCore.pyqtSlot()
    def ao_changed(self):
        self.ao.setText('ao: {}'.format(self.opc.ao.value))

    @QtCore.pyqtSlot()
    def do1_changed(self):
        self.do1.setText('do1: {}'.format(self.opc.do1.value))

    @QtCore.pyqtSlot()
    def do2_changed(self):
        self.do2.setText('do2: {}'.format(self.opc.do2.value))

    @QtCore.pyqtSlot()
    def pv1_changed(self):
        self.pv1.setText('pv1: {:4.2f}'.format(self.opc.pv1.value))

    @QtCore.pyqtSlot()
    def pv2_changed(self):
        self.pv2.setText('pv2: {}'.format(self.opc.pv2.value))

    @QtCore.pyqtSlot()
    def pa1_changed(self):
        self.pa1.setText('pa1: {}'.format(self.opc.pa1.value))

    @QtCore.pyqtSlot()
    def pa2_changed(self):
        self.pa2.setText('pa2: {}'.format(self.opc.pa2.value))

    @QtCore.pyqtSlot()
    def pa3_changed(self):
        self.pa3.setText('pa3: {:4.3f}'.format(self.opc.pa3.value))

    @QtCore.pyqtSlot()
    def gen_changed(self):
        self.gen.setText('gen: {}'.format(self.opc.gen.value))

    @QtCore.pyqtSlot()
    def freq_changed(self):
        v = self.opc.freq.value[2]
        self.opc.gen.value = [v, v * 2, v * 3]
        self.opc.gen.setActive()
        self.freq.setText('freq: {}'.format(self.opc.freq.value))

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
        self.opc.pchv.speed = speed

    def set_pida_task(self):
        self.opc.pidc.setActive(False)
        self.opc.pida.setTask(float(self.pida_task.text()))

    def set_pidc_task(self):
        self.opc.pida.setActive(False)
        self.opc.pidc.setTask(float(self.pidc_task.text()))

    def set_pida_cal(self):
        self.opc.pida.kp = float(self.pida_p.text())
        self.opc.pida.ki = float(self.pida_i.text())
        self.opc.pida.kd = float(self.pida_d.text())
        self.opc.pida.eps = float(self.pida_e.text())

    def set_pidc_cal(self):
        self.opc.pidc.kp = float(self.pidc_p.text())
        self.opc.pidc.ki = float(self.pidc_i.text())
        self.opc.pidc.kd = float(self.pidc_d.text())
        self.opc.pidc.eps = float(self.pidc_e.text())


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Main()
    win.showMaximized()
    app.exec_()
