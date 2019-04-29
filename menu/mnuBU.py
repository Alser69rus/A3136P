from menu.template import Menu
from menu.btn import Btn


class MnuBU(Menu):
    def __init__(self, parent=None):
        super().__init__('Проверка блока управления', parent)

        self.btn_bu_exam = Btn('Проверка блока управления при помощи программатора')
        self.btn_bu_back = Btn('Назад')

        self.set_lst([self.btn_bu_exam, self.btn_bu_back])
