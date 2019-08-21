from PyQt5 import QtWidgets, QtCore, QtGui

com = None
btnBack = None
btnOk = None
do1 = None
pv1 = None
pa1 = None
power = 20
u_ref = 21
r_stock = 22
r_ballast = 23
opc = None
frm = None
frm_main = None
text = None
img = None


class Form(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.img_bu = QtGui.QPixmap('exam_bu\\bu.png')
        self.img_prog = QtGui.QPixmap('exam_bu\\prog.png')
        self.img_prog2 = QtGui.QPixmap('exam_bu\\prog2.png')
        self.img_xp1 = QtGui.QPixmap('exam_bu\\xp1.jpg')
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


class ExamBp(QtCore.QState):

    def __init__(self, parent=None, server=None, form=None):
        super().__init__(parent)
        global com, btnOk, btnBack, pv1, pa1, do1, opc, frm, frm_main, text, img
        com = self
        opc = server
        do1 = server.do1
        pv1 = opc.pv1
        pa1 = opc.pa1
        frm_main = form
        frm = Form()
        frm_main.stl.addWidget(frm)

        btnBack = frm_main.btnPanel.btnBack.clicked
        btnOk = frm_main.btnPanel.btnOk.clicked
        img = frm.img
        text = frm.text

        self.error = Error(self)
        self.finish = Finish(self)

        self.prepare1 = Prepare1(self)
        self.prepare2 = Prepare2(self)
        self.prepare3 = Prepare3(self)
        self.prepare4 = Prepare4(self)

        self.setInitialState(self.prepare1)

        self.addTransition(opc.error, self.error)
        self.error.addTransition(self.finish)
        self.addTransition(btnBack, self.finish)

        self.prepare1.addTransition(self.btnOk, self.prepare2)
        self.prepare2.addTransition(self.btnOk, self.prepare3)
        self.prepare3.addTransition(self.btnOk, self.prepare4)


class Error(QtCore.QState):
    def onEntry(self, e):
        print('bp_error')


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        do1.setValue([0] * 32)
        frm_main.stl.setCurrentWidget(frm_main.menu_main)
        frm_main.connectmenu()


class Prepare1(QtCore.QState):
    def onEntry(self, QEvent):
        frm_main.disconnectmenu()
        frm_main.stl.setCurrentWidget(frm)
        img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
                         '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам '
                         '"XS1 БУ ПИТ.", "XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p>'
                         '<p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare2(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Подключите разъем привода "XS10 ИУ ПЭ" к разъему привода "XP8 НАГРУЗКА", '
                         'или к разъему поворотного электромагнита регулятора. '
                         '</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare3(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Подключите при помощи шлейфа разъем пульта "XS12 БП Х2"'
                         ' и разъем "ХР13 24 В"</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare4(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Снимите защитную крышку с разъема БУ "ОСНОВНАЯ РАБОТА" и подключите'
                         ' программатор</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')
