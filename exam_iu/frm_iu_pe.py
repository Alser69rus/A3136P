from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot as pyqtSlot

import guielement.Tachometr
import guielement.multimetr
import guielement.indicator


class Form_iu_pe_set_pe(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        # self.pixmap = QtGui.QPixmap('img_iu1.png')
        self.pixmap = QtGui.QPixmap('exam_iu\\img_iu1.png')
        self.pixmap.setDevicePixelRatio(1.05)
        self.text = QtWidgets.QLabel(
            'Установка поворотного электромагнита на исполнительное устройство:\n' + \
            ' а) снять верхнюю крышку 4 исполнительного устройства\n' + \
            ' б) перед установкой поворотного электромагнита проверить угол a\n' + \
            '    между рычагами 18 и 32, он должен составлять 60°, при необходимости\n' + \
            '    отрегулировать поворотом рычага 18\n' + \
            'в) расстояние L от рычага 18 до привалочной плоскости должно составлять\n' + \
            '   19±0,5 мм\n' + \
            'г) установить поворотный электромагнит 9 на верхнем корпусе исполнительного\n' + \
            '   устройства и закрепить его. Закрепить свободный конец пружины 31 на\n' + \
            '   упорном рычаге 27.' + \
            '\n\nНажать кнопку ПРИНЯТЬ для продолжения')
        self.text.setFont(QtGui.QFont('Segoi UI', 13))
        self.text.setWordWrap(True)
        self.lbl = QtWidgets.QLabel()
        self.lbl.setPixmap(self.pixmap)
        self.vbox.addWidget(self.lbl)
        self.vbox.addWidget(self.text)
        self.vbox.addStretch(1)
        self.setLayout(self.vbox)


class Form_iu_inst1(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.text = QtWidgets.QLabel()
        self.img = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap('exam_iu\\inst1.png')
        self.img.setScaledContents(True)
        self.pixmap.setDevicePixelRatio(1.05)
        self.img.setPixmap(self.pixmap)
        self.table = QtWidgets.QWidget()
        self.table.setLayout(self.hbox)
        self.hbox.addWidget(self.text)
        self.hbox.addSpacing(20)
        self.hbox.addWidget(self.img)
        self.hbox.addStretch(1)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.table)
        self.vbox.addStretch(1)
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setWordWrap(True)
        self.text.setText('Установка исполнительного устройства на привод стенда:\n' + \
                          'а) Установить на вал привода подходящую муфту (рис. 1)\n' + \
                          'б) Установить исполительное устройство и зафиксируйте его\n' + \
                          '   при помощи болтов (рис. 2)\n'
                          'в) Проверьте отчутствие перекосов при помощи поворота вала\n' + \
                          '   за шестерню. При необходимости устраните перекос (рис. 3)' + \
                          '\n\nНажать кнопку ПРИНЯТЬ для продолжения')
        self.text.setAlignment(QtCore.Qt.AlignTop)


class Form_iu_inst2(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.text = QtWidgets.QLabel()
        self.img = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap('exam_iu\\inst2.png')
        self.img.setScaledContents(True)
        self.pixmap.setDevicePixelRatio(1.05)
        self.img.setPixmap(self.pixmap)
        self.table = QtWidgets.QWidget()
        self.table.setLayout(self.hbox)
        self.hbox.addWidget(self.text)
        self.hbox.addSpacing(20)
        self.hbox.addWidget(self.img)
        self.hbox.addStretch(1)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.table)
        self.vbox.addStretch(1)
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setText('Установка датчика давления на исполнительное устройство:\n' + \
                          'а) Со стороны силового вала, противоположной стороне стрелочного\n' + \
                          '   указателя снимите кронштейн и выкрутите пробку\n   аккумулятора (рис. 4)\n' + \
                          'б) В отверстие аккумулятора ввинтите штуцер, а затем датчик давления.\n' + \
                          '   После чего подключите датчик к разъему шлейфа (рис. 5)\n'
                          'в) Второй конец шлейфа должен быть подключен к разъему\n' + \
                          '   ХР21 ДАТЧИК ДАВЛЕНИЯ (рис. 6)' + \
                          '\n\nНажать кнопку ПРИНЯТЬ для продолжения')
        self.text.setWordWrap(True)
        self.text.setAlignment(QtCore.Qt.AlignTop)


class Form_iu_inst3(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.text = QtWidgets.QLabel()
        self.img = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap('exam_iu\\inst3.png')
        self.img.setScaledContents(True)
        # self.pixmap.setDevicePixelRatio(1.05)
        self.img.setPixmap(self.pixmap)
        self.table = QtWidgets.QWidget()
        self.table.setLayout(self.hbox)
        self.hbox.addWidget(self.text)
        self.hbox.addSpacing(20)
        self.hbox.addWidget(self.img)
        self.hbox.addStretch(1)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.table)
        self.vbox.addStretch(1)
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setWordWrap(True)
        self.text.setText('Установка датчика угла поворота на исполнительное устройство:\n' + \
                          'а) Снимете с силового вала рычаг, ослабив крепежный болт (рис. 7).\n' + \
                          'б) На кронштейне датчика угла поворота ослабьте барашки (рис.8)\n' + \
                          'в) Установите на вал исполнительного устройства резиновую муфту '
                          'и присоедините датчик угла поворота, по возможности соосно с валом (рис. 9). ' + \
                          'После чего зафиксируйте положение кронштейна затянув барашки.\n' + \
                          'г) Разъем датчика подключите к разъему привода ХР17 ДАТЧИК УГЛА' + \
                          '\n\nНажать кнопку ПРИНЯТЬ для продолжения')
        self.text.setAlignment(QtCore.Qt.AlignTop)


class Form_iu_inst4(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.text = QtWidgets.QLabel()
        self.img = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap('exam_iu\\inst4.png')
        self.img.setScaledContents(True)
        # self.pixmap.setDevicePixelRatio(1.05)
        self.img.setPixmap(self.pixmap)
        self.table = QtWidgets.QWidget()
        self.table.setLayout(self.hbox)
        self.hbox.addWidget(self.text)
        self.hbox.addSpacing(20)
        self.hbox.addWidget(self.img)
        self.hbox.addStretch(1)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.table)
        self.vbox.addStretch(1)
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setWordWrap(True)
        self.text.setText('Подключение поворотного электромагнита и датчика положения:\n' + \
                          'а) Датчик положения подключается к разъему ХР9 ИУ ДП.\n' + \
                          'б) Поворотный электромагнит подключается к разъему XS10 ИУ ПЭ\n' + \
                          'при этом в зависимости от конструкции он либо подключается при помощи '
                          'шлейфа с разъемами (рис.12 и рис. 13) или при помощи шлейфа с зажимами (пара одноцветных х3 х4)' + \
                          '\n\nНажать кнопку ПРИНЯТЬ для продолжения')
        self.text.setAlignment(QtCore.Qt.AlignTop)


class Form_iu_pe_check(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.text = QtWidgets.QLabel()
        self.pa3 = guielement.multimetr.PA3()
        self.tachometr = guielement.Tachometr.Tachometr600()
        self.indicator = guielement.indicator.Indicator()
        self.panel = QtWidgets.QWidget()

        self.hbox.addWidget(self.pa3)
        self.hbox.addWidget(self.tachometr)
        self.hbox.addWidget(self.indicator)
        self.panel.setLayout(self.hbox)

        self.vbox.addWidget(self.panel)
        self.vbox.addWidget(self.text)
        self.setLayout(self.vbox)

        self.panel.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Fixed)


        self.text.setFont(QtGui.QFont('Segoi UI', 16))
        self.text.setWordWrap(True)
        self.text.setText('Запуск вращения вала ИУ на скорости 500 об/мин\n')
        self.text.setAlignment(QtCore.Qt.AlignTop)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Form_iu_pe_check()
    win.show()
    print(win.width(),win.height())
    app.exec_()
