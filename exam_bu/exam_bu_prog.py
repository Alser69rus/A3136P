from PyQt5 import QtWidgets, QtCore, QtGui
import time
from dataclasses import dataclass, field

com = None
GR_HEIGHT = 300
GR_WIDTH = 800
GR_MX = 15
GR_MY = 100
GR_OFX = 40
GR_OFY = 20


@dataclass
class BU:
    dev_type: str
    prepare: bool = False
    prepare_r: bool = False
    di_res: str = ''
    di_note: str = ''
    fi_res: str = ''
    fi_note: str = ''
    shim_res: str = ''
    shim_note: str = ''
    shim_graph: list = field(default_factory=list)
    shim_i1: float = 0
    shim_i2: float = 0
    shim_res1: str = ''
    shim_res2: str = ''
    shim_res3: str = ''
    ai_res: str = ''
    ai_note: str = ''
    ai_i11: float = 0
    ai_i12: float = 0
    ai_i21: float = 0
    ai_i22: float = 0


bu = BU('')


class Form(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arr = []
        self.vbox = QtWidgets.QVBoxLayout()
        self.img_bu = QtGui.QPixmap('exam_bu\\bu.png')
        self.img_prog = QtGui.QPixmap('exam_bu\\prog.png')
        self.img_prog2 = QtGui.QPixmap('exam_bu\\prog2.png')
        self.img_xp1 = QtGui.QPixmap('exam_bu\\xp1.png')
        self.img_bu_prog = QtGui.QPixmap('exam_bu\\bu-prog.png')
        self.img_empty = QtGui.QPixmap('exam_bu\\empty.png')
        self.img = QtWidgets.QLabel()

        self.text = QtWidgets.QLabel()
        self.text.setFont(QtGui.QFont('Segoi UI', 14))
        self.text.setWordWrap(True)
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.img)
        self.vbox.addWidget(self.text)
        self.vbox.addStretch(1)
        self.img.setPixmap(self.img_empty)
        self.text.setText(
            '<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
            '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам "XS1 БУ ПИТ.", '
            '"XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p>')

    def paintEvent(self, QPaintEvent):
        if self.arr:
            painter = QtGui.QPainter(self)
            QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.black)), 1)
            points = [QtCore.QPointF(GR_OFX + i[0] * GR_MX, GR_HEIGHT - GR_OFY - i[1] * GR_MY) for i in self.arr]
            painter.drawLine(GR_OFX, GR_HEIGHT - GR_OFY + 5, GR_OFX, GR_OFY)
            painter.drawLine(GR_OFX - 5, GR_HEIGHT - GR_OFY, GR_WIDTH - GR_OFX, GR_HEIGHT - GR_OFY)
            for x in range(0, GR_WIDTH - GR_OFX * 2, GR_MX * 5):
                painter.drawLine(GR_OFX + x, GR_HEIGHT - GR_OFY + 5, GR_OFX + x, GR_HEIGHT - GR_OFY - 5)
                painter.drawText(GR_OFX + x - 5, GR_HEIGHT - 2, '{:.0f}'.format(x / GR_MX))
            for y in range(1, 6):
                painter.drawLine(GR_OFX - 5, GR_HEIGHT - GR_OFY - y * GR_MY / 2, GR_OFX + 5,
                                 GR_HEIGHT - GR_OFY - y * GR_MY / 2)
                painter.drawText(10, GR_HEIGHT - GR_OFY - y * GR_MY / 2 + 7, '{:3.1f}'.format(y / 2))
            painter.drawText(GR_OFX + 10, GR_OFY + 10, 'I, А')
            painter.drawText(GR_WIDTH - 30, GR_HEIGHT - 5, 't, с')
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)), 2))
            painter.drawPolyline(*points)


class Exam_bu(QtCore.QState):
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    btnBack = None
    btnOk = None
    end=QtCore.pyqtSignal()

    def __init__(self, parent=None, server=None, form=None):
        super().__init__(parent)
        global com
        com = self
        self.opc = server
        self.do1 = server.do1
        self.do2 = server.do2
        self.gen = server.gen
        self.pa3 = server.pa3
        self.ao = server.ao
        self.freq = server.freq
        self.frm_main = form
        self.frm = Form()
        self.frm_main.stl.addWidget(self.frm)
        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked

        self.img = self.frm.img
        self.text = self.frm.text

        self.dev_type = ''

        self.idx = 0
        self.val = 0
        self.t1 = 0
        self.t2 = 0
        self.args = []
        self.br3_zero = 0

        self.error = Error(self)
        self.finish = Finish(self)
        self.prepare = Prepare(self)
        self.switch_work = SwitchWork(self)
        self.connect_bu_di = ConnectBUDI(self)
        self.connect_bu = ConnectBU(self)
        self.di_check = DICheck(self)
        self.di_config = DIConfig(self)
        self.di_step = DIStep(self)
        self.di_fail = DIFail(self)
        self.di_done = DIDone(self)

        self.fi_check = FICheck(self)
        self.fi_param_sav = FiParamSave(self)
        self.fi_config = FiConfig(self)
        self.fi_measure = FiMeasure(self)
        self.fi_fail = FiFail(self)
        self.fi_done = FiDone(self)

        self.shim_check = ShimCheck(self)
        self.shim_measure_i1 = ShimMeasure(self)
        self.shim_save_i1 = ShimSaveI1(self)
        self.shim_measure_i2 = ShimMeasure(self)
        self.shim_save_i2 = ShimSaveI2(self)
        self.shim_graph_start = ShimGraphStart(self)
        self.shim_graph = ShimGraph(self)
        self.shim_graph_finish = ShimGraphFinish(self)
        self.shim_fail = ShimFail(self)
        self.shim_finish = ShimFinish(self)

        self.ai_check = AiCheck(self)
        self.ai_measure = AIMeasure(self)
        self.ai_ok = AIOk(self)
        self.ai_fail = AIFail(self)
        self.ai_res = AIRes(self)
        self.ai_done = AIDone(self)

        self.addTransition(self.opc.error, self.error)
        self.error.addTransition(self.finish)
        self.back_transition = self.addTransition(self.btnBack, self.finish)

        self.prepare.addTransition(self.btnOk, self.switch_work)
        self.switch_work.addTransition(self.btnOk, self.connect_bu_di)
        self.switch_work.addTransition(self.success, self.connect_bu_di)
        self.connect_bu_di.addTransition(self.connect_bu)  # self.opc.do1.updated
        self.connect_bu.addTransition(self.finish)

        self.di_check.addTransition(self.btnOk, self.di_config)
        self.di_config.addTransition(self.di_step)
        self.di_step.addTransition(self.btnOk, self.di_step)
        self.di_step.addTransition(self.btnBack, self.di_fail)
        self.di_fail.addTransition(self.di_step)
        self.di_step.addTransition(self.di_step.done, self.di_done)
        self.di_done.addTransition(self.finish)

        self.fi_check.addTransition(self.btnOk, self.fi_config)
        self.fi_check.addTransition(self.btnBack, self.fi_param_sav)
        self.fi_param_sav.addTransition(self.btnOk, self.fi_config)
        self.fi_config.addTransition(self.fi_measure)
        self.fi_measure.addTransition(self.btnOk, self.fi_measure)
        self.fi_measure.addTransition(self.btnBack, self.fi_fail)
        self.fi_fail.addTransition(self.fi_measure)
        self.fi_measure.addTransition(self.fi_measure.done, self.fi_done)
        self.fi_done.addTransition(self.finish)

        self.shim_check.addTransition(self.btnOk, self.shim_measure_i1)
        self.shim_measure_i1.addTransition(self.pa3.updated, self.shim_measure_i1)
        self.shim_measure_i1.addTransition(self.shim_measure_i1.done, self.shim_save_i1)
        self.shim_save_i1.addTransition(self.btnOk, self.shim_measure_i2)
        self.shim_measure_i2.addTransition(self.pa3.updated, self.shim_measure_i2)
        self.shim_measure_i2.addTransition(self.shim_measure_i2.done, self.shim_save_i2)
        self.shim_save_i2.addTransition(self.shim_graph_start)
        self.shim_graph_start.addTransition(self.shim_graph_start.start, self.shim_graph)
        self.shim_graph_start.addTransition(self.pa3.updated, self.shim_graph_start)
        self.shim_graph.addTransition(self.pa3.updated, self.shim_graph)
        self.shim_graph.addTransition(self.shim_graph.done, self.shim_graph_finish)
        self.shim_graph_finish.addTransition(self.btnOk, self.shim_finish)
        self.shim_graph_finish.addTransition(self.btnBack, self.shim_fail)
        self.shim_fail.addTransition(self.shim_finish)
        self.shim_finish.addTransition(self.btnOk, self.finish)

        self.ai_check.addTransition(self.ai_measure)
        self.ai_measure.addTransition(server.ao.updated, self.ai_measure)
        self.ai_measure.addTransition(self.btnBack, self.ai_fail)
        self.ai_measure.addTransition(self.btnOk, self.ai_ok)
        self.ai_fail.addTransition(self.ai_measure)
        self.ai_ok.addTransition(self.ai_measure)
        self.ai_measure.addTransition(self.ai_measure.done, self.ai_res)
        self.ai_res.addTransition(self.ai_done)
        self.ai_done.addTransition(self.btnOk, self.finish)

        self.print_result = PrintResult(self)



class Error(QtCore.QState):
    def onEntry(self, e):
        print('bu_error')


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        print('bu_finish')
        # com.opc.ai.setActive(False)
        # com.opc.di.setActive(True)
        # com.opc.pv1.setActive(False)
        # com.opc.pv2.setActive(False)
        # com.opc.pa1.setActive(False)
        # com.opc.pa2.setActive(False)
        # com.opc.pa3.setActive(False)
        # com.opc.connect_bu_di_power(False)
        # com.opc.connect_bu_power(False)
        com.frm_main.stl.setCurrentWidget(com.frm_main.check_bu)
        com.frm_main.connectmenu()
        # com.pchv.setActive(False)


class Prepare(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu = BU(dev_type=com.dev_type)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
                         '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам '
                         '"XS1 БУ ПИТ.", "XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p><p>Подключите разъем '
                         '"XS10 ИУ ПЭ" к разъему "XP8 НАГРУЗКА", которые расположены на правой стенке привода'
                         ' при помощи шлейфа</p><p>Подключите при помощи шлейфа разъем "XS12 БП Х2"'
                         ' и разъем "ХР13 24 В"</p><p>Снимите защитную крышку с разъема БУ "ОСНОВНАЯ РАБОТА" и подключите'
                         ' программатор</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class SwitchWork(QtCore.QState):
    def onEntry(self, QEvent):
        pass_list = ['ЭРЧМ30T3-04']
        if bu.dev_type in pass_list:
            com.success.emit()
        com.text.setText('<p>Переведите переключатель "РЕЗЕРВНАЯ РАБОТА" на БУ в положение '
                         '"ОТКЛ."</p><p>Для продолжения нажмите "ПРИНЯТЬ"</p>')


class ConnectBUDI(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('Производится подключение питания дискретных входов БУ')
        if bu.dev_type == 'ЭРЧМ30T3-06':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T3-04':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T3-07':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T3-08':
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type == 'ЭРЧМ30T3-08-01':
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type == 'ЭРЧМ30T3-02':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T3-05':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T3-10':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T3-10-01':
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type == 'ЭРЧМ30T4-01':
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type == 'ЭРЧМ30T4-02':
            com.opc.connect_bu_di_power(True, 24)
        elif bu.dev_type == 'ЭРЧМ30T4-02-01':
            com.opc.connect_bu_di_power(True, 24)
        elif bu.dev_type == 'ЭРЧМ30T4-03':
            com.opc.connect_bu_di_power(True, 75)
        else:
            com.opc.connect_bu_di_power(False)


class ConnectBU(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('Производится подключение питания БУ')

        com.opc.connect_bu_power()
        lst = [com.frm_main.check_bu.btn_di, com.frm_main.check_bu.btn_fi, com.frm_main.check_bu.btn_power,
               com.frm_main.check_bu.btn_ai]
        for e in lst:
            e.setEnabled(True)
        com.frm_main.check_bu.btn_prepare.state = 'ok'
        bu.prepare = True


class DICheck(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        bu.di_res = ''
        bu.di_note = ''
        com.text.setText('<p>Установите режим "РЕ00" на программаторе. Для этого удерживайте нажатой кнопку '
                         '1  программатора, а затем кнопками 5 и 6 установите на верхнем индикаторе номер '
                         'режима. После чего отпустите кнопку 1 и нажмите кнопку программатора 2. Кнопками 5 и 6 '
                         'установите номер подрежима.</p>'
                         )


class DI62(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('<p>На нижнем индикаторе необходимо установить адресс 62. '
                         'Для этого кнопкой 4 выберать разряд, а кнопками 5 и 6 задайть значение. На текущий '
                         'разряд указывает точка.</p><p>После всех манипуляций на индикаторах программатора должно '
                         'быть:<br><br><b><font size="+2">bn00<br>6200</font></b></p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>')


class DI63(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('<p>На нижнем индикаторе необходимо установить адресс 63. '
                         'Для этого кнопкой 4 выберать разряд, а кнопками 5 и 6 задайть значение. На текущий '
                         'разряд указывает точка.</p><p>После всех манипуляций на индикаторах программатора должно '
                         'быть:<br><br><b><font size="+2">bn00<br>6300</font></b></p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>')


class DI66(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('<p>На нижнем индикаторе необходимо установить адресс 66. '
                         'Для этого кнопкой 4 выберать разряд, а кнопками 5 и 6 задайть значение. На текущий '
                         'разряд указывает точка.</p><p>После всех манипуляций на индикаторах программатора должно '
                         'быть:<br><br><b><font size="+2">bn00<br>6600</font></b></p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>')


class DIConfig(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.removeTransition(com.back_transition)
        com.idx = -1
        if bu.dev_type == 'ЭРЧМ30T3-06':
            com.opc.connect_bu_di_power(True, 110)
            com.args = (
                (0, '01', 'ДВХ1'), (1, '02', 'ДВХ2'), (2, '04', 'ДВХ3'), (3, '08', 'ДВХ4'),
                (5, '40', 'ДВХ5 (Упр. от КМ)'),
                (8, '10', 'ДВХ6 (Работа/стоп)'), (6, '20', 'ДВХ7 (Поед. реж.)'))


class DIStep(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.do1.setValue([0] * 16 + com.do1.value[16:])
        com.idx += 1
        if com.idx < len(com.args):
            com.do1.setValue(True, com.args[com.idx][0])
            com.text.setText('<p>На индикаторах программатора должны быть следующие показания:'
                             '<br><br><b><font size="+3">bn00<br>62{}</font></b></p><p>'
                             'Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font">'
                             ',<br>Если условие не выполняется нажмите <font color="red">"НАЗАД"</font">.'
                             '</p>'.format(com.args[com.idx][1]))
        else:
            self.done.emit()


class DIFail(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        bu.di_note += 'Неисправен дискретный вход {}.\n'.format(com.args[com.idx][2])
        bu.di_res = 'НЕ НОРМА'


class DIDone(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.addTransition(com.back_transition)
        com.do1.setValue([0] * 20 + com.do1.value[20:])
        if not bu.di_res:
            bu.di_res = 'норма'
            com.frm_main.check_bu.btn_di.state = 'ok'
        else:
            com.frm_main.check_bu.btn_di.state = 'fail'


class FICheck(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        bu.fi_res = ''
        bu.fi_note = ''
        com.removeTransition(com.back_transition)
        com.text.setText('<p>Установите на программаторе режим <b>"РЕА0"</b>. Для этого зажмите кнопку 1 для выбора '
                         'режима или кнопку 2 для выбора подрежима и кнопками 5 и 6 установите значение А0. На '
                         'нижнем ряде индикаторов программатора должно быть: '
                         '<b>0124</b></p><p></p>'
                         'Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font">'
                         ',<br>Если условие не выполняется нажмите <font color="red">"НАЗАД"</font">.</p>'
                         )


class FiParamSave(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText('<p>Кнопками 5 и 6 установите на нижнем ряде индикаторов значение '
                         '<b>0124</b>.</p><p>После чего удерживая кнопку 1 или кнопку 2 '
                         'кнопками 5 и 6 установите  режим "F0". Затем нажмите и удерживайте кнопку 3 и '
                         'кратковременно нажмите кнопку 6. Через несколько секунд, после изменения показаний '
                         'индикаторов программатора, отпустите кнопку 3.</p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>'
                         )


class FiConfig(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.do2.setValue(com.do2.value[:12] + [1, 1, 1] + com.do2.value[15:])
        com.idx = -1
        com.args = (
            ('РЕ10', 'верхнего', '0495-0502', 'ДВХ1 - ДЧД', [1030, 0, 0]),
            ('РЕ9E', 'нижнего', '0995-1005', 'ДВХ2 - ДЧТК', [0, 1000, 0]),
            ('РЕ70', 'верхнего', '01.00-06.00', 'ДВХ3 - ДП 25 кГц', [0, 0, 25000]),
            ('РЕ70', 'верхнего', '14.00-25.00', 'ДВХ3 - ДП 17 кГц', [0, 0, 17000]))


class FiMeasure(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.idx += 1
        if com.idx < len(com.args):
            args = com.args[com.idx]
            com.gen.setValue(args[4])
            com.text.setText('<p>Зажав кнопку программатора 1 или 2 установите при помощи кнопок 5 и 6 '
                             '<b>режим "{}"</b>.</p>'
                             '<p>Показания <b>{} ряда</b> индикаторов должны находится в пределах '
                             '<b>{}</b></p>'
                             '<p>Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font">,'
                             '<br>Если условие не выполняется нажмите <font color="red">"НАЗАД"</font">.</p>'
                             ''.format(*args))
        else:
            self.done.emit()


class FiFail(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        args = com.args[com.idx]
        bu.fi_res = 'НЕ НОРМА'
        bu.fi_note += 'Неисправен частотный вход {}.\n'.format(args[3])


class FiDone(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.addTransition(com.back_transition)
        com.do2.setValue(com.do2.value[:12] + [0, 0, 0] + com.do2.value[15:])
        com.gen.setValue([0, 0, 0])
        if not bu.fi_res:
            bu.fi_res = 'норма'
            com.frm_main.check_bu.btn_fi.state = 'ok'
        else:
            com.frm_main.check_bu.btn_fi.state = 'fail'


class ShimCheck(QtCore.QState):
    def onEntry(self, QEvent):
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        bu.shim_res = ''
        bu.shim_note = ''
        com.args = ['0,6-0,9', 0, 0]
        com.idx = 0
        com.val = 0
        bu.shim_i1 = 0
        bu.shim_i2 = 0
        bu.shim_res1 = ''
        bu.shim_res2 = ''
        bu.shim_res3 = ''
        com.pa3.setActive()
        com.text.setText('<p>Установите на программаторе режим <b>"PE80"</b>. Для этого зажав кнопку 1 или 2 кнопками'
                         ' 5 и 6 установите требуемое значение режима.</p>'
                         '<p>Нижний ряд индикаторов должен показывать <b>"P000"</b>'
                         '</p><p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>'
                         )

        com.do2.setValue(1, 6)  # PA3
        if com.dev_type == 'ЭРЧМ30T3-06':
            com.opc.connect_bu_di_power(True, 110)
            com.do1.setValue(0, 8)  # work/stop


class ShimMeasure(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        com.idx += 1
        com.val += abs(com.pa3.value)
        com.text.setText('<p>Ожидайте. Производится измерение тока силовой цепи.</p>'
                         '<p>Норма: {} А    Факт: {:4.3f} А. Измерение завершено на {:.0%}.</p>'
                         ''.format(com.args[0], com.val / com.idx, com.idx / 23))
        if com.idx >= 23:
            com.val /= com.idx
            self.done.emit()


class ShimSaveI1(QtCore.QState):
    def onEntry(self, QEvent):
        if 0.9 <= com.val <= 1.05:
            com.val = 0.9
        bu.shim_i1 = com.val
        if not (0.6 <= com.val <= 0.9):
            bu.shim_note += 'Ток в силовой цепи ПЭ при параметре "Р000" режима "РЕ80" факт:' \
                            ' {:.3f} А, норма: 0,6-0,9 А.\n'.format(com.val)
            bu.shim_res = 'НЕ НОРМА'

        com.val = 0
        com.idx = 0
        com.args[0] = '2,1-2,4'
        com.text.setText('<p>Установите при помощи кнопки 6 значение '
                         '<b>"P3F8"</b> на нижнем индикаторе  программатора.</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>')


class ShimSaveI2(QtCore.QState):
    def onEntry(self, QEvent):
        if 2.4 <= com.val <= 2.55:
            com.val = 2.4
        bu.shim_i2 = com.val
        if not (2.1 <= com.val <= 2.4):
            bu.shim_note += 'Ток в силовой цепи ПЭ при параметре "Р3F8" режима "РЕ80" факт: ' \
                            '{} А, норма: 2,1-2,9 А.\n'.format(com.val)
            bu.shim_res = 'НЕ НОРМА'

        com.text.setText('<p>Нажмите и удерживайте кнопку 6 программатора. Значения нижнего ряда '
                         'индикаторов будут уменьшаться.'
                         'При этом будет построен график тока силовой цепи.</p>'
                         )


class ShimGraphStart(QtCore.QState):
    start = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.frm.img.clear()
        com.img.setMinimumHeight(GR_HEIGHT)
        com.args = [(0, abs(com.pa3.value))]
        com.frm.arr = com.args
        com.frm.img.update()
        com.t1 = time.perf_counter()
        if abs(com.pa3.value) < bu.shim_i2 - 0.01:
            self.start.emit()


class ShimGraph(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        com.t2 = time.perf_counter()
        dt = com.t2 - com.t1
        v = abs(com.pa3.value)
        com.args.append((dt, v))
        com.text.setText('<p>График тока силовой цепи.</p>'
                         '<p>Текущее значение тока {:5.3f} А, с начала испытания прошло {:.1f} с.</p>'
                         ''.format(v, dt))
        if dt > 50 or v < bu.shim_i1 + 0.05:
            self.done.emit()
        com.frm.arr = com.args
        com.frm.img.update()


class ShimGraphFinish(QtCore.QState):
    def onEntry(self, QEvent):
        com.removeTransition(com.back_transition)
        bu.shim_graph = com.args[:]

        com.text.setText(
            '<p>График должен монотонно уменьшаться. Не должно быть "пиков", '
            '"провалов" и "плато" на всем протяжении графика.</p>'
            '<p>Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font>,'
            '<br>Если условие не выполняется нажмите <font color="red">"НАЗАД"</font>.</p>')


class ShimFail(QtCore.QState):
    def onEntry(self, QEvent):
        bu.shim_note += 'График тока силовой цепи не соответствует требованиям ТУ.\n'
        bu.shim_res = 'НЕ НОРМА'


class ShimFinish(QtCore.QState):
    def onEntry(self, QEvent):
        global com

        com.img.setMinimumHeight(0)
        com.addTransition(com.back_transition)
        com.do2.setValue(0, 6)  # PA3
        com.opc.connect_bu_di_power(False)
        com.do1.setValue(0, 8)  # work/stop
        if not bu.shim_res:
            bu.shim_res = 'норма'
            com.frm_main.check_bu.btn_power.state = 'ok'
        else:
            com.frm_main.check_bu.btn_power.state = 'fail'
        com.pa3.setActive(False)

        if 0.6 <= bu.shim_i1 <= 0.9:
            bu.shim_res1 = 'норма'
            res1 = '<font color="green">норма</font>'
        else:
            bu.shim_res1 = 'НЕ НОРМА'
            res1 = '<font color="red">НЕ НОРМА</font>'

        if 2.1 <= bu.shim_i2 <= 2.4:
            res2 = '<font color="green">норма</font>'
            bu.shim_res2 = 'норма'
        else:
            res2 = '<font color="red">НЕ НОРМА</font>'
            bu.shim_res2 = 'НЕ НОРМА'

        if not bu.shim_note.count('График'):
            res3 = '<font color="green">норма</font>'
            bu.shim_res3 = 'норма'
        else:
            res3 = '<font color="red">НЕ НОРМА {}</font>'
            bu.shim_res3 = 'НЕ НОРМА'

        com.frm.arr = []
        com.text.setText('<p>Результаты проверки силового канала:</p>'
                         '<p>Минимальный ток - факт: {:5.3f} А, норма: 0,6-0,9 А, результат: {}<br>'
                         'Максимальный ток - факт: {:5.3f} А, норма: 2,1-2,4 А, результат: {}<br>'
                         'Монотонность графика: {}</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для выхода в меню проверки</p>'
                         ''.format(bu.shim_i1, res1, bu.shim_i2, res2, res3))


class AiCheck(QtCore.QState):
    def onEntry(self, QEvent):
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        com.removeTransition(com.back_transition)
        bu.ai_res = ''
        bu.ai_note = ''
        bu.ai_res1 = ''
        bu.ai_res2 = ''
        com.do2.setValue(1, 15)  # вкл пит. АО
        com.ao.setActive()
        com.br3_zero = com.freq.value[2]
        com.val = 0
        com.idx = 0
        com.args = [
            {'v0': 10, 'ch': 'АВХ1 - ДДН', 'reg': 'PE91', 'row': 'верхнего', 'val': '00.00', 'norm': '3.97-4.03'},
            {'v0': 900, 'ch': 'АВХ1 - ДДН', 'reg': 'PE91', 'row': 'верхнего', 'val': '02.50', 'norm': '19.97-20.03'},
            {'v0': 10, 'ch': 'АВХ2 - ДДМ', 'reg': 'PEС0', 'row': 'верхнего', 'val': '00.00', 'norm': '3.97-4.03'},
            {'v0': 900, 'ch': 'АВХ2 - ДДМ', 'reg': 'PEС0', 'row': 'верхнего', 'val': '16.00', 'norm': '19.97-20.03'}]


class AIMeasure(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        if com.idx >= len(com.args):
            self.done.emit()
            return
        cur = com.args[com.idx]
        v0 = cur['v0']
        br3 = com.freq.value[2] - com.br3_zero
        v = br3 + v0
        if v < 0:
            v = 0
        if v > 1000:
            v = 1000
        i = 3.9 + v * (20.1 - 3.9) / 1000
        com.val = i

        com.ao.setValue([v, v] + com.ao.value[2:])

        ch = cur['ch']
        reg = cur['reg']
        row = cur['row']
        val = cur['val']
        norm = cur['norm']

        com.text.setText(f'<p>Для проверки канала {ch} установите на программаторе режим <b>"{reg}"</b>. Для этого '
                         'удерживая кнопку 1 или кнопку 2  программатора кнопками 5 и 6 установите требуемое '
                         'значение режима.</p>'
                         f'<p>После чего поворотом рукоятки валкодера BR3 установите значение {row} '
                         f'ряда индикаторов равным <b>{val}</b>.</p>'
                         f'<p>Текущее значение тока: {i:5.2f} мА, норма: {norm} мА</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения,<br>'
                         f'Если значение {val} установить не удалось нажмите "НАЗАД".</p>'
                         )


class AIFail(QtCore.QState):
    def onEntry(self, QEvent):
        cur = com.args[com.idx]
        ch = cur['ch']
        val = cur['val']
        bu.ai_note += f'Не удалось проверить канал {ch} для значения {val}\n'
        com.idx += 1


class AIOk(QtCore.QState):
    def onEntry(self, QEvent):
        if com.idx == 0:
            bu.ai_i11 = com.val
        elif com.idx == 1:
            bu.ai_i12 = com.val
        elif com.idx == 2:
            bu.ai_i21 = com.val
        elif com.idx == 3:
            bu.ai_i22 = com.val
        com.idx += 1


class AIRes(QtCore.QState):
    def onEntry(self, QEvent):
        com.addTransition(com.back_transition)
        com.val = ''
        if not bu.ai_note.count('АВХ1'):
            bu.ai_res = f'Канал АВХ1 - ДДН норма 4-20 мА, факт: {bu.ai_i11:5.2f}-{bu.ai_i12:5.2f} мА, результат: '
            if 3.97 <= bu.ai_i11 <= 4.03 and 19.97 <= bu.ai_i12 <= 20.03:
                bu.ai_res += 'норма'
                com.val = '1'
            else:
                bu.ai_res += 'НЕ НОРМА'
        else:
            bu.ai_res = 'Канал АВХ1 - ДДН, выход за пределы диапазона.'
        bu.ai_res += '\n'

        if not bu.ai_note.count('АВХ2'):
            bu.ai_res += f'Канал АВХ2 - ДДМ норма 4-20 мА, факт: {bu.ai_i21:5.2f}-{bu.ai_i22:5.2f} мА, результат: '
            if 3.97 <= bu.ai_i21 <= 4.03 and 19.97 <= bu.ai_i22 <= 20.03:
                bu.ai_res += 'норма'
                com.val += '2'
            else:
                bu.ai_res += 'НЕ НОРМА'
        else:
            bu.ai_res = 'Канал АВХ2 - ДДМ, выход за пределы диапазона.'

        if com.val == '12':
            com.frm_main.check_bu.btn_ai.state = 'ok'
        else:
            com.frm_main.check_bu.btn_ai.state = 'fail'


class AIDone(QtCore.QState):
    def onEntry(self, QEvent):
        com.do2.setValue(0, 15)  # выкл пит. АО
        com.ao.setActive(False)
        com.text.setText(f'<p>Результаты проверки аналоговых входов:</p>'
                         f'<p>{bu.ai_res}</p>'
                         '<br>Нажмите "ПРИНЯТЬ" для завершения проверки')


class PrintResult(QtCore.QState):
    def onEntry(self, QEvent):
        print('protokol')

class Ended(QtCore.QState):
    def onEntry(self, e):
        global com
        print('bu_finish')
        # com.opc.ai.setActive(False)
        # com.opc.di.setActive(True)
        # com.opc.pv1.setActive(False)
        # com.opc.pv2.setActive(False)
        # com.opc.pa1.setActive(False)
        # com.opc.pa2.setActive(False)
        # com.opc.pa3.setActive(False)
        # com.opc.connect_bu_di_power(False)
        # com.opc.connect_bu_power(False)
        com.frm_main.stl.setCurrentWidget(com.frm_main.mnu_bu)
        com.frm_main.connectmenu()
        # com.pchv.setActive(False)






