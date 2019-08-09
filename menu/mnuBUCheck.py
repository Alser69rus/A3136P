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
        self.btn_shim = Btn('Проверка ШИМ силового канала')
        self.btn_ai = Btn('Проверка аналоговых входов')
        self.btn_rt = Btn('Проверка канала измерения температуры')

        self.btn_di_r = Btn('Проверка резервного канала дискретных входов')
        self.btn_fi1_r = Btn('Проверка резервного канала ДЧД')
        self.btn_power_r = Btn('Проверка резервного канала ШИМ')

        self.btn_bu_back = Btn('Завершение испытаний')

        lst = [self.btn_prepare, self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai, self.btn_rt,
               self.btn_di_r, self.btn_fi1_r, self.btn_power_r, self.btn_bu_back]
        self.set_lst(lst)

        self.btn_bu_back.clicked.connect(self.btn_back)

    def reset(self):
        super().reset()
        self.set_btn_visible()

    def set_btn_visible(self):
        vis = []

        if self.dev_type == 'ЭРЧМ30Т3-06':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai, self.btn_rt]
        elif self.dev_type == 'ЭРЧМ30Т3-07':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai, self.btn_rt]
        elif self.dev_type == 'ЭРЧМ30Т3-04':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai, self.btn_rt]
        elif self.dev_type == 'ЭРЧМ30Т3-08':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-08-01':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-02':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-05':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-10':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-10-01':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-12':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-12-01':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-12-02':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т3-12-03':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т4-01':
            vis = [self.btn_di, self.btn_fi, self.btn_shim]
        elif self.dev_type == 'ЭРЧМ30Т4-02':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т4-02-01':
            vis = [self.btn_di, self.btn_fi, self.btn_shim, self.btn_ai]
        elif self.dev_type == 'ЭРЧМ30Т4-03':
            vis = [self.btn_di, self.btn_fi, self.btn_shim]

        for elem in self.list:
            if elem != self.btn_bu_back and elem != self.btn_prepare:
                elem.setEnabled(False)
                if elem in vis:
                    elem.setVisible(True)
                else:
                    elem.setVisible(False)
