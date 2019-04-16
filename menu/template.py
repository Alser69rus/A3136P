from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
import time

try:
    from . import btn, caption
except Exception:
    import btn, caption


class Menu(QtWidgets.QWidget):
    def __init__(self, title='', parent=None, col=1):
        super().__init__(parent)
        self.col = col
        self.bigbox = QtWidgets.QVBoxLayout()
        self.vbox = QtWidgets.QGridLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.table = QtWidgets.QWidget()
        self.btnArea = QtWidgets.QWidget()

        self.caption = caption.Caption(title)
        self.selected = None
        self.list = []

        self.bigbox.addWidget(self.caption)
        self.bigbox.addSpacing(40)
        self.bigbox.addWidget(self.table)
        self.bigbox.addStretch(1)
        self.setLayout(self.bigbox)

        self.table.setLayout(self.hbox)
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.btnArea)
        self.hbox.addStretch(1)
        self.btnArea.setLayout(self.vbox)

        self.encoder_value = 0

    def set_lst(self, lst):
        self.list = lst[:]
        i = 0

        for elem in lst:
            self.vbox.addWidget(elem, i // self.col, i % self.col)
            elem.mouse_entry.connect(self.on_btn_select)
            i += 1

        self.reset()

    def reset(self):
        for elem in self.list:
            elem.state = 'normal'
            elem.selected = False

        if self.list:
            self.selected = self.list[0]
            self.selected.selected = True

    @pyqtSlot()
    def on_btn_select(self):
        self.select(self.sender())

    def select(self, element):
        if self.selected:
            self.selected.selected = False
        self.selected = element
        self.selected.selected = True

    @pyqtSlot()
    def on_btn_back_clicked(self):
        pass

    @pyqtSlot()
    def on_btn_up_clicked(self):
        self.select(self.previous_element())

    @pyqtSlot()
    def on_btn_down_clicked(self):
        self.select(self.next_element())

    @pyqtSlot()
    def on_btn_ok_clicked(self):
        if self.selected:
            self.selected.animateClick()

    @pyqtSlot(float)
    def on_encoder(self, value):
        if value - self.encoder_value > 5:
            self.encoder_value = value
            self.on_btn_down_clicked()
        if value - self.encoder_value < -5:
            self.encoder_value = value
            self.on_btn_up_clicked()

    def next_element(self):
        if not self.list: return None
        if not self.selected: return self.list[0]
        i = self.list.index(self.selected)
        while True:
            i += 1
            if i >= len(self.list): i = 0
            if self.list[i].isVisible() and self.list[i].isEnabled():
                return self.list[i]

    def previous_element(self):
        if not self.list: return None
        if not self.selected: return self.list[0]
        i = self.list.index(self.selected)
        while True:
            i -= 1
            if i < 0: i = len(self.list) - 1
            if self.list[i].isVisible() and self.list[i].isEnabled():
                return self.list[i]
