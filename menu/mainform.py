from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

import menu.btnPanel as btnPanel
import menu.mnuMain as mnumain
import menu.mnuUI as mnuui
import exam_iu.frm_iu_pe


class MainForm(QtWidgets.QWidget):
    def __init__(self, server=None, parent=None):
        super().__init__(parent)
        self.server = server
        self.vbox = QtWidgets.QVBoxLayout()
        self.setWindowTitle('А3136. Стенд проверки и регулировки ЭРЧМ')
        self.resize(1024, 768)
        self.table = QtWidgets.QWidget()
        self.btnPanel = btnPanel.BtnPanel()
        self.statusbar = QtWidgets.QStatusBar()
        self.btnPanel.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.statusbar.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.vbox.addWidget(self.table)
        self.vbox.addWidget(self.btnPanel)
        self.vbox.addWidget(self.statusbar)
        self.setLayout(self.vbox)

        self.mnu_main = mnumain.MainMenu()
        self.mnu_UI = mnuui.mnuUI()

        self.exam_iu_pe_set_pe = exam_iu.frm_iu_pe.Form_iu_pe_set_pe()
        self.exam_iu_pe_inst1 = exam_iu.frm_iu_pe.Form_iu_inst1()
        self.exam_iu_pe_inst2 = exam_iu.frm_iu_pe.Form_iu_inst2()
        self.exam_iu_pe_inst3 = exam_iu.frm_iu_pe.Form_iu_inst3()
        self.exam_iu_pe_inst4 = exam_iu.frm_iu_pe.Form_iu_inst4()
        self.exam_iu_pe_check = exam_iu.frm_iu_pe.Form_iu_pe_check()

        self.stl = QtWidgets.QStackedLayout()
        self.stl.addWidget(self.mnu_main)
        self.stl.addWidget(self.mnu_UI)
        self.stl.addWidget(self.exam_iu_pe_set_pe)
        self.stl.addWidget(self.exam_iu_pe_inst1)
        self.stl.addWidget(self.exam_iu_pe_inst2)
        self.stl.addWidget(self.exam_iu_pe_inst3)
        self.stl.addWidget(self.exam_iu_pe_inst4)
        self.stl.addWidget(self.exam_iu_pe_check)

        self.table.setLayout(self.stl)
        self._currentmenu = None


    @pyqtSlot(str)
    def on_statusbar_update(self, msg):
        self.statusbar.showMessage(msg)

    @property
    def currentmenu(self):
        return self._currentmenu

    @currentmenu.setter
    def currentmenu(self, value):
        if self.currentmenu:
            self.disconnectmenu()
        self._currentmenu = value
        self.stl.setCurrentWidget(value)
        self.connectmenu()

    def connectmenu(self):
        self.currentmenu.encoder_value = self.server.br3.value
        self.btnPanel.btnUp.clicked.connect(self.currentmenu.on_btn_up_clicked)
        self.btnPanel.btnDown.clicked.connect(self.currentmenu.on_btn_down_clicked)
        self.btnPanel.btnBack.clicked.connect(self.currentmenu.on_btn_back_clicked)
        self.btnPanel.btnOk.clicked.connect(self.currentmenu.on_btn_ok_clicked)
        if self.server:
            self.server.br3.updated.connect(self.currentmenu.on_encoder,QtCore.Qt.QueuedConnection)

    def disconnectmenu(self):
        self.btnPanel.btnUp.clicked.disconnect(self.currentmenu.on_btn_up_clicked)
        self.btnPanel.btnDown.clicked.disconnect(self.currentmenu.on_btn_down_clicked)
        self.btnPanel.btnBack.clicked.disconnect(self.currentmenu.on_btn_back_clicked)
        self.btnPanel.btnOk.clicked.disconnect(self.currentmenu.on_btn_ok_clicked)
        if self.server:
            self.server.br3.updated.disconnect()
