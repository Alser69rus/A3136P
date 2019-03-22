import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QState as QState

import time
import opc.opc
import menu.mainform
import exam_iu.exam_iu_pe


class Trans(QtCore.QSignalTransition):
    def __init__(self, signal, value, state):
        super().__init__(signal)
        self.setTargetState(state)
        self.value = value

    def eventTest(self, QEvent):
        if not super().eventTest(QEvent): return False
        return QEvent.arguments()[0] == self.value


class Main(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.server = opc.opc.Server()
        self.thread1 = QtCore.QThread()
        self.server.moveToThread(self.thread1)
        self.thread1.started.connect(self.server.run)
        self.server.c.finished.connect(self.thread1.quit, QtCore.Qt.DirectConnection)
        self.server.c.finished.connect(self.server.deleteLater)
        self.server.c.finished.connect(self.thread1.deleteLater)

        self.form = menu.mainform.MainForm(self.server)
        self.form.showMaximized()

        self.exam_iu_pe = exam_iu.exam_iu_pe.Exam_iu_pe(self.server, self.form)

        self.stm = QtCore.QStateMachine()

        self.st_init = QState(self.stm)
        self.st_menu = QState(self.stm)
        self.st_close = QtCore.QFinalState(self.stm)
        self.st_exam_iu_pe = self.exam_iu_pe.state
        self.stm.addState(self.st_exam_iu_pe)

        self.stm.setInitialState(self.st_init)

        self.st_menu_main = QtCore.QState(self.st_menu)
        self.st_menu_UI = QtCore.QState(self.st_menu)
        self.st_menu.setInitialState(self.st_menu_main)

        self.st_init.addTransition(Trans(self.signal, 'main menu', self.st_menu))
        self.st_menu_main.addTransition(self.form.mnu_main.btnIU.clicked, self.st_menu_UI)
        self.st_menu_UI.addTransition(self.form.mnu_UI.btn_IU_back.clicked, self.st_menu_main)
        self.st_menu_UI.addTransition(self.form.btnPanel.btnBack.clicked, self.st_menu_main)
        self.st_menu_UI.addTransition(self.form.mnu_UI.btn_IU_PE_tune.clicked, self.st_exam_iu_pe)
        self.st_exam_iu_pe.addTransition(self.st_exam_iu_pe.finished, self.st_menu_UI)

        self.st_init.onEntry = self.on_st_init_entry
        self.st_menu_main.onEntry = self.on_st_menu_main_entry
        self.st_menu_UI.onEntry = self.on_st_menu_iu_entry
        self.server.c.started.connect(self.stm.start)
        self.thread1.start()

    def on_st_init_entry(self, e):
        self.server.btnUp.clicked.connect(self.form.btnPanel.on_up_clicked)
        self.server.btnDown.clicked.connect(self.form.btnPanel.on_down_clicked)
        self.server.btnOk.clicked.connect(self.form.btnPanel.on_ok_clicked)
        self.server.btnBack.clicked.connect(self.form.btnPanel.on_back_clicked)
        self.form.closeEvent = self.closeEvent
        self.form.mnu_main.btnQuit.clicked.connect(self.form.close)
        if self.server:
            self.server.c.updated_quality.connect(self.form.on_statusbar_update)
        self.signal.emit('main menu')

    def on_st_menu_main_entry(self, e):
        self.form.currentmenu = self.form.mnu_main

    def on_st_menu_iu_entry(self, e):
        self.form.mnu_UI.reset()
        self.form.currentmenu = self.form.mnu_UI

    def closeEvent(self, event):
        # form.hide()
        main.stm.stop()

        if self.server and self.server.running:
            self.server.running = False
        if self.thread1.isRunning():
            self.thread1.wait(5000)

        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    print('Старт')

    app.exec_()
