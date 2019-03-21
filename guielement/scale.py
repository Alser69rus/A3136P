from PyQt5 import QtWidgets, QtCore, QtGui


class Scale:
    def __init__(self, x, y, r, startA=180, finishA=0, startV=0, finishV=1, prim=10, sec=2, ter=1, f_str='{}'):
        super().__init__()
        self.x = x
        self.y = y
        self.r = r
        self.startA = startA
        self.startV = startV
        self.finishA = finishA
        self.finishV = finishV
        self.prim = prim
        self.linewidth = 1
        self.sec = sec
        self.ter = ter
        self.f_str = f_str

    def drawScale(self, painter: QtGui.QPainter):
        count = self.prim * self.sec * self.ter
        da = (self.finishA - self.startA) / count

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.translate(self.x, self.y)
        painter.rotate(-self.startA)

        for i in range(count + 1):
            if not i % (self.sec * self.ter):
                self.drawPrimary(painter)
            elif not i % (self.ter):
                self.drawSecondary(painter)
            else:
                self.drawTertiary(painter)

            painter.rotate(-da)
        painter.restore()

    def drawPrimary(self, painter: QtGui.QPainter):
        h = QtGui.QFontMetrics(painter.font()).height()
        pen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.black)), self.linewidth)
        pen2 = QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.black)), 3 * self.linewidth)
        painter.setPen(pen)
        painter.drawLine(self.r, 0, self.r + h, 0)
        painter.setPen(pen2)
        painter.drawLine(self.r + h * 0.67, 0, self.r + h, 0)

    def drawSecondary(self, painter: QtGui.QPainter):
        h = QtGui.QFontMetrics(painter.font()).height()
        pen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.black)), self.linewidth)
        painter.setPen(pen)
        painter.drawLine(self.r, 0, self.r + h * 0.67, 0)

    def drawTertiary(self, painter: QtGui.QPainter):
        h = QtGui.QFontMetrics(painter.font()).height()
        pen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.black)), self.linewidth)
        painter.setPen(pen)
        painter.drawLine(self.r, 0, self.r + h * 0.33, 0)

    def drawVal(self, painter: QtGui.QPainter):
        count = self.prim
        da = (self.finishA - self.startA) / count
        dv = (self.finishV - self.startV) / count
        w = QtGui.QFontMetrics(painter.font()).width(self.f_str.format(self.finishV))
        for i in range(count+1):
            v = self.startV + i * dv
            w=max(w,QtGui.QFontMetrics(painter.font()).width(self.f_str.format(v)))

        h = QtGui.QFontMetrics(painter.font()).height()

        for i in range(count + 1):
            painter.save()
            painter.translate(self.x, self.y)
            a = -self.startA - da * i
            painter.rotate(a)
            v = self.startV + i * dv
            l = self.r + self.linewidth + h + 4 + w / 2
            painter.translate(l, 0)
            painter.rotate(-a)
            painter.drawText(-w / 2, -h / 2, w, h, QtCore.Qt.AlignCenter, self.f_str.format(v))
            painter.restore()


class Arrow:
    def __init__(self, x, y, r, l, w=4):
        self.x = x
        self.y = y
        self.r = r
        self.l = l
        self.w = w


    def drawArrow(self, painter: QtGui.QPainter, angle):
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.x, self.y)
        painter.rotate(-angle)
        painter.drawPolygon(QtCore.QPointF(self.r - self.l, self.w), QtCore.QPointF(self.r, 0),
                            QtCore.QPointF(self.r - self.l, -self.w))
        if self.r == self.l:
            painter.drawEllipse(-self.w, -self.w, self.w * 2, self.w * 2)

        painter.restore()


class test1(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.scale = Scale(150, 460, 400, 106, 74, 0, 10, 10, 2, 1, '{:.0f}')
        # self.arrow = Arrow(150, 450, 388, 20)
        # self.resize(310, 120)
        self.scale = Scale(250, 250, 180, 180, 90, 0, 600, 6, 2, 5, '{:3.0f}')
        self.arrow = Arrow(150, 450, 388, 20)
        self.resize(280, 280)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setFont(QtGui.QFont('Segoi UI', 16))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
        self.scale.drawScale(painter)
        self.scale.drawVal(painter)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
        painter.setPen(QtGui.QPen(QtCore.Qt.red))
        self.arrow.drawArrow(painter, 96.4)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = test1()
    win.show()
    app.exec_()
