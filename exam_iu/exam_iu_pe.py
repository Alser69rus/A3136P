from PyQt5 import QtCore
import cfg

text = None
com = None
form = None
server = None
count = 0
u1 = 0
u2 = 0
i1 = 0
i2 = 0


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    signalStr = QtCore.pyqtSignal(str)
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    btnBack = None
    btnOk = None
    error = None
    suspended = None
    updated = None


class Exam_iu_pe(QtCore.QState):
    def __init__(self, parent=None):
        super().__init__(parent)
        global text
        global com
        global server
        global form

        server = cfg.server
        form = cfg.form

        text = form.exam_iu_pe_check.text
        com = Communicate()
        com.btnOk = form.btnPanel.btnOk.clicked
        com.btnBack = form.btnPanel.btnBack.clicked
        com.error = server.c.error
        com.suspended = server.c.suspended
        com.updated = server.c.updated

        server.pchv.speed_updated.connect(form.exam_iu_pe_check.tachometer.setValue,
                                          QtCore.Qt.QueuedConnection)

        server.pchv.speed_task_changed.connect(form.exam_iu_pe_check.tachometer.setTask,
                                               QtCore.Qt.QueuedConnection)
        server.pa3.c.value_changed.connect(form.exam_iu_pe_check.pa3.setValue, QtCore.Qt.QueuedConnection)
        server.br2.updated.connect(form.exam_iu_pe_check.indicator.setValue, QtCore.Qt.QueuedConnection)
        server.pid_angle.value_changed.connect(form.exam_iu_pe_check.indicator.setTask, QtCore.Qt.QueuedConnection)

        self.install_0 = Install0(self)
        self.install_1 = Install1(self)
        self.install_2 = Install2(self)
        self.install_3 = Install3(self)
        self.install_4 = Install4(self)
        self.set_pe = SetPe(self)

        self.show_check_win = ShowCheckWin(self)
        self.connect_devices = ConnectDevices(self)
        self.start_PCHV = StartPCHV(self)
        self.start_server = StartServer(self)

        self.set_current_13 = SetCurrent13(self)
        self.wait_current_13 = WaitCurrent13(self)

        self.connect_br3 = ConnectBR3(self)
        self.set_u1_with_br3 = SetU1WithBR3(self)
        self.reset_br2 = ResetBR2(self)

        self.prepare_measure_i1 = PrepareMeasureI1(self)
        self.measure_i1 = MeasureI1(self)
        self.check_i1 = CheckI1(self)
        self.tune_i1 = TuneI1(self)

        self.set_position_8 = SetPosition8(self)
        self.wait_position_8 = WaitPosition8(self)

        self.error = Error(self)
        self.stop_server = StopServer(self)
        self.stop_PCHV = StopPCHV(self)
        self.disconnect_devices = DisconnectDevices(self)
        self.disconnect_form = DisconnectForm(self)
        self.finish = Finish(self)

        self.setInitialState(self.install_0)

        self.addTransition(com.error, self.error)
        self.error.addTransition(self.stop_server)
        self.addTransition(com.btnBack, self.stop_server)
        self.stop_server.addTransition(com.suspended, self.stop_PCHV)
        self.stop_PCHV.addTransition(self.disconnect_devices)
        self.disconnect_devices.addTransition(self.disconnect_form)
        self.disconnect_form.addTransition(com.updated, self.finish)

        self.install_0.addTransition(self.install_1)
        self.install_1.addTransition(com.btnOk, self.install_3)
        self.install_3.addTransition(com.btnOk, self.install_4)
        self.install_4.addTransition(com.btnOk, self.set_pe)
        self.set_pe.addTransition(com.btnOk, self.show_check_win)
        self.show_check_win.addTransition(com.suspended, self.connect_devices)
        self.connect_devices.addTransition(self.start_PCHV)
        self.start_PCHV.addTransition(self.start_server)
        self.start_server.addTransition(server.pchv.on_task_signal, self.set_current_13)

        self.set_current_13.addTransition(self.wait_current_13)
        self.wait_current_13.addTransition(com.updated, self.wait_current_13)
        self.wait_current_13.addTransition(com.success, self.connect_br3)

        self.connect_br3.addTransition(self.set_u1_with_br3)
        self.set_u1_with_br3.addTransition(com.updated, self.set_u1_with_br3)
        self.set_u1_with_br3.addTransition(com.btnOk, self.reset_br2)

        self.reset_br2.addTransition(self.prepare_measure_i1)
        self.prepare_measure_i1.addTransition(self.measure_i1)
        self.measure_i1.addTransition(com.updated, self.measure_i1)
        self.measure_i1.addTransition(com.success, self.check_i1)

        self.check_i1.addTransition(com.success, self.set_position_8)
        self.check_i1.addTransition(com.fail, self.tune_i1)
        self.tune_i1.addTransition(com.btnOk, self.set_current_13)

        self.set_position_8.addTransition(self.wait_position_8)
        self.wait_position_8.addTransition(com.updated, self.wait_position_8)


class Install0(QtCore.QState):
    def onEntry(self, e):
        global server
        global form
        form.disconnectmenu()

        form.exam_iu_pe_check.indicator.setArrowVisible(False, False)
        form.exam_iu_pe_check.indicator.text.setVisible(False)
        server.br2.setZero()


class Install1(QtCore.QState):
    def onEntry(self, e):
        global form
        form.stl.setCurrentWidget(form.exam_iu_pe_inst1)


class Install2(QtCore.QState):
    def onEntry(self, e):
        global form
        form.stl.setCurrentWidget(form.exam_iu_pe_inst2)


class Install3(QtCore.QState):
    def onEntry(self, e):
        global form
        form.stl.setCurrentWidget(form.exam_iu_pe_inst3)


class Install4(QtCore.QState):
    def onEntry(self, e):
        global form
        form.stl.setCurrentWidget(form.exam_iu_pe_inst4)


class SetPe(QtCore.QState):
    def onEntry(self, e):
        global form
        form.stl.setCurrentWidget(form.exam_iu_pe_set_pe)


class ShowCheckWin(QtCore.QState):
    def onEntry(self, e):
        global form
        global server
        global text
        text.setText('Запуск вращения вала ИУ на скорости 500 об/мин')
        form.stl.setCurrentWidget(form.exam_iu_pe_check)
        server.suspend(True)


class ConnectDevices(QtCore.QState):
    def onEntry(self, e):
        global server
        server.do2.value[0] = True
        server.do2.value[1] = True
        server.do2.value[4] = True
        server.do2.value[5] = True
        server.do2.value[15] = True
        server.do2.write()


class StartPCHV(QtCore.QState):
    def onEntry(self, e):
        global server
        server.pchv.wait_ready()
        server.pchv.speed = 500
        server.pchv.only_speed = False
        server.pchv.start()


class StartServer(QtCore.QState):
    def onEntry(self, e):
        global server
        server.read_list = [server.di, server.pa3, server.pchv]
        server.write_list = []
        server.suspend(False)


class SetCurrent13(QtCore.QState):
    def onEntry(self, e):
        global server
        global text
        global count
        text.setText('Установка тока 1,3 А в силовой цепи')
        server.pid_current.value = 1.3
        server.read_list = [server.di, server.pa3, server.pchv]
        server.write_list = [server.pid_current, server.ao]
        server.pchv.only_speed = True
        count = 0


class WaitCurrent13(QtCore.QState):
    def onEntry(self, e):
        global server
        global count
        global com
        if 1.295 < server.pa3.value < 1.305:
            count += 1
        if count >= 10:
            com.success.emit()


class ConnectBR3(QtCore.QState):
    def onEntry(self, e):
        global server
        global text
        global u1
        server.read_list = [server.di, server.pa3, server.pchv, server.freq]
        server.write_list = [server.ao]
        server.pchv.only_speed = True
        server.freq.chanel_03 = True
        server.freq.chanel_47 = False
        server.br3.setZero()
        u1 = server.ao.value[2]
        text.setText('При помощи поворота рукоятки BR3 отрегулируйте ток силовой цепи\n' + \
                     'таким образом, чтобы указатель на выходном валу ИУ находился на\n' + \
                     'позиции 2\n\nНажмите ПРИНЯТЬ для продолжения')


class SetU1WithBR3(QtCore.QState):
    def onEntry(self, e):
        global server
        global u1
        server.ao.value[2] = u1 + server.br3.value


class ResetBR2(QtCore.QState):
    def onEntry(self, e):
        global server
        global u1
        global form
        u1 = server.ao.value[2]
        server.br2.setZero()
        server.br2.offset += 2
        form.exam_iu_pe_check.indicator.setArrowVisible(True, True)
        form.exam_iu_pe_check.indicator.text.setVisible(True)


class PrepareMeasureI1(QtCore.QState):
    def onEntry(self, e):
        global server
        global count
        global i1
        i1 = 0
        count = 0
        server.read_list = [server.di, server.pa3, server.pchv]
        server.write_list = []


class MeasureI1(QtCore.QState):
    def onEntry(self, e):
        global server
        global count
        global i1
        global text
        global com
        i1 += server.pa3.value
        count += 1
        text.setText('Производится измерение тока силовой цепи поворотного электромагнита\n' + \
                     'для на второй позиции указателя\n\n' + \
                     'Измеренное значение: {:.3f} А'.format(i1 / count))
        if count > 23:
            i1 = i1 / count
            com.success.emit()


class CheckI1(QtCore.QState):
    def onEntry(self, e):
        global com
        global i1
        if 1.25 <= i1 <= 1.35:
            com.success.emit()
        else:
            com.fail.emit()


class TuneI1(QtCore.QState):
    def onEntry(self, e):
        global server
        global text

        server.read_list = [server.di, server.pa3, server.pchv]
        server.write_list = [server.pid_current, server.ao]
        server.pchv.only_speed = True
        server.pid_current.value = 1.3

        text.setText('''При помощи винта 25 отрегулируйте натяжение пружины 31 
        чтобы стрелка указателя силового вала ИУ встала на позицию 2. 

        Если натяжением пружины не получается отрегулировать позицию указателя,
        пружину следует заменить и выполнить повторную проверку.
        Если заменой пружины невозможно исправить проблему, необходимо заменить
        поворотный электромагнит, а неисправный отдать в ремонот.

        Нажмите НАЗАД для прекращения проверки и выхода в меню
        Нажмите ПРИНЯТЬ для продолжения проверки''')


class SetPosition8(QtCore.QState):
    def onEntry(self, e):
        global server
        global form
        global text
        global count
        global u2
        text.setText('Производится установка указателя в позицию 8')
        form.exam_iu_pe_check.indicator.setArrowVisible(True, True)
        server.pid_angle.value = 8
        server.read_list = [server.di, server.pa3, server.pchv]
        server.write_list = [server.pid_angle, server.ao]
        server.pchv.only_speed = True
        count = 0
        u2 = 0


class WaitPosition8(QtCore.QState):
    def onEntry(self, e):
        global server
        global count
        global com
        if 7.9 < server.br2.value < 8.1:
            count += 1
        if count >= 10:
            com.success.emit()


class Error(QtCore.QState):
    def onEntry(self, e):
        pass


class StopServer(QtCore.QState):
    def onEntry(self, e):
        global server
        server.suspend(True)


class StopPCHV(QtCore.QState):
    def onEntry(self, e):
        global server
        server.pchv.stop()


class DisconnectDevices(QtCore.QState):
    def onEntry(self, e):
        global server
        server.do2.value = [0] * 32
        server.do2.write()
        server.ao.value = [0] * 8
        server.ao.write()

        server.freq.chanel_03 = True
        server.freq.chanel_47 = False
        server.pchv.only_speed = False


class DisconnectForm(QtCore.QState):
    def onEntry(self, e):
        global server
        server.read_list = [server.di, server.freq]
        server.write_list = []
        # server.pchv.speed_updated.disconnect()
        # server.pchv.speed_task_changed.disconnect()
        # server.pa3.c.value_changed.disconnect()
        # server.br2.updated.disconnect()
        # server.pid_angle.value_changed.disconnect()
        server.suspend(False)


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global form
        form.connectmenu()
