from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot as pyqtSlot
try:
    import guielement.scale as scale
except Exception:
    import scale as scale


class Indicator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.caption = QtWidgets.QLabel('Указатель\nсилового вала')
        self.caption.setFont(QtGui.QFont('Segoi UI', 20))
        self.text = QtWidgets.QLabel('Позиция 0.0')
        self.vbox.addWidget(self.caption)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.text)
        self.setLayout(self.vbox)
        self.text.setFont(QtGui.QFont('Segoi UI', 24))
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.scale = scale.Scale(130, 500, 350, 106, 74, 0, 10, 10, 2, 1, '{:.0f}')
        self.arrow = scale.Arrow(130, 500, 350, 40)
        self.arrow_green = scale.Arrow(130, 500, 350, 20)
        self.red_pen = QtGui.QPen(QtCore.Qt.red)
        self.red_brush = QtGui.QBrush(QtCore.Qt.red)
        self.green_pen = QtGui.QPen(QtCore.Qt.green)
        self.green_brush = QtGui.QBrush(QtCore.Qt.transparent)
        self.setFont(QtGui.QFont('Segoi UI', 16))

        self.task_value = 0
        self.value = 0
        self.angle = 106
        self.task_angle = 106

        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.resize(280, 320)
        self.setMinimumSize(280, 320)

    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
        self.scale.drawScale(painter)
        self.scale.drawVal(painter)
        painter.setPen(self.green_pen)
        painter.setBrush(self.green_brush)
        self.arrow_green.drawArrow(painter, self.task_angle)
        painter.setPen(self.red_pen)
        painter.setBrush(self.red_brush)
        self.arrow.drawArrow(painter, self.angle)

    @pyqtSlot(float)
    def setValue(self, value):
        self.value = value
        self.angle = 106 - 32 * value / 10
        self.text.setText('Позиция: {:>3.1f}'.format(value))
        # self.repaint()

    @pyqtSlot(float)
    def setTask(self, value):
        self.task_value = value
        self.task_angle = 106 - 32 * value / 10
        # self.repaint()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Indicator()
    win.setValue(1.5)
    win.setTask(3)

    win.show()

    app.exec_()