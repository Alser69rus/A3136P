from PyQt5 import QtWidgets

try:
    from . import template, btn
except Exception:
    import aseMenu, btn


class mnuIU(template.Menu):
    def __init__(self, parent=None):
        super().__init__('Проверка исполнительного устройства', parent)

        self.btn_IU_exam = btn.Btn('Проверка исполнительного устройства')
        self.btn_IU_PE_tune = btn.Btn('Регулировка поворотного электромагнита')
        self.btn_IU_DP_tune = btn.Btn('Регулировка датчика положения')
        self.btn_IU_back = btn.Btn('Назад')

        self.set_lst([self.btn_IU_exam, self.btn_IU_PE_tune, self.btn_IU_DP_tune, self.btn_IU_back])


