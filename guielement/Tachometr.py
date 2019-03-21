from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import pyqtSlot as pyqtSlot

try:
    import guielement.scale as scale
except Exception:
    import scale as scale


class Tachometr600(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.caption = QtWidgets.QLabel('Тахометр')
        self.caption.setFont(QtGui.QFont('Segoi UI', 20))
        self.text = QtWidgets.QLabel('0 об/мин')
        self.vbox.addWidget(self.caption)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.text)
        self.setLayout(self.vbox)
        self.text.setFont(QtGui.QFont('Segoi UI', 24))
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.scale = scale.Scale(250, 250, 180, 180, 90, 0, 600, 6, 2, 5, '{:3.0f}')
        self.arrow = scale.Arrow(250, 250, 178, 178)
        self.arrow_green = scale.Arrow(250, 250, 178, 20)
        self.red_pen = QtGui.QPen(QtCore.Qt.red)
        self.red_brush = QtGui.QBrush(QtCore.Qt.red)
        self.green_pen = QtGui.QPen(QtCore.Qt.green)
        self.green_brush = QtGui.QBrush(QtCore.Qt.transparent)
        self.setFont(QtGui.QFont('Segoi UI', 16))

        self.task_value = 0
        self.value = 0
        self.angle = 180
        self.task_angle = 180

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
        self.angle = 180 - 90 * value / 600
        self.text.setText('{:>3.0f} об/мин'.format(value))
        self.update()

    @pyqtSlot(float)
    def setTask(self, value):
        self.task_value = value
        self.task_angle = 180 - 90 * value / 600
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Tachometr600()
    win.setValue(320)

    win.show()

    app.exec_()
