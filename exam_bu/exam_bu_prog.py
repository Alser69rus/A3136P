from PyQt5 import QtWidgets, QtCore, QtGui

com = None


class Form(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.img_bu = QtGui.QPixmap('exam_bu\\bu.png')
        self.img_prog = QtGui.QPixmap('exam_bu\\prog.png')
        self.img_prog2 = QtGui.QPixmap('exam_bu\\prog2.png')
        self.img_xp1 = QtGui.QPixmap('exam_bu\\xp1.png')
        self.img_bu_prog = QtGui.QPixmap('exam_bu\\bu-prog.png')
        self.img_empty = QtGui.QPixmap('exam_bu\\empty.png')
        self.img = QtWidgets.QLabel()
        self.text = QtWidgets.QLabel()
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setWordWrap(True)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.img)
        self.vbox.addWidget(self.text)
        self.vbox.addStretch(1)
        self.img.setPixmap(self.img_empty)
        self.text.setText(
            '<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
            '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам "XS1 БУ ПИТ.", '
            '"XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p>')


class Exam_bu(QtCore.QState):
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    btnBack = None
    btnOk = None

    def __init__(self, parent=None, server=None, form=None):
        super().__init__(parent)
        global com
        com = self
        self.opc = server
        self.frm_main = form
        self.frm = Form()
        self.frm_main.stl.addWidget(self.frm)
        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked

        self.img = self.frm.img
        self.text = self.frm.text

        self.dev_type = ''

        self.error = Error(self)
        self.finish = Finish(self)
        self.prepare = Prepare(self)
        self.switch_work = SwitchWork(self)
        self.connect_bu = ConnectBU(self)

        self.addTransition(self.opc.error, self.error)
        self.error.addTransition(self.finish)
        self.addTransition(self.btnBack, self.finish)

        self.prepare.addTransition(self.btnOk, self.switch_work)
        self.switch_work.addTransition(self.btnOk, self.connect_bu)
        self.switch_work.addTransition(self.success, self.connect_bu)
        self.connect_bu.addTransition(self.finish)


class Error(QtCore.QState):
    def onEntry(self, e):
        print('bu_error')


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        print('bu_finish')
        # com.opc.ai.setActive(False)
        # com.opc.di.setActive(True)
        # com.opc.pv1.setActive(False)
        # com.opc.pv2.setActive(False)
        # com.opc.pa1.setActive(False)
        # com.opc.pa2.setActive(False)
        # com.opc.pa3.setActive(False)
        # com.pidc.setActive(False)
        com.frm_main.stl.setCurrentWidget(com.frm_main.check_bu)
        com.frm_main.connectmenu()
        # com.pchv.setActive(False)


class Prepare(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
                         '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам '
                         '"XS1 БУ ПИТ.", "XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p><p>Подключите разъем '
                         '"XS10 ИУ ПЭ" к разъему "XP8 НАГРУЗКА", которые расположены на правой стенке привода'
                         ' при помощи шлейфа</p><p>Снимите защитную крышку с разъема БУ "ОСНОВНАЯ РАБОТА" и подключите'
                         ' программатор</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class SwitchWork(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        pass_list = ['ЭРЧМ30T3-04']
        if com.dev_type in pass_list:
            com.success.emit()
        com.text.setText('<p>Переведите переключатель "РЕЗЕРВНАЯ РАБОТА" на БУ в положение '
                         '"ОТКЛ."</p><p>Для продолжения нажмите "ПРИНЯТЬ"</p>')


class ConnectBU(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.opc.connect_bu_power()
        lst = [com.frm_main.check_bu.btn_di, com.frm_main.check_bu.btn_fi1, com.frm_main.check_bu.btn_f12,
               com.frm_main.check_bu.btn_fi3, com.frm_main.check_bu.btn_power, com.frm_main.check_bu.btn_ai1,
               com.frm_main.check_bu.btn_ai2, com.frm_main.check_bu.btn_ai3]
        for e in lst:
            e.setEnabled(True)
        com.frm_main.check_bu.btn_prepare.state = 'ok'
