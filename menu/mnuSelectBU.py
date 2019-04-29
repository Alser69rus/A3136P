from PyQt5 import QtCore, QtWidgets
from menu.template import Menu
from menu.btn import Btn


class SelectBU(Menu):
    btn_back = QtCore.pyqtSignal()
    btn_ok = QtCore.pyqtSignal()

    def __init__(self, parent=None, form=None):
        super().__init__('Выбор типа блока управления', parent, col=3)
        self.dev_type = ''
        self.form = form

        self.btn_bu_3_06 = Btn('30T3-06')
        self.btn_bu_3_07 = Btn('30Т3-07')
        self.btn_bu_3_04 = Btn('30Т3-04')

        self.btn_bu_back = Btn('Назад')

        lst = [self.btn_bu_3_04, self.btn_bu_3_06, self.btn_bu_3_07]
        for dev in lst:
            dev.clicked.connect(self.on_select)
        lst.append(self.btn_bu_back)
        self.set_lst(lst)

        self.btn_bu_back.clicked.connect(self.btn_back)

    @QtCore.pyqtSlot()
    def on_select(self):
        self.dev_type = self.sender().text()
        frm = self.form
        vis = []
        if self.dev_type == '30T3-06':

            vis = [frm.btn_di, frm.btn_fi1, frm.btn_f12, frm.btn_fi3, frm.btn_power, frm.btn_ai1,
                   frm.btn_ai2, frm.btn_ai3, frm.btn_di_r, frm.btn_fi1_r, frm.btn_power_r]

        elif self.dev_type == '30Т3-07':
            vis = [frm.btn_di, frm.btn_fi1, frm.btn_f12, frm.btn_fi3, frm.btn_power, frm.btn_ai1,
                   frm.btn_ai2, frm.btn_ai3]
        elif self.dev_type == '30Т3-04':
            vis = [frm.btn_di, frm.btn_fi1, frm.btn_f12, frm.btn_fi3, frm.btn_power, frm.btn_ai1,
                   frm.btn_ai2, frm.btn_ai3]

        for elem in frm.list:
            if elem != frm.btn_bu_back and elem != frm.btn_prepare:
                elem.setEnabled(False)
                if elem in vis:
                    elem.setVisible(True)
                else:
                    elem.setVisible(False)

        self.btn_ok.emit()
