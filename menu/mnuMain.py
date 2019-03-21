from PyQt5 import QtWidgets

try:
    from . import template, btn
except Exception:
    import aseMenu, btn


class MainMenu(template.Menu):
    def __init__(self, parent=None):
        super().__init__('Главное меню', parent)

        self.btnBU = btn.Btn('Проверка блока управления')
        self.btnIU = btn.Btn('Проверка исполнительного устройства')
        self.btnBP = btn.Btn('Проверка блока питания')
        self.btnDT = btn.Btn('Проверка датчиков')
        self.btnSettings = btn.Btn('Настройки')
        self.btnQuit = btn.Btn('Выход')

        self.set_lst([self.btnBU, self.btnIU, self.btnBP, self.btnDT, self.btnSettings, self.btnQuit])


