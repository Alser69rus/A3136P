import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QState as QState

import opc.opc2
import menu.mainform
import exam_iu.exam_iu_pe
import exam_iu.exam_iu_dp
from exam_iu.exam_iu import ExamIU

com = None


class Communicate(QtCore.QObject):
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    opc = None
    form = None


class Main(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        global com
        com = Communicate()

        self.opc = opc.opc2.Server()
        com.opc = self.opc

        self.form = menu.mainform.MainForm(self.opc)
        com.form = self.form
        # com.form.setCursor(QtCore.Qt.BlankCursor)
        self.form.closeEvent = self.closeEvent
        self.form.mnu_main.btnQuit.clicked.connect(self.form.close)
        self.form.showMaximized()

        self.stm = QtCore.QStateMachine()

        self.state_init = StateInit(self.stm)
        self.menu = QState(self.stm)
        self.menu_main = MenuMain(self.menu)
        self.menu_iu = MenuIU(self.menu)
        self.exam_iu_pe_select = ExamIUPESelect(self.stm)
        self.exam_iu_pe = exam_iu.exam_iu_pe.ExamIUPE(self.stm, self.opc, self.form)
        self.exam_iu_dp_select = ExamIUPESelect(self.stm)
        self.exam_iu_dp = exam_iu.exam_iu_dp.ExamIUDP(self.stm, self.opc, self.form)
        self.exam_iu_auth = ExamIUAuth(self.stm)
        self.exam_iu_select = ExamIUSelect(self.stm)
        self.exam_iu = ExamIU(self.stm, self.opc, self.form)

        self.menu_bu = MenuBU(self.stm)
        self.exam_bu_auth = ExamBUAuth(self.stm)
        self.exam_bu_select = ExamBUSelect(self.stm)
        self.check_bu = CheckBU(self.stm)

        self.state_close = QtCore.QFinalState(self.stm)

        self.stm.setInitialState(self.state_init)
        self.menu.setInitialState(self.menu_main)

        self.state_init.addTransition(com.success, self.menu)
        self.menu_main.addTransition(self.form.mnu_main.btnIU.clicked, self.menu_iu)
        self.menu_iu.addTransition(self.form.mnu_iu.btn_IU_back.clicked, self.menu_main)
        self.menu_iu.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_main)
        self.menu_iu.addTransition(self.form.mnu_iu.btn_IU_PE_tune.clicked, self.exam_iu_pe_select)
        self.exam_iu_pe_select.addTransition(self.form.select_iu.btn_ok, self.exam_iu_pe)
        self.exam_iu_pe_select.addTransition(self.form.select_iu.btn_back, self.menu_iu)
        self.exam_iu_pe_select.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_iu)
        self.menu_iu.addTransition(self.form.mnu_iu.btn_IU_DP_tune.clicked, self.exam_iu_dp_select)
        self.exam_iu_dp_select.addTransition(self.form.select_iu.btn_ok, self.exam_iu_dp)
        self.exam_iu_dp_select.addTransition(self.form.select_iu.btn_back, self.menu_iu)
        self.exam_iu_dp_select.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_iu)
        self.exam_iu_pe.addTransition(self.exam_iu_pe.finished, self.menu_iu)
        self.exam_iu_dp.addTransition(self.exam_iu_dp.finished, self.menu_iu)
        self.menu_iu.addTransition(self.form.mnu_iu.btn_IU_exam.clicked, self.exam_iu_auth)
        self.exam_iu_auth.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_iu)
        self.exam_iu_auth.addTransition(self.form.auth.btn_back, self.menu_iu)
        self.exam_iu_auth.addTransition(self.form.auth.btn_ok, self.exam_iu_select)
        self.exam_iu_select.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_iu)
        self.exam_iu_select.addTransition(self.form.select_iu.btn_back, self.menu_iu)
        self.exam_iu_select.addTransition(self.form.select_iu.btn_ok, self.exam_iu)
        self.exam_iu.addTransition(self.exam_iu.finished, self.menu_iu)

        self.menu_main.addTransition(self.form.mnu_main.btnBU.clicked, self.menu_bu)
        self.menu_bu.addTransition(self.form.mnu_bu.btn_bu_back.clicked, self.menu_main)
        self.menu_bu.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_main)
        self.menu_bu.addTransition(self.form.mnu_bu.btn_bu_exam.clicked, self.exam_bu_auth)
        self.exam_bu_auth.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_bu)
        self.exam_bu_auth.addTransition(self.form.auth.btn_back, self.menu_bu)
        self.exam_bu_auth.addTransition(self.form.auth.btn_ok, self.exam_bu_select)
        self.exam_bu_select.addTransition(self.form.btnPanel.btnBack.clicked, self.menu_bu)
        self.exam_bu_select.addTransition(self.form.select_bu.btn_back, self.menu_bu)
        self.exam_bu_select.addTransition(self.form.select_bu.btn_ok, self.check_bu)

        self.opc.started.connect(self.stm.start)
        self.opc.start()

    def closeEvent(self, QEvent):
        self.form.hide()
        main.stm.stop()
        self.opc.stop()
        QEvent.accept()


class StateInit(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        print('stm started')
        com.opc.ai.setActive(False)
        com.opc.di.setActive(True)
        com.opc.ao.setActive(False)
        com.opc.do1.setActive(False)
        com.opc.do1.setActive(False)
        com.opc.pv1.setActive(False)
        com.opc.pv2.setActive(False)
        com.opc.pa1.setActive(False)
        com.opc.pa2.setActive(False)
        com.opc.pa3.setActive(False)

        com.form.mnu_main.reset()
        com.form.mnu_iu.reset()
        com.success.emit()


class MenuMain(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.mnu_main


class MenuIU(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.mnu_iu
        com.form.mnu_iu.reset()


class MenuBU(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.mnu_bu
        com.form.mnu_bu.reset()


class ExamIUPESelect(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.select_iu
        com.form.currentmenu.reset()


class ExamIUDPSelect(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.select_iu
        com.form.currentmenu.reset()


class ExamIUAuth(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.auth
        com.form.currentmenu.reset()


class ExamBUAuth(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.auth
        com.form.currentmenu.reset()


class ExamIUSelect(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.select_iu
        com.form.currentmenu.reset()


class ExamBUSelect(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.select_bu
        com.form.currentmenu.reset()
        com.form.check_bu.reset()


class CheckBU(QtCore.QState):
    def onEntry(self, QEvent):
        com.form.currentmenu = com.form.check_bu


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    print('Старт')

    app.exec_()
