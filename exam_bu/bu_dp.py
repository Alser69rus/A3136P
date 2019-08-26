from PyQt5 import QtWidgets, QtCore, QtGui
from guielement.scale import ScaledDevice

com = None


class Form(QtWidgets.QWidget):
    def __init__(self, parent=None):
        global com
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox.addLayout(self.hbox)

        self.tachometer = ScaledDevice(width=200, height=250, arr_x=180, arr_y=190, arr_r=100, min_a=180, max_a=90,
                                       min_v=0, max_v=600, mark_prim=6, mark_sec=5, mark_ter=1, f_mark='{:3.0f}',
                                       f_text='{:>3.0f} об/мин')
        self.tachometer.caption.setText('Тахометр')
        self.tachometer.setValue(0)
        com.opc.pchv.speed_changed.connect(self.tachometer.setValue)
        com.opc.pchv.task_changed.connect(self.tachometer.setTask)

        self.indicator = ScaledDevice(width=230, height=250, arr_x=100, arr_y=410, arr_r=270, arr_length=40, min_a=106,
                                      max_a=74, min_v=0, max_v=10, mark_prim=10, mark_sec=2, mark_ter=1,
                                      f_mark='{:.0f}', f_text='Позиция: {: >4.1f}')
        self.indicator.caption.setText('Указатель\nнагрузки')
        self.indicator.setValue(0)
        com.opc.br2_changed.connect(self.indicator.setValue)
        com.opc.pida.task_changed.connect(self.indicator.setTask)

        self.dp = ScaledDevice(width=320, height=250, arr_x=160, arr_y=610, arr_r=470, arr_length=40, min_a=106,
                               max_a=74, min_v=14, max_v=26, mark_prim=6, mark_sec=2, mark_ter=5,
                               f_mark='{:.0f}', f_text='Частота: {: >6.3f} кГц')
        self.dp.caption.setText('Показания ДП')
        self.dp.setArrowVisible(True, False)
        self.dp.setValue(0)
        com.opc.dp_changed.connect(self.dp.setValue)

        self.hbox.addWidget(self.tachometer)
        self.hbox.addWidget(self.indicator)
        self.hbox.addWidget(self.dp)

        self.text = QtWidgets.QLabel()
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setWordWrap(True)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.text)
        self.vbox.addStretch(1)


class TuneBuDp(QtCore.QState):
    def __init__(self, parent=None, server=None, form=None):
        super().__init__(parent)
        global com
        com = self
        self.opc = server
        self.do1 = server.do1
        self.do2 = server.do2
        self.gen = server.gen
        self.pa3 = server.pa3
        self.ao = server.ao
        self.freq = server.freq
        self.pchv = server.pchv
        self.frm_main = form
        self.frm = Form()
        self.frm_main.stl.addWidget(self.frm)

        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked
        self.btnUp = self.frm_main.btnPanel.btnUp.clicked
        self.btnDown = self.frm_main.btnPanel.btnDown.clicked

        self.font_red = '<font color="red">'
        self.font_end = '</font>'
        self.ok_to_cont = '<p><br>Нажмите "ПРИНЯТЬ" для продолжения.</p>'

        self.text = self.frm.text

        self.dev_type = ''

        self.idx = 0
        self.val = 0
        self.f1 = 0
        self.f2 = 0
        self.args = []
        self.msg_head = ''
        self.msg = ''
        self.msg_tail = ''

        self.error = Error(self)
        self.finish = Finish(self)

        self.prepare1 = Prepare1(self)
        self.prepare2 = Prepare2(self)
        self.prepare3 = Prepare3(self)
        self.prepare4 = Prepare4(self)

        self.setInitialState(self.prepare1)

        self.addTransition(self.opc.error, self.error)
        self.error.addTransition(self.finish)
        self.back_transition = self.addTransition(self.btnBack, self.finish)

        self.prepare1.addTransition(self.btnOk, self.prepare2)
        self.prepare2.addTransition(self.btnOk, self.prepare3)
        self.prepare3.addTransition(self.btnOk, self.prepare4)

        self.connect_iu = ConnectIU(self)
        self.set_speed = SetSpeed(self)
        self.reset_br2 = ResetBr2(self)
        self.prepare4.addTransition(self.btnOk, self.connect_iu)
        self.connect_iu.addTransition(self.pchv.task_changed, self.set_speed)
        self.set_speed.addTransition(self.pchv.speed_reached, self.reset_br2)

        self.set_pos_2 = SetPos2(self)
        self.prepare_measure_2 = PrepareMeasure(self)
        self.measure_2 = MeasureF(self)
        self.reset_br2.addTransition(self.set_pos_2)
        self.set_pos_2.addTransition(self.opc.pida.task_reached, self.prepare_measure_2)
        self.prepare_measure_2.addTransition(self.measure_2)
        self.measure_2.addTransition(self.freq.updated, self.measure_2)

        self.set_pos_8 = SetPos8(self)
        self.prepare_measure_8 = PrepareMeasure(self)
        self.measure_8 = MeasureF(self)
        self.set_current_0 = SetCurrent0(self)
        self.disconnect_iu = DisconnectIU(self)
        self.measure_2.addTransition(self.measure_2.done, self.set_pos_8)
        self.set_pos_8.addTransition(self.opc.pida.task_reached, self.prepare_measure_8)
        self.prepare_measure_8.addTransition(self.measure_8)
        self.measure_8.addTransition(self.freq.updated, self.measure_8)
        self.measure_8.addTransition(self.measure_8.done, self.set_current_0)
        self.set_current_0.addTransition(self.pchv.break_on, self.disconnect_iu)


class Error(QtCore.QState):
    def onEntry(self, e):
        print('bu_error')


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        com.pchv.setActive(True)
        com.opc.connect_pchv(False)
        com.opc.connect_pe(False)
        com.opc.connect_dp(False)

        com.opc.connect_bu_di_power(False)
        com.opc.connect_bu_power(False)
        com.freq.setActive(True)
        com.frm_main.stl.setCurrentWidget(com.frm_main.check_bu)
        com.frm_main.connectmenu()
        com.do1.setValue([0] * 32)
        # com.pchv.setActive(False)


class Prepare1(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.opc.connect_bu_di_power(False)
        com.opc.connect_bu_power(False)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.text.setText(f'<p><br>{com.font_red}Внимание! Согласование датчика положения с блоком управления '
                         f'следует проводить на исправном исполнительном устройстве. Согласование '
                         f'применяется для настройки блока управления на особенности конкретного '
                         f'исполнительного устройства и не проверяет правильность его работы.{com.font_end}</p>'
                         f'{com.ok_to_cont}')


class Prepare2(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText(f'<p><br>'
                         f'<ol><b>Установка исполнительного устройства на привод</b>'
                         f'<li>Установите на вал привода подходящую муфту.'
                         f'<li>Установите исполнительное устройство на привод и зафиксируйте при помощи болтов.'
                         f'<li>Проверте отсутствие перекосов при помощи поворота вала за шестерню распроложееную внутри'
                         f' стенда. При необходимости устраните перекос.'
                         f'</ol>'
                         f'</p>'
                         f'{com.ok_to_cont}')


class Prepare3(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText(f'<p><br>'
                         f'<ol><b>Установка датчика угла поворота</b>'
                         f'<li>Снимите с силового вала рычаг.'
                         f'<li>Установите на силовой вал резиновую муфту.'
                         f'<li>На кронштейне датчика угла поворота ослабте барашки.'
                         f'<li>Присоедините датчик угла при помощи резиновой муфты к силовому валу. '
                         f'По возможности соосно.'
                         f'<li> Зафиксируйте положение кронштейна затянув барашки.'
                         f'<li> Разъем датчика подключите к разъему привода "ХР17 ДАТЧИК УГЛА".'
                         f'</ol>'
                         f'</p>'
                         f'{com.ok_to_cont}')


class Prepare4(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText(f'<p><br>'
                         f'<ol><b>Подключение поворотного электромагнита и датчика положения</b>'
                         f'<li>Подключите датчик положения исполнительного устройства к разъему привода "ХР9 ИУ ДП"'
                         f'<li>Подключите поворотный электромагнит исполнительного устройства к разъему '
                         f'привода "XS10 ИУ ПЭ"'
                         f'</ol>'
                         f'</p>'
                         f'{com.ok_to_cont}')


class ConnectIU(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.msg_head = '<p><br><ol><b>Измерение параметров исполнительного устройства</b>'
        com.msg = '<li>Подключение привода ... </li>'
        com.msg_tail = '</ol></p>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')

        com.pchv.setActive(True)
        com.opc.connect_pchv(True, com.frm_main.select_iu.dir[0])
        com.opc.connect_pe(True)
        com.opc.connect_dp(True)
        com.opc.current.setActive('manual', 10)
        com.pchv.speed = 300


class SetSpeed(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.msg_head += '<li>Подключение привода ... ok</li>'
        com.msg = '<li>Разгон до скорости 500 об/мин ...</li>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')
        com.opc.pchv.speed = 500


class ResetBr2(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.msg_head += '<li>Разгон до скорости 500 об/мин ... ok</li>'
        com.msg = '<li>Установка  позиции индикатора "0" ... </li>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')
        com.freq.setClear(0)


class SetPos2(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.msg_head += '<li>Установка  позиции индикатора "0" ... ok</li>'
        com.msg = '<li>Установка позиции индикатора "2" ... </li>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')
        com.opc.current.setActive('pida', 2)


class PrepareMeasure(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.msg_head += com.msg[:-5] + 'ok</li>'
        com.msg = '<li>Показания датчика положения ... </li>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')
        com.val = 0
        com.idx = 0


class MeasureF(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.idx += 1
        com.val += com.freq.value[7]
        com.text.setText(f'{com.msg_head}{com.msg[:-5]}{com.val/com.idx:6.3f} кГц{com.msg_tail}')
        if com.idx >= 50:
            self.done.emit()


class SetPos8(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.f1 = com.val / com.idx
        com.idx = 0
        com.val = 0

        com.msg_head += f'<li>Показания датчика положения ... {com.f1:6.3f} кГц</li>'
        com.msg = f'<li>Установка позиции индикатора "8" ... </li>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')

        com.opc.current.setActive('pida', 8)


class SetCurrent0(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.f2 = com.val / com.idx
        com.idx = 0
        com.val = 0

        com.msg_head += f'<li>Показания датчика положения ... {com.f2:6.3f} кГц</li>'
        com.msg = f'<li>Отключение привода ... </li>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')

        com.opc.current.setActive('manual', 0)
        com.pchv.speed = 0


class DisconnectIU(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.msg = f'<li>Отключение привода ... ok</li>'
        com.msg_tail = f'</ol>{com.ok_to_cont}</p>'
        com.text.setText(f'{com.msg_head}{com.msg}{com.msg_tail}')

        com.pchv.setActive(False)
        com.opc.connect_pchv(False)
        com.opc.connect_pe(False)
        com.opc.connect_dp(False)
