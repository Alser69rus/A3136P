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
        self.frm_main = form
        self.frm = Form()
        self.frm_main.stl.addWidget(self.frm)

        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked
        self.btnUp = self.frm_main.btnPanel.btnUp.clicked
        self.btnDown = self.frm_main.btnPanel.btnDown.clicked

        self.text = self.frm.text

        self.dev_type = ''

        self.idx = 0
        self.val = 0
        self.f1 = 0
        self.f2 = 0
        self.args = []

        self.error = Error(self)
        self.finish = Finish(self)

        self.prepare1 = Prepare1(self)
        self.prepare2 = Prepare2(self)
        self.prepare3 = Prepare3(self)
        self.prepare4 = Prepare4(self)
        self.switch_work = SwitchWork(self)
        self.connect_bu_di = ConnectBUDI(self)
        self.connect_bu = ConnectBU(self)

        self.setInitialState(self.prepare1)

        self.addTransition(self.opc.error, self.error)
        self.error.addTransition(self.finish)
        self.back_transition = self.addTransition(self.btnBack, self.finish)

        self.prepare1.addTransition(self.btnOk, self.prepare2)
        self.prepare2.addTransition(self.btnOk, self.prepare3)
        self.prepare3.addTransition(self.btnOk, self.prepare4)


class Error(QtCore.QState):
    def onEntry(self, e):
        print('bu_error')


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        # com.opc.ai.setActive(False)
        # com.opc.di.setActive(True)
        # com.opc.pv1.setActive(False)
        # com.opc.pv2.setActive(False)
        # com.opc.pa1.setActive(False)
        # com.opc.pa2.setActive(False)
        # com.opc.pa3.setActive(False)
        # com.opc.connect_bu_di_power(False)
        # com.opc.connect_bu_power(False)
        com.freq.setActive(True)
        com.frm_main.stl.setCurrentWidget(com.frm_main.check_bu)
        com.frm_main.connectmenu()
        # com.pchv.setActive(False)


class Prepare1(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.opc.connect_bu_di_power(False)
        com.opc.connect_bu_power(False)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.text.setText('<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
                         '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам '
                         '"XS1 БУ ПИТ.", "XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p>'
                         '<p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare2(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText('<p>Подключите разъем привода "XS10 ИУ ПЭ" к разъему привода "XP8 НАГРУЗКА", '
                         'или к разъему поворотного электромагнита регулятора. '
                         '</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare3(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText('<p>Подключите при помощи шлейфа разъем пульта "XS12 БП Х2"'
                         ' и разъем "ХР13 24 В"</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare4(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText('<p>Снимите защитную крышку с разъема БУ "ОСНОВНАЯ РАБОТА" и подключите'
                         ' программатор</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class SwitchWork(QtCore.QState):
    success = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        if bu.dev_type == 'ЭРЧМ30Т3-06':
            com.text.setText('<p>Переведите переключатель "РЕЗЕРВНАЯ РАБОТА" на БУ в положение '
                             '"ОТКЛ."</p><p>Для продолжения нажмите "ПРИНЯТЬ"</p>')
        else:
            self.success.emit()


class ConnectBUDI(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('Производится подключение питания дискретных входов БУ')

        if bu.dev_type in ['ЭРЧМ30Т3-06', 'ЭРЧМ30Т3-04', 'ЭРЧМ30Т3-07']:
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type in ['ЭРЧМ30Т3-12', 'ЭРЧМ30Т3-12-01', 'ЭРЧМ30Т3-12-02', 'ЭРЧМ30Т3-12-03']:
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type in ['ЭРЧМ30Т3-08', 'ЭРЧМ30Т3-08-01']:
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type in ['ЭРЧМ30Т3-02', 'ЭРЧМ30Т3-05', 'ЭРЧМ30Т3-10', 'ЭРЧМ30Т3-10-01']:
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type in ['ЭРЧМ30Т4-01']:
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type in ['ЭРЧМ30Т4-02']:
            com.opc.connect_bu_di_power(True, 24)
        elif bu.dev_type in ['ЭРЧМ30Т4-02-01']:
            com.opc.connect_bu_di_power(True, 48)
        elif bu.dev_type in ['ЭРЧМ30Т4-03']:
            com.opc.connect_bu_di_power(True, 75)
        else:
            com.opc.connect_bu_di_power(False)
            print(f'Неизвестный тип {bu.dev_type}')


class ConnectBU(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('Производится подключение питания БУ')

        com.opc.connect_bu_power()

        lst = [com.frm_main.check_bu.btn_di, com.frm_main.check_bu.btn_fi, com.frm_main.check_bu.btn_shim,
               com.frm_main.check_bu.btn_ai, com.frm_main.check_bu.btn_rt, com.frm_main.check_bu.btn_prepare_r]
        for e in lst:
            e.setEnabled(True)

        lst = [com.frm_main.check_bu.btn_di_r, com.frm_main.check_bu.btn_fi_r, com.frm_main.check_bu.btn_shim_r]
        for it in lst:
            it.setEnabled(False)

        com.frm_main.check_bu.btn_prepare.state = 'ok'
        bu.prepare = True
