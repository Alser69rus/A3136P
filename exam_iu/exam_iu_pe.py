from PyQt5 import QtCore


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    signalStr = QtCore.pyqtSignal(str)
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()


class Exam_iu_pe(QtCore.QObject):
    def __init__(self, server=None, form=None, parent=None):
        super().__init__(parent)
        self.server = server
        self.form = form
        self.text = self.form.exam_iu_pe_check.text
        self.c = Communicate()
        self.count = 0
        self.current_u1 = 0
        self.angle_2 = 0

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
        self.st_br3_3 = QtCore.QState(self.state)
        self.st_check_i1_1 = QtCore.QState(self.state)
        self.st_check_i1_2 = QtCore.QState(self.state)
        self.st_tune_i1 = QtCore.QState(self.state)
        self.st_check_i2_1 = QtCore.QState(self.state)
        self.st_check_i2_2 = QtCore.QState(self.state)

        self.st_err = QtCore.QState(self.state)
        self.st_switch_off = QtCore.QState(self.state)
        self.st_switch_off2 = QtCore.QState(self.state)
        self.st_finish = QtCore.QFinalState(self.state)

        self.state.setInitialState(self.st_inst0)

        self.state.addTransition(self.form.btnPanel.btnBack.clicked, self.st_switch_off)
        self.state.addTransition(self.server.c.error, self.st_err)
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
        self.st_br3_2.addTransition(self.form.btnPanel.btnOk.clicked, self.st_br3_3)
        self.st_br3_3.addTransition(self.st_check_i1_1)
        self.st_check_i1_1.addTransition(self.form.btnPanel.btnOk.clicked, self.st_check_i1_2)
        self.st_check_i1_2.addTransition(self.c.fail, self.st_tune_i1)
        self.st_check_i1_2.addTransition(self.c.success, self.st_check_i2_1)
        self.st_tune_i1.addTransition(self.server.c.updated, self.st_tune_i1)
        self.st_tune_i1.addTransition(self.form.btnPanel.btnOk.clicked, self.st_br3_1)
        self.st_check_i2_1.addTransition(self.server.c.updated, self.st_check_i2_2)
        self.st_check_i2_2.addTransition(self.server.c.updated, self.st_check_i2_2)

        self.st_err.addTransition(self.st_switch_off)
        self.st_switch_off.addTransition(self.server.c.suspended, self.st_switch_off2)
        self.st_switch_off2.addTransition(self.server.c.updated, self.st_finish)

        self.st_set_pe.onEntry = self.on_set_pe
        self.st_inst0.onEntry = self.on_inst0
        self.st_inst1.onEntry = self.on_inst1
        self.st_inst2.onEntry = self.on_inst2
        self.st_inst3.onEntry = self.on_inst3
        self.st_inst4.onEntry = self.on_inst4
        self.st_start500_1.onEntry = self.on_start500_1
        self.st_start500_2.onEntry = self.on_start500_2
        self.st_start500_3.onEntry = self.on_start500_3
        self.st_start500_4.onEntry = self.on_start500_4
        self.st_br3_1.onEntry = self.on_br3_1
        self.st_br3_2.onEntry = self.on_br3_2
        self.st_br3_3.onEntry = self.on_br3_3
        self.st_check_i1_1.onEntry = self.on_check_i1_1
        self.st_check_i1_2.onEntry = self.on_check_i1_2
        self.st_check_i2_1.onEntry = self.on_check_i2_1

        self.st_err.onEntry = self.on_err
        self.st_switch_off.onEntry = self.on_switch_off
        self.st_switch_off2.onEntry = self.on_switch_off2
        self.st_finish.onEntry = self.on_finish

    def on_set_pe(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_set_pe)

    def on_inst0(self, e):
        self.form.disconnectmenu()
        self.server.pchv.speed_updated.connect(self.form.exam_iu_pe_check.tachometer.setValue,
                                               QtCore.Qt.QueuedConnection)

        self.server.pchv.speed_task_changed.connect(self.form.exam_iu_pe_check.tachometer.setTask,
                                                    QtCore.Qt.QueuedConnection)
        self.server.pa3.c.value_changed.connect(self.form.exam_iu_pe_check.pa3.setValue, QtCore.Qt.QueuedConnection)
        self.form.exam_iu_pe_check.indicator.setArrowVisible(True, False)
        self.server.br2.setZero()
        self.server.br2.updated.connect(self.form.exam_iu_pe_check.indicator.setValue)
        self.server.pid_angle.value_changed.connect(self.form.exam_iu_pe_check.indicator.setTask)

    def on_inst1(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst1)

    def on_inst2(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst2)

    def on_inst3(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst3)

    def on_inst4(self, e):
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_inst4)

    def on_start500_1(self, e):
        self.text.setText('Запуск вращения вала ИУ на скорости 500 об/мин')
        self.form.stl.setCurrentWidget(self.form.exam_iu_pe_check)
        self.server.suspend(True)

    def on_start500_2(self, e):
        self.server.do2.value[0] = True
        self.server.do2.value[1] = True
        self.server.do2.value[4] = True
        self.server.do2.value[5] = True
        self.server.do2.value[15] = True
        self.server.do2.write()

        self.server.pchv.wait_ready()

        self.server.pchv.speed = 500
        self.server.pchv.start()

        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv]
        self.server.write_list = [self.server.pid_current, self.server.ao]
        self.server.pchv.only_speed = False
        self.server.suspend(False)

    def on_start500_3(self, e):
        self.text.setText('Запуск вращения вала ИУ на скорости 500 об/мин...ok\n' + \
                          'Установка тока 1,3 А в силовой цепи')
        self.server.pid_current.value = 1.3
        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv, self.server.freq]
        self.server.pchv.only_speed = True
        self.server.freq.chanel_03 = True
        self.server.freq.chanel_47 = False
        self.count = 0

    def on_start500_4(self, e):
        if 1.295 < self.server.pa3.value < 1.305:
            self.count += 1
        if self.count >= 10:
            self.c.signal.emit()

    def on_br3_1(self, e):
        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv, self.server.freq]
        self.server.write_list = [self.server.ao]
        self.server.pchv.only_speed = True
        self.server.freq.chanel_03 = True
        self.server.freq.chanel_47 = False
        self.current_u1 = self.server.ao.value[2]
        self.server.br3.setZero()
        self.text.setText('При помощи поворота рукоятки BR3 отрегулируйте ток силовой цепи\n' + \
                          'таким образом, чтобы указатель на выходном валу ИУ находился на\n' + \
                          'позиции 2\n\nНажмите ПРИНЯТЬ для продолжения')

    def on_br3_2(self, e):
        self.server.ao.value[2] = self.current_u1 + self.server.br3.value

    def on_br3_3(self, e):
        self.current_u1 = self.server.ao.value[2]
        self.server.br2.setZero()
        self.server.br2.offset += 2
        self.angle_2 = self.server.br2.value

    def on_check_i1_1(self, e):
        text = 'Ток в силовой цепи поворотного электромагнита должен быть в пределах 1,25-1,35 А\n\n' + \
               'Фактическое значение: {:.3f} А\n' + \
               'Результат: {}\n\n' + \
               'Нажмите ПРИНЯТЬ для продолжения'
        value = self.server.pa3.value
        if 1.25 <= value <= 1.35:
            res = 'НОРМА'
        else:
            res = 'НЕ НОРМА'
        self.text.setText(text.format(value, res))

    def on_check_i1_2(self, e):
        if 1.25 <= self.server.pa3.value <= 1.35:
            self.c.success.emit()
        else:
            self.c.fail.emit()

    def on_tune_i1(self, e):
        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv]
        self.server.write_list = [self.server.pid_current, self.server.ao]
        self.server.pchv.only_speed = False
        self.server.pid_current.value = 1.3

        text = '''При помощи винта 25 отрегулируйте натяжение пружины 31 
        чтобы стрелка указателя силового вала ИУ встала на позицию 2. 
        
        Если натяжением пружины не получается отрегулировать позицию указателя,
        пружину следует заменить и выполнить повторную проверку.
        Если заменой пружины невозможно исправить проблему, необходимо заменить
        поворотный электромагнит, а неисправный отдать в ремонот.
        
        Нажмите НАЗАД для прекращения проверки и выхода в меню
        Нажмите ПРИНЯТЬ для продолжения проверки'''

        value = self.server.pa3.value
        if 1.25 <= value <= 1.35:
            res = 'НОРМА'
        else:
            res = 'НЕ НОРМА'
        self.text.setText(text.format(value, res))

    def on_check_i2_1(self, e):
        self.text.setText('Будет проведно измерение тока силовой цепи на 8 позиции стрелочного индикатора')
        self.form.exam_iu_pe_check.indicator.setArrowVisible(True, True)
        self.server.pid_angle.value = 8
        self.server.read_list = [self.server.di, self.server.pa3, self.server.pchv]
        self.server.write_list = [self.server.pid_angle, self.server.ao]
        self.server.pchv.only_speed = True
        self.count = 0

    def on_check_i2_2(self, e):
        self.text.setText('Будет проведно измерение тока силовой цепи на 8 позиции стрелочного индикатора\n\n' + \
                          'Текущая позиция: {:.1f}'.format(self.server.br2.value))
        if 7.9 < self.server.br2.value < 8.1:
            self.count += 1
        if self.count >= 10:
            self.c.success.emit()

    def on_err(self, e):
        pass

    def on_switch_off(self, e):
        self.server.suspend(True)

    def on_switch_off2(self, e):
        self.server.do2.value = [0] * 32
        self.server.do2.write()
        self.server.ao.value = [0] * 8
        self.server.ao.write()

        self.server.read_list = [self.server.di, self.server.freq]
        self.server.freq.chanel_03 = True
        self.server.freq.chanel_47 = False

        self.server.pchv.speed_updated.disconnect()
        self.server.pchv.speed_task_changed.disconnect()
        self.server.pa3.c.value_changed.disconnect()
        self.server.br2.updated.disconnect()
        self.server.pid_angle.value_changed.disconnect()
        self.server.suspend(False)

    def on_finish(self, e):
        self.server.write_list = []
        self.form.connectmenu()
