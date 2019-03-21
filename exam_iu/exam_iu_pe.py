from PyQt5 import QtCore


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    signalStr = QtCore.pyqtSignal(str)


class Exam_iu_pe(QtCore.QObject):
    def __init__(self, server=None, form=None, parent=None):
        super().__init__(parent)
        self.server = server
        self.form = form
        self.c = Communicate()
        self.count = 0
        self.current_u1 = 0

        self.state = QtCore.QState()
        self.st_set_pe = QtCore.QState(self.state)
        self.st_inst0 = QtCore.QState(self.state)
        self.st_inst1 = QtCore.QState(self.state)
        self.st_inst2 = QtCore.QState(self.state)
        self.st_inst3 = QtCore.QState(self.state)
        self.st_inst4 = QtCore.QState(self.state)
        self.st_start500_1 = QtCore.QState(self.state)
        self.st_start500_2 = QtCore.QState(self.state)
        self.st_start500_3 = QtCore.QState(self.state)
        self.st_start500_4 = QtCore.QState(self.state)
        self.st_br3_1 = QtCore.QState(self.state)
        self.st_br3_2 = QtCore.QState(self.state)
        self.st_finish = QtCore.QFinalState(self.state)

        self.state.setInitialState(self.st_inst0)

        self.st_inst0.addTransition(self.st_inst1)
        self.st_inst1.addTransition(self.form.btnPanel.btnOk.clicked, self.st_inst3)
        self.st_inst3.addTransition(self.form.btnPanel.btnOk.clicked, self.st_inst4)
        self.st_inst4.addTransition(self.form.btnPanel.btnOk.clicked, self.st_set_pe)
        self.st_set_pe.addTransition(self.form.btnPanel.btnOk.clicked, self.st_start500_1)
        self.st_start500_1.addTransition(self.server.c.suspended, self.st_start500_2)
        self.st_start500_2.addTransition(self.server.pchv.on_task_signal, self.st_start500_3)
        self.st_start500_3.addTransition(self.st_start500_4)
        self.st_start500_4.addTransition(self.server.c.updated, self.st_start500_4)
        self.st_start500_4.addTransition(self.c.signal, self.st_br3_1)
        self.st_br3_1.addTransition(self.st_br3_2)
        self.st_br3_2.addTransition(self.server.c.updated, self.st_br3_2)

        self.st_set_pe.onEntry = self.on_set_pe_entry
        self.st_finish.onEntry = self.on_finish
        self.st_inst0.onEntry = self.on_inst0_entry
        self.st_inst1.onEntry = self.on_inst1_entry
        self.st_inst2.onEntry = self.on_inst2_entry
        self.st_inst3.onEntry = self.on_inst3_entry
        self.st_inst4.onEntry = self.on_inst4_entry
        self.st_start500_1.onEntry = self.on_start500_1_entry
        self.st_start500_2.onEntry = self.on_start500_2_entry
        self.st_start500_3.onEntry = self.on_start500_3_entry
        self.st_start500_4.onEntry = self.on_start500_4_entry
        self.st_br3_1.onEntry = self.on_br3_1_entry
        self.st_br3_2.onEntry = self.on_br3_2_entry

    def on_start500_1_entry(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_check)
        self.server.suspend(True)

    def on_start500_2_entry(self, e):
        self.server.do2.value[0] = True
        self.server.do2.value[1] = True
        self.server.do2.value[4] = True
        self.server.do2.value[5] = True
        self.server.do2.value[15] = True
        self.server.do2.write()

        self.server.pchv.wait_ready()
        self.server.pchv.speed_updated.connect(self.form.exam_iu_pe_check.tachometr.setValue,
                                               QtCore.Qt.QueuedConnection)

        self.server.pchv.speed_task_changed.connect(self.form.exam_iu_pe_check.tachometr.setTask,
                                                    QtCore.Qt.QueuedConnection)
        self.server.pa3.c.value_changed.connect(self.form.exam_iu_pe_check.pa3.setValue, QtCore.Qt.QueuedConnection)

        self.server.pchv.speed = 500
        self.server.pchv.start()

        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv]
        self.server.write_list = [self.server.pida, self.server.ao]
        self.server.pchv.only_speed = False
        self.server.suspend(False)

    def on_start500_3_entry(self, e):
        self.form.exam_iu_pe_check.text.setText('Запуск вращения вала ИУ на скорости 500 об/мин...ok\n' + \
                                                'Установка тока 1,2 А в силовой цепи')
        self.server.pida.value = 1.2
        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv, self.server.freq]
        self.server.pchv.only_speed = True
        self.server.freq.chanel_03 = True
        self.server.freq.chanel_47 = False
        self.count = 0

    def on_start500_4_entry(self, e):
        if 1.195 < self.server.pa3.value < 1.205:
            self.count += 1
        if self.count >= 10:
            self.c.signal.emit()

    def on_br3_1_entry(self, e):
        self.server.write_list = [self.server.ao]
        self.current_u1 = self.server.ao.value[2]
        self.server.br3.setZero()
        self.form.exam_iu_pe_check.text.setText('При помощи поворота рукоятки BR3 отрегулируйте ток силовой цепи\n' + \
                                                'таким образом, чтобы указатель на выходном валу ИУ находился на\n' + \
                                                'позиции 2\n\nНажмите ПРИНЯТЬ для продолжения')

    def on_br3_2_entry(self, e):
        self.server.ao.value[2] = int(self.current_u1 + self.server.br3.value)

    def on_finish(self, e):
        self.server.do1.value = [0] * 32
        self.server.do5.value = [0] * 32
        self.server.ao.value = [0] * 8

    def on_set_pe_entry(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_set_pe)

    def on_inst0_entry(self, e):
        self.form.disconnectmenu()

    def on_inst1_entry(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst1)

    def on_inst2_entry(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst2)

    def on_inst3_entry(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst3)

    def on_inst4_entry(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst4)
