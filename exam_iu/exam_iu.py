from PyQt5 import QtCore, QtWidgets


class ExamIU(QtCore.QState):
    """Проверка работоспособности ИУ"""
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    br2_changed = QtCore.pyqtSignal(float)
    br3_changed = QtCore.pyqtSignal(float)
    btnBack = None
    btnOk = None

    def __init__(self, parent=None, server=None,  form=None):
        super().__init__(parent)
        global com
        com = self
        # self.iu_type = iu_type
        self.opc = server
        self.frm_main = form
        self.frm = self.frm_main.exam_iu_dp_check
        self.text = self.frm.text
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked
        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.pchv = self.opc.pchv
        self.tachometer = self.frm.tachometer
        self.pchv.speed_changed.connect(self.tachometer.setValue, QtCore.Qt.QueuedConnection)
        self.pchv.task_changed.connect(self.tachometer.setTask, QtCore.Qt.QueuedConnection)
        self.pa3 = self.opc.pa3
        self.pa3.changed.connect(self.frm.pa3.setValue, QtCore.Qt.QueuedConnection)
        self.freq = self.opc.freq
        self.freq.changed.connect(self.on_freq_change, QtCore.Qt.QueuedConnection)
        self.pida = self.opc.pida
        self.pidc = self.opc.pidc
        self.indicator = self.frm.indicator
        self.pida.task_changed.connect(self.indicator.setTask, QtCore.Qt.QueuedConnection)
        self.br2_changed.connect(self.indicator.setValue, QtCore.Qt.QueuedConnection)
        # self.dp_changed.connect(self.frm.dp.setValue, QtCore.Qt.QueuedConnection)
        com.btnBack = self.frm_main.btnPanel.btnBack.clicked
        com.btnOk = self.frm_main.btnPanel.btnOk.clicked
        self.ao = self.opc.ao

        # Обработка ошибок и возврат по нажатию НАЗАД
        self.error = Error(self)
        self.stop_PCHV = StopPCHV(self)
        self.wait_stop_pchv = WaitStopPCHV(self)
        self.disconnect_devices = DisconnectDevices(self)
        self.finish = Finish(self)
        self.addTransition(com.opc.error, self.error)
        self.error.addTransition(self.stop_PCHV)
        self.addTransition(com.btnBack, self.stop_PCHV)
        self.stop_PCHV.addTransition(self.wait_stop_pchv)
        self.wait_stop_pchv.addTransition(self.pchv.updated, self.wait_stop_pchv)
        self.wait_stop_pchv.addTransition(self.success, self.disconnect_devices)
        self.disconnect_devices.addTransition(self.finish)

        # Подготовка к испытанию и установка оборудования на стенд
        self.install_0 = Install0(self)
        self.install_1 = Install1(self)
        self.install_2 = Install2(self)
        self.install_3 = Install3(self)
        self.install_4 = Install4(self)
        # self.set_pe = SetPe(self)
        # self.show_check_win = ShowCheckWin(self)
        self.install_0.addTransition(self.install_1)
        self.install_1.addTransition(com.btnOk, self.install_3)
        self.install_3.addTransition(com.btnOk, self.install_4)
        # self.install_4.addTransition(com.btnOk, self.set_pe)
        # self.set_pe.addTransition(com.btnOk, self.show_check_win)
        #
        # # Запуск ПЧВ
        # self.connect_pchv = ConnectPchv(self)
        # self.connect_pe = ConnectPe(self)
        # self.start_PCHV = StartPCHV(self)
        # self.show_check_win.addTransition(self.connect_pchv)
        # self.connect_pchv.addTransition(self.connect_pe)
        # self.connect_pe.addTransition(self.start_PCHV)
        #
        # # Установка тока 0 А и сброс энкодера Br2
        # self.set_current_0 = SetCurrent0(self)
        # self.reset_br2 = ResetBr2(self)
        # self.start_PCHV.addTransition(self.pchv.speed_reached, self.set_current_0)
        # self.set_current_0.addTransition(self.pidc.task_reached, self.reset_br2)
        #
        # # Установка тока 1,3 А и позиции 2
        # self.set_current_13 = SetCurrent13(self)
        # self.show_pos_2 = ShowPos2(self)
        # self.tune_pos_2 = TunePos2(self)
        # self.reset_br2.addTransition(self.freq.cleared, self.set_current_13)
        # self.set_current_13.addTransition(self.pidc.task_reached, self.show_pos_2)
        # self.show_pos_2.addTransition(self.tune_pos_2)
        # self.tune_pos_2.addTransition(self.br3_changed, self.tune_pos_2)
        #
        # # Установка тока 2 А и позиции 8
        # self.set_current_20 = SetCurrent20(self)
        # self.show_pos_8 = ShowPos8(self)
        # self.tune_pos_8 = TunePos8(self)
        # self.tune_pos_2.addTransition(self.btnOk, self.set_current_20)
        # self.set_current_20.addTransition(self.pidc.task_reached, self.show_pos_8)
        # self.show_pos_8.addTransition(self.tune_pos_8)
        # self.tune_pos_8.addTransition(self.br3_changed, self.tune_pos_8)
        #
        # # Отображение результатов проверки и рекомендаций по настройке
        # self.check_result = CheckResult(self)
        # self.tune_i1 = TuneI1(self)
        # self.tune_i2 = TuneI2(self)
        # self.tune_pos_8.addTransition(self.btnOk, self.check_result)
        # self.check_result.addTransition(self.btnOk, self.tune_i1)
        # self.tune_i1.addTransition(self.success, self.tune_i2)
        # self.tune_i1.addTransition(self.btnOk, self.tune_i2)
        # self.tune_i2.addTransition(self.success, self.set_current_0)
        # self.tune_i2.addTransition(self.btnOk, self.set_current_0)

        self.setInitialState(self.install_0)

    def on_freq_change(self):
        v = self.freq.value[0]
        if v != self.br2:
            self.br2 = v
            self.br2_changed.emit(v)
        v = self.freq.value[2]
        if v != self.br3:
            self.br3 = v
            self.br3_changed.emit(v)


class Error(QtCore.QState):
    def onEntry(self, e):
        pass


class StopPCHV(QtCore.QState):
    def onEntry(self, e):
        global com
        com.pchv.stop()
        com.ao.value[2] = 0
        com.ao.setActive()


class WaitStopPCHV(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        if com.pchv.breaking:
            com.success.emit()


class DisconnectDevices(QtCore.QState):
    def onEntry(self, e):
        global com
        com.opc.do2.value = [0] * 32
        com.opc.ao.value = [0] * 8
        com.opc.do2.setActive()
        com.opc.ao.setActive()


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        com.opc.ai.setActive(False)
        com.opc.di.setActive(True)
        com.opc.pv1.setActive(False)
        com.opc.pv2.setActive(False)
        com.opc.pa1.setActive(False)
        com.opc.pa2.setActive(False)
        com.opc.pa3.setActive(False)
        com.frm_main.connectmenu()
        com.pchv.setActive(False)


class Install0(QtCore.QState):
    """подготовка"""

    def onEntry(self, e):
        global com
        com.frm_main.disconnectmenu()

        com.indicator.setArrowVisible(True, False)
        com.indicator.text.setVisible(False)
        com.frm.dp.setArrowVisible(True, False)
        com.freq.setClear(2)
        com.br2 = com.freq.value[0]
        com.br3 = com.freq.value[2]
        com.opc.ai.setActive(False)
        com.opc.di.setActive(True)
        com.opc.pv1.setActive(False)
        com.opc.pv2.setActive(False)
        com.opc.pa1.setActive(False)
        com.opc.pa2.setActive(False)
        com.opc.pa3.setActive(True)
        com.pchv.setActive(False)
        com.f1 = 0
        com.f2 = 0
        com.f3 = 0
        com.dp = 0
        com.br2 = com.freq.value[0]
        com.br3 = com.freq.value[2]


class Install1(QtCore.QState):
    """установка оборудования 1"""

    def onEntry(self, e):
        global com
        com.frm_main.stl.setCurrentWidget(com.frm_main.exam_iu_pe_inst1)


class Install2(QtCore.QState):
    """установка оборудования 2"""

    def onEntry(self, e):
        global com
        com.frm_main.stl.setCurrentWidget(com.frm_main.exam_iu_pe_inst2)


class Install3(QtCore.QState):
    """установка оборудования 3"""

    def onEntry(self, e):
        global com
        com.frm_main.stl.setCurrentWidget(com.frm_main.exam_iu_pe_inst3)


class Install4(QtCore.QState):
    """установка оборудования 4"""

    def onEntry(self, e):
        global com
        com.frm_main.stl.setCurrentWidget(com.frm_main.exam_iu_pe_inst4)
