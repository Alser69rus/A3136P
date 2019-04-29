from PyQt5 import QtCore, QtWidgets
from menu.template import Menu
from menu.btn import Btn


class CheckBU(Menu):
    btn_back = QtCore.pyqtSignal()
    btn_ok = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__('Проверка блока управления', parent, col=2)

        self.btn_prepare = Btn('Подготовка')
        self.btn_di = Btn('Проверка дискретных входов')
        self.btn_fi1 = Btn('Проверка канала ЧВХ1 - ДЧД')
        self.btn_f12 = Btn('Проверка канала ЧВХ2 - ДЧТК')
        self.btn_fi3 = Btn('Проверка канала ЧВХ3- ДП')
        self.btn_power = Btn('Проверка ШИМ силового канала')
        self.btn_ai1 = Btn('Проверка канала АВХ1 - ДДН')
        self.btn_ai2 = Btn('Проверка канала АВХ2 - ДДМ')
        self.btn_ai3 = Btn('Проверка канала АВХ3 - ДТ')
        self.btn_di_r = Btn('Проверка резервного канала дискретных входов')
        self.btn_fi1_r = Btn('Проверка резервного канала ДЧД')
        self.btn_power_r = Btn('Проверка резервного канала ШИМ')

        self.btn_bu_back = Btn('Завершение испытаний')

        lst = [self.btn_prepare, self.btn_di, self.btn_fi1, self.btn_f12, self.btn_fi3, self.btn_power, self.btn_ai1,
               self.btn_ai2, self.btn_ai3, self.btn_di_r, self.btn_fi1_r, self.btn_power_r, self.btn_bu_back]
        self.set_lst(lst)

        self.btn_bu_back.clicked.connect(self.btn_back)
