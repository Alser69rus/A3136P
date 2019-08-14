from PyQt5 import QtWidgets, QtGui, QtCore
from functools import partial

class KeyRow(QtWidgets.QWidget):

    def __init__(self, keys, indent: float = 0, width=0, parent=None):
        super().__init__(parent)
        size = 50
        pad = 4
        self.setFont(QtGui.QFont('Segoi UI', 20))
        self.btns = [QtWidgets.QPushButton(key, parent=self) for key in keys]
        for i, btn in enumerate(self.btns):
            if len(btn.text()) == 1:
                btn.setGeometry(i * (size + pad) + indent * size, pad, size, size)
            else:
                btn.move(i * (size + pad) + indent * size, pad)
                btn.setFixedHeight(size)

            btn.setFlat(True)


class Keypad(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Клавиатура')
        self.setFixedWidth(800)
        self.setFixedHeight(400)
        self.setFont(QtGui.QFont('Segoi UI', 14))

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.label = QtWidgets.QLabel('')
        self.label.setFont(QtGui.QFont('Segoi UI', 20))
        self.label.setFixedHeight(40)
        self.label.setAlignment(QtCore.Qt.AlignRight)
        self.vbox.addWidget(self.label)

        row = [[it for it in '1234567890-+_'],
               [it for it in 'йцукенгшщзхъ'],
               [it for it in 'фывапролджэ'],
               [it for it in 'ячсмитьбю.,'],
               [' ' * 20 + 'ПРОБЕЛ' + ' ' * 20],
               ]

        self.rows = [KeyRow(keys, i * 0.3) for i, keys in enumerate(row)]
        for row in self.rows:
            self.vbox.addWidget(row)
            for btn in row.btns:
                if len(btn.text()) == 1:
                    btn.clicked.connect(partial(self.keyPress,btn.text()))

    def keyPress(self,text):
        self.label.setText(self.label.text() + text)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])
    win = QtWidgets.QPushButton('keypad')
    key = Keypad()
    win.clicked.connect(key.exec)
    win.show()
    sys.exit(app.exec_())
