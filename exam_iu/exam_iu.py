from PyQt5 import QtCore, QtWidgets
import time

com = None


class ExamIU(QtCore.QState):
    """Проверка работоспособности ИУ"""
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    btnBack = None
    btnOk = None

    def __init__(self, parent=None, server=None, form=None):
        super().__init__(parent)
        global com
        com = self

        self.opc = server
        self.current = server.current
        self.frm_main = form
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked
        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.pchv = self.opc.pchv
        self.pa3 = self.opc.pa3
        self.ao = self.opc.ao
        self.ai = self.opc.ai
        self.pida = self.opc.pida
        self.pidc = self.opc.pidc
        self.freq = self.opc.freq

        self.frm1 = form.exam_iu_pressure
        self.frm2 = form.exam_iu_pe_check
        self.frm3 = form.exam_iu_dp_check

        self.tachometer1 = self.frm1.tachometer
        self.tachometer2 = self.frm2.tachometer
        self.tachometer3 = self.frm3.tachometer
        self.pchv.speed_changed.connect(self.tachometer1.setValue, QtCore.Qt.QueuedConnection)
        self.pchv.speed_changed.connect(self.tachometer2.setValue, QtCore.Qt.QueuedConnection)
        self.pchv.speed_changed.connect(self.tachometer3.setValue, QtCore.Qt.QueuedConnection)
        self.pchv.task_changed.connect(self.tachometer1.setTask, QtCore.Qt.QueuedConnection)
        self.pchv.task_changed.connect(self.tachometer2.setTask, QtCore.Qt.QueuedConnection)
        self.pchv.task_changed.connect(self.tachometer3.setTask, QtCore.Qt.QueuedConnection)

        self.indicator1 = self.frm2.indicator
        self.indicator2 = self.frm3.indicator
        self.pida.task_changed.connect(self.indicator1.setTask, QtCore.Qt.QueuedConnection)
        self.pida.task_changed.connect(self.indicator2.setTask, QtCore.Qt.QueuedConnection)
        self.pidc.task_changed.connect(self.indicator1.setTask, QtCore.Qt.QueuedConnection)
        self.pidc.task_changed.connect(self.indicator2.setTask, QtCore.Qt.QueuedConnection)
        self.opc.br2_changed.connect(self.indicator1.setValue, QtCore.Qt.QueuedConnection)
        self.opc.br2_changed.connect(self.indicator2.setValue, QtCore.Qt.QueuedConnection)

        self.ammeter1 = self.frm2.pa3
        self.ammeter2 = self.frm3.pa3
        self.pa3.changed.connect(self.ammeter1.setValue, QtCore.Qt.QueuedConnection)
        self.pa3.changed.connect(self.ammeter2.setValue, QtCore.Qt.QueuedConnection)

        self.clock = self.frm1.timer

        self.dp = self.frm3.dp
        self.opc.dp_changed.connect(self.frm3.dp.setValue, QtCore.Qt.QueuedConnection)

        self.pressure = self.frm1.pressure
        self.opc.pressure_change.connect(self.pressure.setValue)

        self.text1 = self.frm1.text
        self.text2 = self.frm2.text
        self.text3 = self.frm3.text

        # Обработка ошибок и возврат по нажатию НАЗАД
        self.error = Error(self)
        self.stop_pid = StopPid(self)
        self.stop_PCHV = StopPCHV(self)
        self.wait_stop_pchv = WaitStopPCHV(self)
        self.disconnect_devices = DisconnectDevices(self)
        self.finish = Finish(self)
        self.addTransition(com.opc.error, self.error)
        self.error.addTransition(self.stop_pid)
        self.addTransition(com.btnBack, self.stop_pid)
        self.stop_pid.addTransition(self.stop_PCHV)
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
        self.install_0.addTransition(self.install_1)
        self.install_1.addTransition(self.btnOk, self.install_2)
        self.install_2.addTransition(self.btnOk, self.install_3)
        self.install_3.addTransition(self.btnOk, self.install_4)

        # Прокачка
        self.connect_dev = ConnectDev(self)
        self.prepare = Prepare(self)
        self.wait_timer = WaitTimer(self)
        self.install_4.addTransition(self.btnOk, self.connect_dev)
        self.connect_dev.addTransition(self.prepare)
        self.prepare.addTransition(self.wait_timer)
        self.wait_timer.addTransition(self.pchv.updated, self.wait_timer)

        # Замер давлений
        self.print_result = PrintResult(self)
        self.set_speed_pressure1 = SetSpeed(self)
        self.measure_p1 = MeasureP(self)
        self.set_speed_pressure2 = SetSpeed(self)
        self.measure_p2 = MeasureP(self)
        self.select_p3_i1 = SelectP3I1(self)
        self.stop_pchv1 = StopPCHV(self)
        self.connect_pchv_reverse = ConnectPchvReverse(self)
        self.set_speed_pressure3 = SetSpeed(self)
        self.measure_p3 = MeasureP(self)
        self.set_speed_pressure4 = SetSpeed(self)
        self.measure_p4 = MeasureP(self)
        self.stop_pchv2 = StopPCHV(self)
        self.connect_pchv2 = ConnectPchv(self)
        self.wait_timer.addTransition(self.success, self.set_speed_pressure1)
        self.set_speed_pressure1.addTransition(self.pchv.speed_reached, self.measure_p1)
        self.measure_p1.addTransition(self.success, self.set_speed_pressure2)
        self.measure_p1.addTransition(self.ai.updated, self.measure_p1)
        self.set_speed_pressure2.addTransition(self.pchv.speed_reached, self.measure_p2)
        self.measure_p2.addTransition(self.ai.updated, self.measure_p2)
        self.measure_p2.addTransition(self.success, self.select_p3_i1)

        self.select_p3_i1.addTransition(self.fail, self.stop_pchv1)
        self.stop_pchv1.addTransition(self.pchv.break_on, self.connect_pchv_reverse)
        self.connect_pchv_reverse.addTransition(self.opc.do2.updated, self.set_speed_pressure3)
        self.set_speed_pressure3.addTransition(self.pchv.speed_reached, self.measure_p3)
        self.measure_p3.addTransition(self.success, self.set_speed_pressure4)
        self.measure_p3.addTransition(self.ai.updated, self.measure_p3)
        self.set_speed_pressure4.addTransition(self.pchv.speed_reached, self.measure_p4)
        self.measure_p4.addTransition(self.success, self.stop_pchv2)
        self.measure_p4.addTransition(self.ai.updated, self.measure_p4)
        self.stop_pchv2.addTransition(self.pchv.break_on, self.connect_pchv2)

        # Измерение тока в силовой цепи на 2 и 8 позиции
        self.show_frm2 = ShowFrm2(self)
        self.set_speed_pe = SetSpeed(self)
        self.set_pos0 = SetPos0(self)
        self.reset_br2 = ResetBr2(self)
        self.set_pos2 = SetPos(self)
        self.measure_i1 = MeasureI(self)
        self.set_pos8 = SetPos(self)
        self.measure_i2 = MeasureI(self)
        self.select_p3_i1.addTransition(self.success, self.show_frm2)
        self.connect_pchv2.addTransition(self.opc.do2.updated, self.show_frm2)
        self.show_frm2.addTransition(self.set_speed_pe)
        self.set_speed_pe.addTransition(self.pchv.speed_reached, self.set_pos0)
        self.set_pos0.addTransition(self.pidc.task_reached, self.reset_br2)
        self.reset_br2.addTransition(self.freq.cleared, self.set_pos2)
        self.set_pos2.addTransition(self.pida.task_reached, self.measure_i1)
        self.measure_i1.addTransition(self.pa3.updated, self.measure_i1)
        self.measure_i1.addTransition(self.success, self.set_pos8)
        self.set_pos8.addTransition(self.pida.task_reached, self.measure_i2)
        self.measure_i2.addTransition(self.pa3.updated, self.measure_i2)


        # Измерение частоты ДП
        self.show_frm3 = ShowFrm3(self)
        self.set_speed_dp = SetSpeed(self)
        self.set_pos1 = SetPos(self)
        self.measure_f1 = MeasureF(self)
        self.set_pos9 = SetPos(self)
        self.measure_f2 = MeasureF(self)
        self.set_current0 = SetPos0(self)
        self.stop_pchv3 = StopPCHV(self)
        self.measure_i2.addTransition(self.success, self.show_frm3)
        self.show_frm3.addTransition(self.set_speed_dp)
        self.set_speed_dp.addTransition(self.pchv.speed_reached, self.set_pos1)
        self.set_pos1.addTransition(self.pida.task_reached, self.measure_f1)
        self.measure_f1.addTransition(self.freq.updated, self.measure_f1)
        self.measure_f1.addTransition(self.success, self.set_pos9)
        self.set_pos9.addTransition(self.pida.task_reached, self.measure_f2)
        self.measure_f2.addTransition(self.freq.updated, self.measure_f2)
        self.measure_f2.addTransition(self.success, self.set_current0)
        self.set_current0.addTransition(self.stop_pchv3)
        self.stop_pchv3.addTransition(self.print_result)

        # переменные для хранения результатов измерений
        self.print_result.addTransition(self.stop_pid)
        self.setInitialState(self.install_0)
        self.time = 0
        self.iu = com.frm_main.select_iu
        self.count = 0
        self.value = 0
        self.pr = []
        self.speed_idx = 0
        self.text = self.text1
        self.frm = self.frm1
        self.cur = []
        self.pos = [2, 8, 1, 9]
        self.pos_idx = 0
        self.br2_zero = 0
        self.f_dp = []


class Error(QtCore.QState):
    def onEntry(self, e):
        pass


class StopPid(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.current.setActive('pidc', 0)


class StopPCHV(QtCore.QState):
    def onEntry(self, e):
        global com
        com.pchv.stop()


class WaitStopPCHV(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        if com.pchv.breaking:
            com.success.emit()


class DisconnectDevices(QtCore.QState):
    def onEntry(self, e):
        global com
        com.opc.do2.setValue([0] * 32)


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
        com.pidc.setActive(False)
        com.frm_main.connectmenu()
        com.pchv.setActive(False)


class Install0(QtCore.QState):
    """подготовка"""

    def onEntry(self, e):
        global com
        com.frm_main.disconnectmenu()

        com.freq.setClear(2)
        com.opc.ai.setActive(True)
        com.opc.di.setActive(True)
        com.opc.pv1.setActive(False)
        com.opc.pv2.setActive(False)
        com.opc.pa1.setActive(False)
        com.opc.pa2.setActive(False)
        com.opc.pa3.setActive(True)
        com.pchv.setActive(False)


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


class ConnectDev(QtCore.QState):
    """Подключение оборудования"""

    def onEntry(self, QEvent):
        global com
        com.pchv.setActive(True)
        com.opc.connect_pchv(True, com.iu.dir[0])
        com.opc.connect_pe(True)
        com.opc.connect_dp(True)
        com.current.setActive('manual', 10)


class ConnectPchvReverse(QtCore.QState):
    """Подключение ПЧВ в обратном направлении"""

    def onEntry(self, QEvent):
        global com
        com.opc.connect_pchv(True, com.iu.dir[1])
        com.speed_idx = 1


class ConnectPchv(QtCore.QState):
    """Подключение ПЧВ в прямом направлении"""

    def onEntry(self, QEvent):
        global com
        com.opc.connect_pchv(True, com.iu.dir[0])


class Prepare(QtCore.QState):
    """Прокачка"""

    def onEntry(self, QEvent):
        global com
        com.frm = com.frm1
        com.text = com.text1
        com.frm_main.stl.setCurrentWidget(com.frm1)
        com.time = time.time()
        com.pchv.speed = com.iu.speed[0]
        com.clock.setValue(com.clock.max_v)
        com.pr = []
        com.cur = []


class WaitTimer(QtCore.QState):
    """Ожидание завершения прокачки"""

    def onEntry(self, QEvent):
        global com
        t = com.clock.max_v + com.time - time.time()
        com.clock.setValue(t)
        com.text.setText('<p>Ожидайте.<br>Выполняется прогрев исполнительного устройства перед началом '
                         'испытания.</p><p>Осталось {: 3.0f} мин {: 2.0f} сек</p>'.format(t // 60, t % 60))
        if t <= 0:
            com.speed_idx = 1
            com.success.emit()


class SetSpeed(QtCore.QState):
    """Установка скорости1 для проверки давления"""

    def onEntry(self, QEvent):
        global com
        com.pchv.speed = com.iu.speed[com.speed_idx]
        com.text.setText('<p>Ожидайте.<br>Выполняется установка скорости вращения '
                         '{: 4.0f}</p>'.format(com.iu.speed[com.speed_idx]))
        com.count = 0
        com.value = 0


class MeasureP(QtCore.QState):
    """Измерение давления"""

    def onEntry(self, QEvent):
        com.count += 1
        com.value += com.opc.pressure
        com.text.setText('<p>Ожидайте.<br>Выполняется измерение давления в аккумуляторе<br>'
                         'Давление: {: 5.3f} МПа, измерение завершено на: {:.0%}</p>'.format(com.value / com.count,
                                                                                             com.count / 23))
        if com.count == 23:
            com.pr.append(com.value / com.count)
            com.speed_idx += 1
            com.success.emit()


class SelectP3I1(QtCore.QState):
    """Выбор измерение давления 3 или тока 1"""

    def onEntry(self, QEvent):
        global com
        if com.iu.dir[0] == com.iu.dir[1]:
            com.success.emit()
        else:
            com.fail.emit()


class ShowFrm2(QtCore.QState):
    """Показ формы измерения тока"""

    def onEntry(self, QEvent):
        global com
        com.frm_main.stl.setCurrentWidget(com.frm2)
        com.frm = com.frm2
        com.text = com.text2
        com.speed_idx = 3


class SetPos0(QtCore.QState):
    """Установка позиции энкодера 0"""

    def onEntry(self, QEvent):
        global com
        com.current.setActive('pidc', 0)
        com.text.setText('<p>Ожидайте.<br>Выполняется установка тока 0 А в силовой цепи.</p>')


class ResetBr2(QtCore.QState):
    """Сброс энкодера угла"""

    def onEntry(self, QEvent):
        global com
        com.freq.setClear(0)
        com.text.setText('<p>Ожидайте.<br>Выполняется сброс датчика угла.</p>')
        com.pos_idx = 0


class SetPos(QtCore.QState):
    """Установка позиции 2"""

    def onEntry(self, QEvent):
        global com
        com.text.setText('<p>Ожидайте.<br>Выполняется установка позиции {:.0f} на индикаторе нагрузки.</p>'.format(
            com.pos[com.pos_idx]))
        com.current.setActive('pida', com.pos[com.pos_idx])
        com.value = 0
        com.count = 0


class MeasureI(QtCore.QState):
    """Измерение тока"""

    def onEntry(self, QEvent):
        com.count += 1
        com.value += com.pa3.value
        com.text.setText('<p>Ожидайте.<br>Выполняется измерение тока силовой цепи<br>'
                         'Ток: {: 5.3f} А, измерение завершено на: {:.0%}</p>'.format(com.value / com.count,
                                                                                      com.count / 23))
        if com.count == 23:
            com.cur.append(com.value / com.count)
            com.pos_idx += 1
            com.success.emit()


class ShowFrm3(QtCore.QState):
    """Показать форму проверки ДП"""

    def onEntry(self, QEvent):
        global com
        com.frm_main.stl.setCurrentWidget(com.frm3)
        com.frm = com.frm3
        com.text = com.text3
        com.speed_idx = 4
        com.f_dp = []


class MeasureF(QtCore.QState):
    """Измерение частоты ДП"""

    def onEntry(self, QEvent):
        com.count += 1
        com.value += com.freq.value[7]
        com.text.setText('<p>Ожидайте.<br>Выполняется измерение сигнала датчика линейных перемещений<br>'
                         'Частота: {: 6.3f} кГц, измерение завершено на: {:.0%}</p>'.format(com.value / com.count,
                                                                                            com.count / 23))
        if com.count == 23:
            com.f_dp.append(com.value / com.count)
            com.pos_idx += 1
            com.success.emit()


class PrintResult(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        print(com.pr)
        print(com.cur)
        print(com.f_dp)
