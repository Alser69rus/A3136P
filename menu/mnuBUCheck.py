from PyQt5 import QtCore, QtWidgets
from menu.template import Menu
from menu.btn import Btn


class CheckBU(Menu):
    btn_back = QtCore.pyqtSignal()
    btn_ok = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__('Проверка блока управления', parent, col=2)
        self.dev_type = ''

        self.btn_prepare = Btn('Подготовка')
        self.btn_di = Btn('Проверка дискретных входов')
        self.btn_fi = Btn('Проверка частотных входов')
        self.btn_power = Btn('Проверка ШИМ силового канала')
        self.btn_ai1 = Btn('Проверка канала АВХ1 - ДДН')
        self.btn_ai2 = Btn('Проверка канала АВХ2 - ДДМ')
        self.btn_ai3 = Btn('Проверка канала АВХ3 - ДТ')
        self.btn_di_r = Btn('Проверка резервного канала дискретных входов')
        self.btn_fi1_r = Btn('Проверка резервного канала ДЧД')
        self.btn_power_r = Btn('Проверка резервного канала ШИМ')

        self.btn_bu_back = Btn('Завершение испытаний')

        lst = [self.btn_prepare, self.btn_di, self.btn_fi, self.btn_power, self.btn_ai1,
               self.btn_ai2, self.btn_ai3, self.btn_di_r, self.btn_fi1_r, self.btn_power_r, self.btn_bu_back]
        self.set_lst(lst)

        self.btn_bu_back.clicked.connect(self.btn_back)
        for e in lst:
            e.clicked.connect(self.on_select)

    def reset(self):
        super().reset()
        vis = []
        if self.dev_type == 'ЭРЧМ30T3-06':
            vis = [self.btn_di, self.btn_fi, self.btn_power, self.btn_ai1,
                   self.btn_ai2, self.btn_ai3, self.btn_di_r, self.btn_fi1_r, self.btn_power_r]
        elif self.dev_type == 'ЭРЧМ30Т3-07':
            vis = [self.btn_di, self.btn_fi, self.btn_power, self.btn_ai1,
                   self.btn_ai2, self.btn_ai3]
        elif self.dev_type == 'ЭРЧМ30Т3-04':
            vis = [self.btn_di, self.btn_fi, self.btn_power, self.btn_ai1,
                   self.btn_ai2, self.btn_ai3]

        for elem in self.list:
            if elem != self.btn_bu_back and elem != self.btn_prepare:
                elem.setEnabled(False)
                if elem in vis:
                    elem.setVisible(True)
                else:
                    elem.setVisible(False)

    def on_select(self):
        self.btn_ok.emit(self.sender().text())
