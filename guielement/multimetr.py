from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot as pyqtSlot

try:
    import guielement.scale as scale
except Exception:
    import scale as scale


class PA3(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()
        self.caption = QtWidgets.QLabel('PA3')
        self.caption.setFont(QtGui.QFont('Segoi UI', 24))
        self.text = QtWidgets.QLabel('0 А')
        self.vbox.addWidget(self.caption)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.text)
        self.setLayout(self.vbox)
        self.text.setFont(QtGui.QFont('Segoi UI', 24))
        self.text.setAlignment(QtCore.Qt.AlignRight)

        self.scale = scale.Scale(180, 155, 90, 270, -22.5, 0, 2.6, 13, 2, 5, '{: >.1f}')
        self.arrow = scale.Arrow(180, 155, 88,88)

        self.red_pen = QtGui.QPen(QtCore.Qt.red)
        self.red_brush = QtGui.QBrush(QtCore.Qt.red)
        self.setFont(QtGui.QFont('Segoi UI', 16))

        self.value = 0
        self.angle = 270

        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.resize(380, 320)
        self.setMinimumSize(380, 320)

    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
        self.scale.drawScale(painter)
        self.scale.drawVal(painter)
        painter.setPen(self.red_pen)
        painter.setBrush(self.red_brush)
        self.arrow.drawArrow(painter, self.angle)

    @pyqtSlot(float)
    def setValue(self, value):
        self.value = value
        self.angle = 270 - 292.5 * value / 2.6
        self.text.setText('{:>5.3f} А'.format(value))
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = PA3()
    win.setValue(0.85)

    win.show()

    app.exec_()
