from PyQt5 import QtWidgets, QtCore, QtGui, QtPrintSupport
import time
from dataclasses import dataclass, field
import datetime
from pathlib import Path

com = None


@dataclass
class BU:
    dev_type: str
    prepare: bool = False
    prepare_r: bool = False

    di_res: list = field(default_factory=list)
    di_res_r: list = field(default_factory=list)
    di_min: int = 0
    di_max: int = 0
    di_reg: str = ''

    fi_res: str = ''
    fi_note: str = ''
    fi_res_r: str = ''
    fi_note_r: str = ''

    shim_res: str = ''
    shim_note: str = ''
    shim_graph: list = field(default_factory=list)
    shim_i1: float = 0
    shim_i2: float = 0
    shim_res1: str = ''
    shim_res2: str = ''
    shim_res3: str = ''

    shim_res_r: str = ''
    shim_note_r: str = ''
    shim_graph_r: list = field(default_factory=list)
    shim_i1_r: float = 0
    shim_i2_r: float = 0
    shim_res1_r: str = ''
    shim_res2_r: str = ''
    shim_res3_r: str = ''

    ai_res: str = ''
    ai_note: str = ''
    ai_i11: float = 0
    ai_i12: float = 0
    ai_i21: float = 0
    ai_i22: float = 0

    ai_3_1: bool = False
    ai_3_2: bool = False
    ai_3_3: bool = False


bu = BU('')


class Form(QtWidgets.QWidget):
    GR_HEIGHT = 300
    GR_WIDTH = 800
    GR_MX = 15
    GR_MY = 100
    GR_OFX = 40
    GR_OFY = 20

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
            points = [QtCore.QPointF(self.GR_OFX + i[0] * self.GR_MX,
                                     self.GR_HEIGHT - self.GR_OFY - i[1] * self.GR_MY)
                      for i in self.arr]
            painter.drawLine(self.GR_OFX,
                             self.GR_HEIGHT - self.GR_OFY + 5,
                             self.GR_OFX,
                             self.GR_OFY)
            painter.drawLine(self.GR_OFX - 5,
                             self.GR_HEIGHT - self.GR_OFY,
                             self.GR_WIDTH - self.GR_OFX,
                             self.GR_HEIGHT - self.GR_OFY)
            for x in range(0, self.GR_WIDTH - self.GR_OFX * 2, self.GR_MX * 5):
                painter.drawLine(self.GR_OFX + x,
                                 self.GR_HEIGHT - self.GR_OFY + 5,
                                 self.GR_OFX + x,
                                 self.GR_HEIGHT - self.GR_OFY - 5)
                painter.drawText(self.GR_OFX + x - 5,
                                 self.GR_HEIGHT - 2,
                                 f'{x / self.GR_MX:.0f}')
            for y in range(1, 6):
                painter.drawLine(self.GR_OFX - 5,
                                 self.GR_HEIGHT - self.GR_OFY - y * self.GR_MY / 2,
                                 self.GR_OFX + 5,
                                 self.GR_HEIGHT - self.GR_OFY - y * self.GR_MY / 2)
                painter.drawText(10,
                                 self.GR_HEIGHT - self.GR_OFY - y * self.GR_MY / 2 + 7,
                                 f'{y / 2:3.1f}')
            painter.drawText(self.GR_OFX + 10,
                             self.GR_OFY + 10,
                             'I, А')
            painter.drawText(self.GR_WIDTH - 30,
                             self.GR_HEIGHT - 5,
                             't, с')
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)), 2))
            painter.drawPolyline(*points)


class FormPrint(QtPrintSupport.QPrintPreviewWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.fitToWidth()


class Exam_bu(QtCore.QState):
    success = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal()
    btnBack = None
    btnOk = None
    end = QtCore.pyqtSignal()

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
        self.frm_print = FormPrint()
        self.protocol = Protocol(self)
        self.frm_print.paintRequested.connect(self.protocol.preview)
        self.frm_main.stl.addWidget(self.frm_print)
        self.frm_main.stl.addWidget(self.frm)
        self.btnBack = self.frm_main.btnPanel.btnBack.clicked
        self.btnOk = self.frm_main.btnPanel.btnOk.clicked
        self.btnUp = self.frm_main.btnPanel.btnUp.clicked
        self.btnDown = self.frm_main.btnPanel.btnDown.clicked

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

        self.prepare1 = Prepare1(self)
        self.prepare2 = Prepare2(self)
        self.prepare3 = Prepare3(self)
        self.prepare4 = Prepare4(self)
        self.switch_work = SwitchWork(self)
        self.connect_bu_di = ConnectBUDI(self)
        self.connect_bu = ConnectBU(self)

        self.prepare_r = PrepareR(self)
        self.connect_bu_r = ConnectBUR(self)

        self.di_check = DICheck(self)
        self.di_select_first = DISelectFirst(self)
        self.di_select_second = DISelectSecond(self)
        self.di_62 = DI62(self)
        self.di_63 = DI63(self)
        self.di_66 = DI66(self)
        self.di_config1 = DIConfig1(self)
        self.di_config2 = DIConfig2(self)
        self.di_show_table = DIShowTable(self)
        self.di_key_check = DIKeyCheck(self)
        self.di_key_ok = DIKeyOk(self)
        self.di_success = DISuccess(self)
        self.di_fail = DIFail(self)
        self.di_next = DINext(self)
        self.di_previous = DIPrevious(self)
        self.di_result = DIResult(self)

        self.di_check_r = DICheckR(self)
        self.di_29 = DI29(self)
        self.di_config_r = DIConfigR(self)
        self.di_show_table_r = DIShowTableR(self)
        self.di_key_check_r = DIKeyCheck(self)
        self.di_key_ok_r = DIKeyOkR(self)
        self.di_success_r = DISuccessR(self)
        self.di_fail_r = DIFailR(self)
        self.di_next_r = DINext(self)
        self.di_previous_r = DIPrevious(self)
        self.di_result_r = DIResultR(self)

        self.fi_check = FICheck(self)
        self.fi_param_sav = FiParamSave(self)
        self.fi_config = FiConfig(self)
        self.fi_measure = FiMeasure(self)
        self.fi_fail = FiFail(self)
        self.fi_done = FiDone(self)

        self.fi_check_r = FICheckR(self)
        self.fi_param_sav_r = FiParamSave(self)
        self.fi_config_r = FiConfigR(self)
        self.fi_measure_r = FiMeasure(self)
        self.fi_fail_r = FiFailR(self)
        self.fi_done_r = FiDoneR(self)

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
        self.shim_reg_off = ShimRegOff(self)

        self.shim_check_r = ShimCheckR(self)
        self.shim_measure_i1_r = ShimMeasure(self)
        self.shim_save_i1_r = ShimSaveI1R(self)
        self.shim_measure_i2_r = ShimMeasure(self)
        self.shim_save_i2_r = ShimSaveI2R(self)
        self.shim_graph_start_r = ShimGraphStartR(self)
        self.shim_graph_r = ShimGraphR(self)
        self.shim_graph_finish_r = ShimGraphFinishR(self)
        self.shim_fail_r = ShimFailR(self)
        self.shim_finish_r = ShimFinishR(self)
        self.shim_reg_off_r = ShimRegOff(self)

        self.ai_check = AiCheck(self)
        self.ai_measure = AIMeasure(self)
        self.ai_ok = AIOk(self)
        self.ai_fail = AIFail(self)
        self.ai_res = AIRes(self)
        self.ai_done = AIDone(self)

        self.rt_check = RtCheck(self)
        self.rt_100 = Rt100(self)
        self.rt_max = RtMax(self)
        self.rt_success_1 = RtSuccess1(self)
        self.rt_fail_1 = RtFail1(self)
        self.rt_success_2 = RtSuccess2(self)
        self.rt_fail_2 = RtFail2(self)
        self.rt_success_3 = RtSuccess3(self)
        self.rt_fail_3 = RtFail3(self)
        self.rt_switch = AIRegSwitch(self)
        self.rt_res = RtRes(self)

        self.addTransition(self.opc.error, self.error)
        self.error.addTransition(self.finish)
        self.back_transition = self.addTransition(self.btnBack, self.finish)

        self.prepare1.addTransition(self.btnOk, self.prepare2)
        self.prepare2.addTransition(self.btnOk, self.prepare3)
        self.prepare3.addTransition(self.btnOk, self.prepare4)
        self.prepare4.addTransition(self.btnOk, self.switch_work)
        self.switch_work.addTransition(self.btnOk, self.connect_bu_di)
        self.switch_work.addTransition(self.switch_work.success, self.connect_bu_di)
        self.connect_bu_di.addTransition(self.connect_bu)
        self.connect_bu.addTransition(self.finish)

        self.prepare_r.addTransition(self.btnOk, self.connect_bu_r)
        self.connect_bu_r.addTransition(self.finish)

        self.di_check.addTransition(self.btnOk, self.di_select_first)
        self.di_select_first.addTransition(self.di_select_first.type3, self.di_62)
        self.di_select_first.addTransition(self.di_select_first.type4, self.di_66)
        self.di_62.addTransition(self.btnOk, self.di_config1)
        self.di_66.addTransition(self.btnOk, self.di_config1)
        self.di_config1.addTransition(self.di_show_table)
        self.di_show_table.addTransition(self.di_key_check)
        self.di_key_check.addTransition(self.freq.updated, self.di_key_check)
        self.di_key_check.addTransition(self.di_key_check.next, self.di_next)
        self.di_key_check.addTransition(self.di_key_check.previous, self.di_previous)
        self.di_next.addTransition(self.di_show_table)
        self.di_previous.addTransition(self.di_show_table)
        self.di_key_check.addTransition(self.btnUp, self.di_success)
        self.di_key_check.addTransition(self.btnDown, self.di_fail)
        self.di_success.addTransition(self.di_next)
        self.di_fail.addTransition(self.di_next)
        self.di_key_check.addTransition(self.btnOk, self.di_key_ok)
        self.di_key_ok.addTransition(self.di_key_ok.next, self.di_next)
        self.di_key_ok.addTransition(self.di_key_ok.done, self.di_select_second)
        self.di_select_second.addTransition(self.di_select_second.done, self.di_result)
        self.di_select_second.addTransition(self.di_select_second.di63, self.di_63)
        self.di_63.addTransition(self.btnOk, self.di_config2)
        self.di_config2.addTransition(self.di_show_table)
        self.di_result.addTransition(self.btnOk, self.finish)

        self.di_check_r.addTransition(self.btnOk, self.di_29)
        self.di_29.addTransition(self.btnOk, self.di_config_r)
        self.di_config_r.addTransition(self.di_show_table_r)
        self.di_show_table_r.addTransition(self.di_key_check_r)
        self.di_key_check_r.addTransition(self.freq.updated, self.di_key_check_r)
        self.di_key_check_r.addTransition(self.di_key_check_r.next, self.di_next_r)
        self.di_key_check_r.addTransition(self.di_key_check_r.previous, self.di_previous_r)
        self.di_next_r.addTransition(self.di_show_table_r)
        self.di_previous_r.addTransition(self.di_show_table_r)
        self.di_key_check_r.addTransition(self.btnUp, self.di_success_r)
        self.di_key_check_r.addTransition(self.btnDown, self.di_fail_r)
        self.di_success_r.addTransition(self.di_next_r)
        self.di_fail_r.addTransition(self.di_next_r)
        self.di_key_check_r.addTransition(self.btnOk, self.di_key_ok_r)
        self.di_key_ok_r.addTransition(self.di_key_ok_r.next, self.di_next_r)
        self.di_key_ok_r.addTransition(self.di_key_ok_r.done, self.di_result_r)
        self.di_result_r.addTransition(self.btnOk, self.finish)

        self.fi_check.addTransition(self.btnOk, self.fi_config)
        self.fi_check.addTransition(self.btnDown, self.fi_param_sav)
        self.fi_param_sav.addTransition(self.btnOk, self.fi_config)
        self.fi_config.addTransition(self.fi_measure)
        self.fi_measure.addTransition(self.btnOk, self.fi_measure)
        self.fi_measure.addTransition(self.btnDown, self.fi_fail)
        self.fi_fail.addTransition(self.fi_measure)
        self.fi_measure.addTransition(self.fi_measure.done, self.fi_done)
        self.fi_done.addTransition(self.finish)

        self.fi_check_r.addTransition(self.btnOk, self.fi_config_r)
        self.fi_check_r.addTransition(self.btnDown, self.fi_param_sav_r)
        self.fi_param_sav_r.addTransition(self.btnOk, self.fi_config_r)
        self.fi_config_r.addTransition(self.fi_measure_r)
        self.fi_measure_r.addTransition(self.btnOk, self.fi_measure_r)
        self.fi_measure_r.addTransition(self.btnDown, self.fi_fail_r)
        self.fi_fail_r.addTransition(self.fi_measure_r)
        self.fi_measure_r.addTransition(self.fi_measure_r.done, self.fi_done_r)
        self.fi_done_r.addTransition(self.finish)

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
        self.shim_graph_finish.addTransition(self.btnDown, self.shim_fail)
        self.shim_fail.addTransition(self.shim_finish)
        self.shim_finish.addTransition(self.btnOk, self.shim_reg_off)
        self.shim_reg_off.addTransition(self.btnOk, self.finish)

        self.shim_check_r.addTransition(self.btnOk, self.shim_measure_i1_r)
        self.shim_measure_i1_r.addTransition(self.pa3.updated, self.shim_measure_i1_r)
        self.shim_measure_i1_r.addTransition(self.shim_measure_i1_r.done, self.shim_save_i1_r)
        self.shim_save_i1_r.addTransition(self.btnOk, self.shim_measure_i2_r)
        self.shim_measure_i2_r.addTransition(self.pa3.updated, self.shim_measure_i2_r)
        self.shim_measure_i2_r.addTransition(self.shim_measure_i2_r.done, self.shim_save_i2_r)
        self.shim_save_i2_r.addTransition(self.shim_graph_start_r)
        self.shim_graph_start_r.addTransition(self.shim_graph_start_r.start, self.shim_graph_r)
        self.shim_graph_start_r.addTransition(self.pa3.updated, self.shim_graph_start_r)
        self.shim_graph_r.addTransition(self.pa3.updated, self.shim_graph_r)
        self.shim_graph_r.addTransition(self.shim_graph_r.done, self.shim_graph_finish_r)
        self.shim_graph_finish_r.addTransition(self.btnOk, self.shim_finish_r)
        self.shim_graph_finish_r.addTransition(self.btnDown, self.shim_fail_r)
        self.shim_fail_r.addTransition(self.shim_finish_r)
        self.shim_finish_r.addTransition(self.btnOk, self.shim_reg_off_r)
        self.shim_reg_off_r.addTransition(self.btnOk, self.finish)

        self.ai_check.addTransition(self.ai_measure)
        self.ai_measure.addTransition(server.ao.updated, self.ai_measure)
        self.ai_measure.addTransition(self.btnDown, self.ai_fail)
        self.ai_measure.addTransition(self.btnOk, self.ai_ok)
        self.ai_fail.addTransition(self.rt_switch)
        self.ai_ok.addTransition(self.rt_switch)
        self.rt_switch.addTransition(self.rt_switch.done, self.ai_measure)
        self.rt_switch.addTransition(self.btnOk, self.ai_measure)
        self.ai_measure.addTransition(self.ai_measure.done, self.ai_res)
        self.ai_res.addTransition(self.ai_done)
        self.ai_done.addTransition(self.btnOk, self.finish)

        self.rt_check.addTransition(self.btnOk, self.rt_success_1)
        self.rt_check.addTransition(self.btnDown, self.rt_fail_1)
        self.rt_success_1.addTransition(self.rt_100)
        self.rt_fail_1.addTransition(self.rt_100)
        self.rt_100.addTransition(self.btnOk, self.rt_success_2)
        self.rt_100.addTransition(self.btnDown, self.rt_fail_2)
        self.rt_success_2.addTransition(self.rt_max)
        self.rt_fail_2.addTransition(self.rt_max)
        self.rt_max.addTransition(self.btnOk, self.rt_success_3)
        self.rt_max.addTransition(self.btnDown, self.rt_fail_3)
        self.rt_success_3.addTransition(self.rt_res)
        self.rt_fail_3.addTransition(self.rt_res)
        self.rt_res.addTransition(self.btnOk, self.finish)


class Error(QtCore.QState):
    def onEntry(self, e):
        print('bu_error')


class Finish(QtCore.QFinalState):
    def onEntry(self, e):
        global com
        # com.opc.ai.setActive(False)
        # com.opc.di.setActive(True)
        # com.opc.pv1.setActive(False)
        # com.opc.pv2.setActive(False)
        # com.opc.pa1.setActive(False)
        # com.opc.pa2.setActive(False)
        # com.opc.pa3.setActive(False)
        # com.opc.connect_bu_di_power(False)
        # com.opc.connect_bu_power(False)
        com.freq.setActive(True)
        com.frm_main.stl.setCurrentWidget(com.frm_main.check_bu)
        com.frm_main.connectmenu()
        # com.pchv.setActive(False)


class Prepare1(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.opc.connect_bu_di_power(False)
        com.opc.connect_bu_power(False)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Установите блок управления (БУ) на кронштейн на боковой стенке пульта.</p>'
                         '<p>Подключите шлейфы к разъемам "XP1", "XP2", "XP3" блока управления и разъемам '
                         '"XS1 БУ ПИТ.", "XS2 БУ ДВХ", "XS3 БУ АВХ" пульта соответственно</p>'
                         '<p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare2(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Подключите разъем привода "XS10 ИУ ПЭ" к разъему привода "XP8 НАГРУЗКА", '
                         'или к разъему поворотного электромагнита регулятора. '
                         '</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare3(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Подключите при помощи шлейфа разъем пульта "XS12 БП Х2"'
                         ' и разъем "ХР13 24 В"</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class Prepare4(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Снимите защитную крышку с разъема БУ "ОСНОВНАЯ РАБОТА" и подключите'
                         ' программатор</p><p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class SwitchWork(QtCore.QState):
    success = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        if bu.dev_type == 'ЭРЧМ30Т3-06':
            com.text.setText('<p>Переведите переключатель "РЕЗЕРВНАЯ РАБОТА" на БУ в положение '
                             '"ОТКЛ."</p><p>Для продолжения нажмите "ПРИНЯТЬ"</p>')
        else:
            self.success.emit()


class ConnectBUDI(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('Производится подключение питания дискретных входов БУ')

        if bu.dev_type in ['ЭРЧМ30Т3-06', 'ЭРЧМ30Т3-04', 'ЭРЧМ30Т3-07']:
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type in ['ЭРЧМ30Т3-12', 'ЭРЧМ30Т3-12-01', 'ЭРЧМ30Т3-12-02', 'ЭРЧМ30Т3-12-03']:
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type in ['ЭРЧМ30Т3-08', 'ЭРЧМ30Т3-08-01']:
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type in ['ЭРЧМ30Т3-02', 'ЭРЧМ30Т3-05', 'ЭРЧМ30Т3-10', 'ЭРЧМ30Т3-10-01']:
            com.opc.connect_bu_di_power(True, 110)
        elif bu.dev_type in ['ЭРЧМ30Т4-01']:
            com.opc.connect_bu_di_power(True, 75)
        elif bu.dev_type in ['ЭРЧМ30Т4-02']:
            com.opc.connect_bu_di_power(True, 24)
        elif bu.dev_type in ['ЭРЧМ30Т4-02-01']:
            com.opc.connect_bu_di_power(True, 48)
        elif bu.dev_type in ['ЭРЧМ30Т4-03']:
            com.opc.connect_bu_di_power(True, 75)
        else:
            com.opc.connect_bu_di_power(False)
            print(f'Неизвестный тип {bu.dev_type}')


class ConnectBU(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('Производится подключение питания БУ')

        com.opc.connect_bu_power()

        lst = [com.frm_main.check_bu.btn_di, com.frm_main.check_bu.btn_fi, com.frm_main.check_bu.btn_shim,
               com.frm_main.check_bu.btn_ai, com.frm_main.check_bu.btn_rt, com.frm_main.check_bu.btn_prepare_r]
        for e in lst:
            e.setEnabled(True)

        lst = [com.frm_main.check_bu.btn_di_r, com.frm_main.check_bu.btn_fi_r, com.frm_main.check_bu.btn_shim_r]
        for it in lst:
            it.setEnabled(False)

        com.frm_main.check_bu.btn_prepare.state = 'ok'
        bu.prepare = True


class DICheck(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu.di_res = []
        com.do1.setValue([0] * 16 + com.do1.value[16:])
        com.do1.setValue(1, 8)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        com.text.setText('<p>Установите режим <b><font color="blue">"РЕ00"</font></b> на программаторе. '
                         'Для этого удерживайте нажатой кнопку '
                         '1  программатора, а затем кнопками 5 и 6 установите на верхнем индикаторе номер '
                         'режима. После чего отпустите кнопку 1 и нажмите кнопку программатора 2. Кнопками 5 и 6 '
                         'установите номер подрежима.</p>'
                         '<p>Нажмите "ПРИНЯТЬ" для продолжения</p>'
                         )


class DISelectFirst(QtCore.QState):
    type3 = QtCore.pyqtSignal()
    type4 = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com, bu
        com.do1.setValue([0] * 16 + com.do1.value[16:])
        t3 = ['ЭРЧМ30Т3-06', 'ЭРЧМ30Т3-04', 'ЭРЧМ30Т3-07', 'ЭРЧМ30Т3-12', 'ЭРЧМ30Т3-12-01', 'ЭРЧМ30Т3-12-02',
              'ЭРЧМ30Т3-12-03', 'ЭРЧМ30Т3-02', 'ЭРЧМ30Т3-05', 'ЭРЧМ30Т3-08', 'ЭРЧМ30Т3-08-01', 'ЭРЧМ30Т3-10',
              'ЭРЧМ30Т3-10-01']
        t4 = ['ЭРЧМ30Т4-01', 'ЭРЧМ30Т4-02', 'ЭРЧМ30Т4-02-01', 'ЭРЧМ30Т4-03']

        if bu.dev_type in t3:
            bu.di_reg = '62'
            self.type3.emit()
        elif bu.dev_type in t4:
            bu.di_reg = '66'
            self.type4.emit()
        else:
            print(f'Неизвестный тип {bu.dev_type}')


class DI62(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('<p>На нижнем индикаторе необходимо установить адресс 62. '
                         'Для этого кнопкой 4 выбрать разряд, а кнопками 5 и 6 задайть значение. На текущий '
                         'разряд указывает точка.</p><p>После всех манипуляций на индикаторах программатора должно '
                         'быть:<br><br><b><font size="+1" color="green">bn00<br>6200</font></b></p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>')


class DI63(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('<p>На нижнем индикаторе необходимо установить адресс 63. '
                         'Для этого кнопкой 4 выбрать разряд, а кнопками 5 и 6 задайть значение. На текущий '
                         'разряд указывает точка.</p><p>После всех манипуляций на индикаторах программатора должно '
                         'быть:<br><br><b><font size="+1" color="green">bn00<br>6300</font></b></p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>')


class DI66(QtCore.QState):
    def onEntry(self, QEvent):
        com.text.setText('<p>На нижнем индикаторе необходимо установить адресс 66. '
                         'Для этого кнопкой 4 выбрать разряд, а кнопками 5 и 6 задайть значение. На текущий '
                         'разряд указывает точка.</p><p>После всех манипуляций на индикаторах программатора должно '
                         'быть:<br><br><b><font size="+1" color="green">bn00<br>6600</font></b></p><p><br>Нажмите '
                         '"ПРИНЯТЬ" для продолжения</p>')


class DIConfig1(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        if bu.dev_type in ['ЭРЧМ30Т3-06', 'ЭРЧМ30Т3-04', 'ЭРЧМ30Т3-07']:
            com.opc.connect_bu_di_power(True, 110)
            com.args = ((0, '02', 'ДВХ1'),
                        (1, '04', 'ДВХ2'),
                        (2, '08', 'ДВХ3'),
                        (3, '01', 'ДВХ4'),
                        (5, '40', 'ДВХ5 (Упр. от КМ)'),
                        (8, '10', 'ДВХ6 (Работа/стоп)'),
                        (6, '20', 'ДВХ7 (Поезд. реж.)'))
        elif bu.dev_type in ['ЭРЧМ30Т3-12', 'ЭРЧМ30Т3-12-01', 'ЭРЧМ30Т3-12-02', 'ЭРЧМ30Т3-12-03']:
            com.opc.connect_bu_di_power(True, 110)
            com.args = ((0, '02', 'ДВХ1'),
                        (1, '04', 'ДВХ2'),
                        (2, '08', 'ДВХ3'),
                        (3, '01', 'ДВХ4'),
                        (8, '10', 'ДВХ9 (Работа/стоп)'),
                        (6, '20', 'ДВХ7 (Поезд. реж.)'))
        elif bu.dev_type in ['ЭРЧМ30Т3-08', 'ЭРЧМ30Т3-08-01']:
            com.opc.connect_bu_di_power(True, 75)
            com.args = ((0, '02', 'ДВХ1'),
                        (1, '04', 'ДВХ2'),
                        (2, '08', 'ДВХ3'),
                        (3, '01', 'ДВХ4'),
                        (8, '10', 'ДВХ9 (Работа/стоп)'),
                        (6, '20', 'ДВХ7 (Поезд. реж.)'),
                        (9, '40', 'ДВХ10 (Резерв)'),
                        (11, '80', 'ДВХ12 (Резерв)'))
        elif bu.dev_type in ['ЭРЧМ30Т3-02', 'ЭРЧМ30Т3-05', 'ЭРЧМ30Т3-10', 'ЭРЧМ30Т3-10-01']:
            com.opc.connect_bu_di_power(True, 110)
            com.args = ((0, '02', 'ДВХ1'),
                        (1, '04', 'ДВХ2'),
                        (2, '08', 'ДВХ3'),
                        (3, '01', 'ДВХ4'),
                        (8, '10', 'ДВХ9 (Работа/стоп)'),
                        (6, '20', 'ДВХ7 (Поезд. реж.)'),
                        (9, '40', 'ДВХ10 (Резерв)'),
                        (11, '80', 'ДВХ12 (Резерв)'))
        elif bu.dev_type in ['ЭРЧМ30Т4-01']:
            com.opc.connect_bu_di_power(True, 75)
            com.args = ((0, '01', 'ДВХ1'),
                        (1, '02', 'ДВХ2'),
                        (2, '04', 'ДВХ3'),
                        (3, '20', 'ДВХ4'),
                        (5, '10', 'ДВХ5'),
                        (8, '08', 'ДВХ7 (Работа/стоп)'))
        elif bu.dev_type in ['ЭРЧМ30Т4-02']:
            com.opc.connect_bu_di_power(True, 24)
            com.args = ((0, '01', 'ДВХ1'),
                        (1, '02', 'ДВХ2'),
                        (2, '04', 'ДВХ3'),
                        (3, '20', 'ДВХ4'),
                        (5, '10', 'ДВХ5 (Мин. частота'),
                        (8, '08', 'ДВХ6 (Работа/стоп)'),
                        (12, '80', 'ДВХ7 (Работа от КМ)'))
        elif bu.dev_type in ['ЭРЧМ30Т4-02-01']:
            com.opc.connect_bu_di_power(True, 48)
            com.args = ((0, '01', 'ДВХ1'),
                        (1, '02', 'ДВХ2'),
                        (2, '04', 'ДВХ3'),
                        (3, '20', 'ДВХ4'),
                        (5, '10', 'ДВХ5 (Мин. частота'),
                        (8, '08', 'ДВХ6 (Работа/стоп)'),
                        (12, '80', 'ДВХ7 (Работа от КМ)'))
        elif bu.dev_type in ['ЭРЧМ30Т4-03']:
            com.opc.connect_bu_di_power(True, 75)
            com.args = ((0, '01', 'ДВХ1'),
                        (1, '02', 'ДВХ2'),
                        (2, '04', 'ДВХ3'),
                        (3, '20', 'ДВХ4'),
                        (5, '10', 'ДВХ5'),
                        (8, '08', 'ДВХ7 (Работа/стоп)'))
        else:
            print(f'Неизвестный тип {bu.dev_type}')
            com.opc.connect_bu_di_power(False)

        bu.di_min = 0
        bu.di_max = len(com.args)

        if bu.dev_type in ['ЭРЧМ30Т3-12', 'ЭРЧМ30Т3-12-01', 'ЭРЧМ30Т3-12-02', 'ЭРЧМ30Т3-12-03']:
            com.args += ((4, '02', 'ДВХ5 (Букс. 1)'),
                         (5, '04', 'ДВХ6 (Букс. 2)'),
                         (12, '80', 'ДВХ13 (Работа от КМ)'))
        elif bu.dev_type in ['ЭРЧМ30Т3-08', 'ЭРЧМ30Т3-08-01']:
            com.args += ((4, '02', 'ДВХ5 (Букс. 1)'),
                         (5, '04', 'ДВХ6 (Букс. 2)'),
                         (7, '10', 'ДВХ8 (Резерв)'),
                         (10, '01', 'ДВХ11 (Резерв)'),
                         (12, '80', 'ДВХ13 (Работа от КМ)'))
        elif bu.dev_type in ['ЭРЧМ30Т3-02', 'ЭРЧМ30Т3-05', 'ЭРЧМ30Т3-10', 'ЭРЧМ30Т3-10-01']:
            com.args += ((4, '02', 'ДВХ5 (Букс. 1)'),
                         (5, '04', 'ДВХ6 (Букс. 2)'),
                         (7, '10', 'ДВХ8 (Резерв)'),
                         (10, '01', 'ДВХ11 (Резерв)'),
                         (12, '80', 'ДВХ13 (Работа от КМ)'))

        bu.di_res = [0] * len(com.args)
        com.idx = 0


class DIShowTable(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        br2 = 2
        com.freq.setClear(br2)

        com.do1.setValue([0] * 16 + com.do1.value[16:])
        di_in = com.args[com.idx][0]
        com.do1.setValue(True, di_in)

        table_header = '<table ' \
                       'border="1" ' \
                       'style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" ' \
                       'cellspacing="0" ' \
                       'cellpadding="0">'

        table_bottom = '</table>'

        row1 = '<tr><td  width="100">Вход БУ</td>'
        row2 = '<tr><td  width="100">Значение</td>'

        for i in range(bu.di_min, bu.di_max):
            text1 = com.args[i][2]
            text2 = com.args[i][1]
            cell_state = bu.di_res[i]

            if cell_state > 0 and i == com.idx:
                color = '#60c060'
            elif cell_state > 0:
                color = '#80ff80'
            elif cell_state < 0 and i == com.idx:
                color = '#c06060'
            elif cell_state < 0:
                color = '#ff8080'
            elif cell_state == 0 and i == com.idx:
                color = '#c0c0c0'
            else:
                color = '#ffffff'

            cell1 = f'<td width="80" bgcolor="{color}">{text1}</td>'
            cell2 = f'<td width="80" bgcolor="{color}">{bu.di_reg+text2}</td>'

            row1 += cell1
            row2 += cell2
        row1 += '</tr>'
        row2 += '</tr>'

        com.text.setText(f'<p>Для каждого столбца таблицы необходимо проверить совпадают ли '
                         f'показания нижнего индикатора программатора со значениями указанными '
                         f'во второй строке таблицы</p>'
                         f'<p>{table_header}{row1}{row2}{table_bottom}</p>'
                         f'<p>Поворотом валкодера "BR3" можно перемещаться по столбцам таблицы<br>'
                         f'Нажмите кнопку "ВВЕРХ" если значения совпадают<br>'
                         f'Нажмите кнопку "ВНИЗ если значения не совпадают"<br>'
                         f'Нажмите кнопку "ПРИНЯТЬ" для продолжения<br>'
                         f'Нажмите кнопку "НАЗАД" для выхода в меню</p>')


class DIKeyCheck(QtCore.QState):
    next = QtCore.pyqtSignal()
    previous = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        if com.freq.value[2] > 1:
            self.next.emit()
        elif com.freq.value[2] < -1:
            self.previous.emit()


class DIKeyOk(QtCore.QState):
    next = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com, bu

        if com.idx == bu.di_max - 1:
            if bu.di_res[com.idx] == 0:
                bu.di_res[com.idx] = 1
            self.done.emit()
        else:
            bu.di_res[com.idx] = 1
            self.next.emit()


class DISuccess(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu.di_res[com.idx] = 1


class DIFail(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu.di_res[com.idx] = -1


class DINext(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.idx += 1
        if com.idx >= bu.di_max:
            com.idx = bu.di_max - 1


class DIPrevious(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.idx -= 1
        if com.idx < bu.di_min:
            com.idx = bu.di_min


class DISelectSecond(QtCore.QState):
    done = QtCore.pyqtSignal()
    di63 = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com, bu
        com.do1.setValue([0] * 16 + com.do1.value[16:])

        if bu.di_reg == '66':
            self.done.emit()
        elif bu.di_reg == '63':
            self.done.emit()
        elif bu.dev_type in ['ЭРЧМ30Т3-06', 'ЭРЧМ30Т3-04', 'ЭРЧМ30Т3-07']:
            self.done.emit()
        else:
            bu.di_reg = '63'
            self.di63.emit()


class DIConfig2(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu

        bu.di_min = bu.di_max
        bu.di_max = len(com.args)
        com.idx = bu.di_min


class DIResult(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        if -1 in bu.di_res:
            com.frm_main.check_bu.btn_di.state = 'fail'
        elif all(bu.di_res):
            com.frm_main.check_bu.btn_di.state = 'ok'

        bu.di_res = [(com.args[i][2], bu.di_res[i]) for i in range(bu.di_max)]

        ok = [bu.di_res[i][0] for i in range(bu.di_max) if bu.di_res[i][1] > 0]
        fail = [bu.di_res[i][0] for i in range(bu.di_max) if bu.di_res[i][1] < 0]
        pas = [bu.di_res[i][0] for i in range(bu.di_max) if bu.di_res[i][1] == 0]
        ok = ', '.join(ok)
        fail = ', '.join(fail)
        pas = ', '.join(pas)

        res = ''
        if ok:
            res += '<p>Входы прошедшие проверку:<br>'
            res += ok
            res += '</p>'
        if fail:
            res += '<p>Входы провалившие проверку:<br>'
            res += fail
            res += '</p>'
        if pas:
            res += '<p>Проверка была пропущена для входов:<br>'
            res += pas
            res += '</p>'
        res += '<p>Нажмите "ПРИНЯТЬ" для продолжения</p>'
        com.text.setText(res)


class FICheck(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        bu.fi_res = ''
        bu.fi_note = ''
        # com.removeTransition(com.back_transition)
        com.text.setText('<p>Установите на программаторе режим <b><font color="blue">"РЕА0"</font></b>. '
                         'Для этого зажмите кнопку 1 для выбора '
                         'режима или кнопку 2 для выбора подрежима и кнопками 5 и 6 установите значение А0. На '
                         'нижнем ряде индикаторов программатора должно быть: '
                         '<b><font color="green">0124</font></b></p><p></p>'
                         'Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font>,'
                         '<br>Если условие не выполняется нажмите <font color="red">"ВНИЗ"</font>.</p>'
                         )


class FiParamSave(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.text.setText('<p>Кнопками 5 и 6 установите на нижнем ряде индикаторов значение '
                         '<b><font color="green">0124</font></b>.</p><p>После чего удерживая кнопку 1 или кнопку 2 '
                         'кнопками 5 и 6 установите  режим <b><font color="blue">"PEF0"</font></b>. '
                         'Затем нажмите и удерживайте кнопку 3 и '
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
            ('РЕ10', 'верхнего', '0495-0502', 'ЧВХ1 - ДЧД', [1030, 0, 0]),
            ('РЕ9E', 'нижнего', '0995-1005', 'ЧВХ2 - ДЧТК', [0, 1000, 0]),
            ('РЕ70', 'верхнего', '01.00-06.00', 'ЧВХ3 - ДП 25 кГц', [0, 0, 25000]),
            ('РЕ70', 'верхнего', '14.00-25.00', 'ЧВХ3 - ДП 17 кГц', [0, 0, 17000]))


class FiMeasure(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.idx += 1
        if com.idx < len(com.args):
            args = com.args[com.idx]
            com.gen.setValue(args[4])
            com.text.setText('<p>Зажав кнопку программатора 1 или 2 установите при помощи кнопок 5 и 6 '
                             'режим <b><font color="blue">"{}"</font></b>.</p>'
                             '<p>Показания <b>{} ряда</b> индикаторов должны находится в пределах '
                             '<b><font color="green">{}</font></b></p>'
                             '<p>Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font>,'
                             '<br>Если условие не выполняется нажмите <font color="red">"ВНИЗ"</font>.</p>'
                             ''.format(*args))
        else:
            self.done.emit()


class FiFail(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        args = com.args[com.idx]
        bu.fi_res = 'НЕ НОРМА'
        bu.fi_note += 'Неисправен частотный вход {}.;'.format(args[3])


class FiDone(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        # com.addTransition(com.back_transition)
        com.do2.setValue(com.do2.value[:12] + [0, 0, 0] + com.do2.value[15:])
        com.gen.setValue([0, 0, 0])
        if not bu.fi_res:
            bu.fi_res = 'норма'
            com.frm_main.check_bu.btn_fi.state = 'ok'
        else:
            com.frm_main.check_bu.btn_fi.state = 'fail'


class ShimCheck(QtCore.QState):
    def onEntry(self, QEvent):
        com.freq.setActive(False)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        com.frm.arr = []
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
        com.text.setText('<p>Установите на программаторе режим <b><font color="blue">"PE80"</font></b>. '
                         'Для этого зажав кнопку 1 или 2 кнопками'
                         ' 5 и 6 установите требуемое значение режима.</p>'
                         '<p>Нижний ряд индикаторов должен показывать <b><font color="green">"P000"</font></b>'
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
                            ' {:.3f} А, норма: 0,6-0,9 А.;'.format(com.val)
            bu.shim_res = 'НЕ НОРМА'

        com.val = 0
        com.idx = 0
        com.args[0] = '2,1-2,4'
        com.text.setText('<p>Установите при помощи кнопки 6 значение '
                         '<b><font color="green">"P3F8"</font></b> на нижнем индикаторе  программатора.</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>')


class ShimSaveI2(QtCore.QState):
    def onEntry(self, QEvent):
        if 2.4 <= com.val <= 2.55:
            com.val = 2.4
        bu.shim_i2 = com.val
        if not (2.1 <= com.val <= 2.4):
            bu.shim_note += 'Ток в силовой цепи ПЭ при параметре "Р3F8" режима "РЕ80" факт: ' \
                            '{} А, норма: 2,1-2,9 А.;'.format(com.val)
            bu.shim_res = 'НЕ НОРМА'

        com.text.setText('<p>Нажмите и удерживайте кнопку 6 "МЕНЬШЕ" программатора. Значения нижнего ряда '
                         'индикаторов будут уменьшаться.'
                         'При этом будет построен график тока силовой цепи.</p>'
                         )


class ShimGraphStart(QtCore.QState):
    start = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.frm.img.clear()
        com.img.setMinimumHeight(com.frm.GR_HEIGHT)
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
        # com.removeTransition(com.back_transition)
        bu.shim_graph = com.args[:]

        com.text.setText(
            '<p>График должен монотонно уменьшаться. Не должно быть "пиков", '
            '"провалов" и "плато" на всем протяжении графика.</p>'
            '<p>Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font>,'
            '<br>Если условие не выполняется нажмите <font color="red">"ВНИЗ"</font>.</p>')


class ShimFail(QtCore.QState):
    def onEntry(self, QEvent):
        bu.shim_note += 'График тока силовой цепи не соответствует требованиям ТУ.;'
        bu.shim_res = 'НЕ НОРМА'


class ShimFinish(QtCore.QState):
    def onEntry(self, QEvent):
        global com

        com.img.setMinimumHeight(0)
        # com.addTransition(com.back_transition)
        com.do2.setValue(0, 6)  # PA3
        com.opc.connect_bu_di_power(False)
        com.do1.setValue(0, 8)  # work/stop
        if not bu.shim_res:
            bu.shim_res = 'норма'
            com.frm_main.check_bu.btn_shim.state = 'ok'
        else:
            com.frm_main.check_bu.btn_shim.state = 'fail'
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
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>'
                         ''.format(bu.shim_i1, res1, bu.shim_i2, res2, res3))


class ShimRegOff(QtCore.QState):
    def onEntry(self, QEvent):
        com.freq.setActive(True)
        com.text.setText('<p>Установите на программаторе режим <b><font color="blue">"PE10"</font></b>. '
                         'Для этого зажав кнопку 1 или 2 кнопками'
                         ' 5 и 6 установите требуемое значение режима.</p>'
                         '</p><p><br>Нажмите "ПРИНЯТЬ" для выхода в меню</p>'
                         )


class AiCheck(QtCore.QState):
    def onEntry(self, QEvent):
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        # com.removeTransition(com.back_transition)
        bu.ai_res = ''
        bu.ai_note = ''
        bu.ai_res1 = ''
        bu.ai_res2 = ''
        bu.ai_i11 = 0
        bu.ai_i12 = 0
        bu.ai_i21 = 0
        bu.ai_i22 = 0
        com.do2.setValue(1, 15)  # вкл пит. АО
        com.ao.setActive()
        com.freq.setClear(2)
        # com.br3_zero = com.freq.value[2]
        com.val = 0
        com.idx = 0
        com.args = [
            {'v0': 32, 'ch': 'АВХ1.1 - ДДН', 'reg': 'PE91', 'row': 'верхнего', 'val': '0.080', 'norm': '4.45-4.55'},
            {'v0': 960, 'ch': 'АВХ1.2 - ДДН', 'reg': 'PE91', 'row': 'верхнего', 'val': '2.400', 'norm': '19.45-19.55'},
            {'v0': 31, 'ch': 'АВХ2.1 - ДДМ', 'reg': 'PEС0', 'row': 'верхнего', 'val': '00.50', 'norm': '4.45-4.55'},
            {'v0': 969, 'ch': 'АВХ2.2 - ДДМ', 'reg': 'PEС0', 'row': 'верхнего', 'val': '15.50', 'norm': '19.45-19.55'}]


class AIMeasure(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        if com.idx >= len(com.args):
            self.done.emit()
            return
        cur = com.args[com.idx]
        v0 = cur['v0']
        br3 = com.freq.value[2]
        v = br3 + v0
        if v < 0:
            v = 0
        if v > 1000:
            v = 1000
        i = 4 + v * (20 - 4) / 1000
        com.val = i

        com.ao.setValue([v, v] + com.ao.value[2:])

        ch = cur['ch']
        reg = cur['reg']
        row = cur['row']
        val = cur['val']
        norm = cur['norm']

        com.text.setText(f'<p>Для проверки канала {ch} установите на программаторе режим '
                         f'<b><font color="blue">"{reg}"</font></b>. Для этого '
                         'удерживая кнопку 1 или 2 программатора кнопками 5 и 6 установите требуемое '
                         'значение режима.</p>'
                         f'<p>После чего поворотом рукоятки валкодера BR3 установите значение {row} '
                         f'ряда индикаторов в диапазоне <b><font color="green">{val}\u00b10.05</font></b>.</p>'
                         f'<p>Текущее значение тока: {i:5.2f} мА, норма: {norm} мА</p>'
                         '<p><br>Нажмите <font color="green">"ПРИНЯТЬ"</font> для продолжения,<br>'
                         f'Если значение {val} установить не удалось нажмите <font color="red">"ВНИЗ"</font>.</p>'
                         )


class AIFail(QtCore.QState):
    def onEntry(self, QEvent):
        if com.idx == 0:
            bu.ai_i11 = 0
        elif com.idx == 1:
            bu.ai_i12 = 0
        elif com.idx == 2:
            bu.ai_i21 = 0
        elif com.idx == 3:
            bu.ai_i22 = 0
        cur = com.args[com.idx]
        ch = cur['ch']
        val = cur['val']
        bu.ai_note += f'Не удалось проверить канал {ch} для значения {val};'
        com.idx += 1
        com.freq.setClear(2)


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
        com.freq.setClear(2)


class AIRegSwitch(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        if com.idx == 2:
            com.text.setText('<p>Установите на программаторе режим '
                             '<b><font color="blue">"PEС0"</font></b>. Для этого '
                             'удерживая кнопку 1 или 2 программатора кнопками 5 и 6 установите требуемое '
                             'значение режима.</p>'
                             '<p><br>Нажмите <font color="green">"ПРИНЯТЬ"</font> для продолжения.</p>'
                             )
        else:
            self.done.emit()


class AIRes(QtCore.QState):
    def onEntry(self, QEvent):
        # com.addTransition(com.back_transition)
        table_header = '<table ' \
                       'border="1" ' \
                       'style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" ' \
                       'cellspacing="0" ' \
                       'cellpadding="0">' \
                       '<tr>' \
                       '<td  width="200">Параметр</td>' \
                       '<td  width="120">Норма, мА</td>' \
                       '<td  width="120">Факт, мА</td>' \
                       '<td  width="120">Результат</td>' \
                       '</tr>'

        table_bottom = '</table>'

        color_success = '#80ff80'
        color_fail = '#ff8080'
        val = [bu.ai_i11, bu.ai_i12, bu.ai_i21, bu.ai_i22]
        norm = [4.512, 19.36, 4.496, 19.504]
        check = [norm[i] - 0.05 <= val[i] <= norm[i] + 0.05 for i in range(4)]

        row = [''] * 4
        for i in range(4):
            if check[i]:
                res = 'НОРМА'
                color = color_success
            else:
                res = 'НЕ НОРМА'
                color = color_fail

            row[i] = f'<tr>' \
                     f'<td bgcolor="{color}">{com.args[i]["ch"]}</td>' \
                     f'<td bgcolor="{color}">{com.args[i]["norm"]}</td>' \
                     f'<td bgcolor="{color}">{val[i]:5.2f}</td>' \
                     f'<td bgcolor="{color}">{res}</td>' \
                     f'</tr>'

        com.text.setText(f'<p>Резудьтаты испытания аналоговых входов АВХ1 - ДДН и АВХ2 - ДДМ</p>'
                         f'<p>{table_header}'
                         f'{row[0]}'
                         f'{row[1]}'
                         f'{row[2]}'
                         f'{row[3]}'
                         f'{table_bottom}</p>'
                         f'<p><br>Нажмите "ПРИНЯТЬ" для продолжения.</p>')
        if all(check):
            com.frm_main.check_bu.btn_ai.state = 'ok'
        else:
            com.frm_main.check_bu.btn_ai.state = 'fail'


class AIDone(QtCore.QState):
    def onEntry(self, QEvent):
        com.do2.setValue(0, 15)  # выкл пит. АО
        com.ao.setActive(False)


class RtCheck(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.do2.setValue(True, 31)
        bu.ai_3_1 = False
        bu.ai_3_2 = False
        bu.ai_3_3 = False
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        com.text.setText(f'<p>Для проверки канала АВХ3 - датчика температуры установите на программаторе режим '
                         f'<b><font color="blue">"PECB"</font></b>. Для этого '
                         'удерживая кнопку 1 или 2 программатора кнопками 5 и 6 установите требуемое '
                         'значение режима.</p>'
                         f'<p>Показания верхнего ряда индикаторов должны быть '
                         f'<b><font color="green">0000</font></b></p>'
                         '<p><br>Нажмите <font color="green">"ПРИНЯТЬ"</font> для продолжения,<br>'
                         f'Если значение отличается нажмите <font color="red">"ВНИЗ"</font>.</p>'
                         )


class RtFail1(QtCore.QState):
    def onEntry(self, QEvent):
        global bu
        bu.ai_3_1 = False


class RtSuccess1(QtCore.QState):
    def onEntry(self, QEvent):
        global bu
        bu.ai_3_1 = True


class Rt100(QtCore.QState):
    def onEntry(self, QEvent):
        com.do2.setValue(False, 31)
        com.do2.setValue(True, 30)
        com.text.setText(f'<p>Проверка среднего значения. Показания верхнего '
                         f'ряда индикаторов должны быть в диапазоне '
                         f'<b><font color="green">0095 - 0105</font></b>.</p>'
                         '<p><br>Нажмите <font color="green">"ПРИНЯТЬ"</font> для продолжения,<br>'
                         f'Если значение отличается нажмите <font color="red">"ВНИЗ"</font>.</p>'
                         )


class RtFail2(QtCore.QState):
    def onEntry(self, QEvent):
        global bu
        bu.ai_3_2 = False


class RtSuccess2(QtCore.QState):
    def onEntry(self, QEvent):
        global bu
        bu.ai_3_2 = True


class RtMax(QtCore.QState):
    def onEntry(self, QEvent):
        com.do2.setValue(False, 30)
        com.do2.setValue(True, 29)
        com.text.setText(f'<p>Проверка максимального значения. Показания верхнего '
                         f'ряда индикаторов должны быть '
                         f'<b><font color="green">не менее  0100</font></b></p>'
                         '<p><br>Нажмите <font color="green">"ПРИНЯТЬ"</font> для продолжения,<br>'
                         f'Если значение отличается нажмите <font color="red">"ВНИЗ"</font>.</p>'
                         )


class RtFail3(QtCore.QState):
    def onEntry(self, QEvent):
        global bu
        bu.ai_3_3 = False


class RtSuccess3(QtCore.QState):
    def onEntry(self, QEvent):
        global bu
        bu.ai_3_3 = True


class RtRes(QtCore.QState):
    def onEntry(self, QEvent):
        com.do2.setValue(False, 29)
        com.do2.setValue(False, 30)
        com.do2.setValue(False, 31)
        if bu.ai_3_1 and bu.ai_3_2 and bu.ai_3_3:
            com.text.setText('<p>Проверка завершена <b><font color="green">успешно</font></b>.'
                             '<p><br>Нажмите "ПРИНЯТЬ" для продолжения.'
                             )
            com.frm_main.check_bu.btn_rt.state = 'ok'
        else:
            com.text.setText('<p>Канал измерения температуры масла '
                             '<b><font color="red">неисправен или требует настройки</font></b>.'
                             '<p><br>Нажмите "ПРИНЯТЬ" для продолжения.'
                             )
            com.frm_main.check_bu.btn_rt.state = 'fail'


class PrepareR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.opc.connect_bu_di_power(False)
        com.opc.connect_bu_power(False)

        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_bu_prog)
        com.text.setText('<p>Снимите защитную крышку с разъема БУ "РЕЗЕРВНАЯ РАБОТА" и подключите'
                         ' программатор к разъему под ней.</p>'
                         '<p>Переведите переключатель "РЕЗЕРВНАЯ РАБОТА" на БУ в положение "ВКЛ."</p>'
                         '<p>Нажмите "ПРИНЯТЬ" для продолжения.</p>')


class ConnectBUR(QtCore.QState):
    def onEntry(self, QEvent):
        com.opc.connect_bu_di_power(True, 110)

        com.text.setText('Производится подключение питания БУ')
        com.opc.connect_bu_power(True, reserve=True)

        lst = [com.frm_main.check_bu.btn_di, com.frm_main.check_bu.btn_fi, com.frm_main.check_bu.btn_shim,
               com.frm_main.check_bu.btn_ai, com.frm_main.check_bu.btn_rt]
        for it in lst:
            it.setEnabled(False)

        lst = [com.frm_main.check_bu.btn_di_r, com.frm_main.check_bu.btn_fi_r, com.frm_main.check_bu.btn_shim_r]
        for it in lst:
            it.setEnabled(True)

        com.frm_main.check_bu.btn_prepare_r.state = 'ok'


class DICheckR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu.di_res_r = []
        com.do1.setValue([0] * 16 + com.do1.value[16:])
        com.do1.setValue(1, 8)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        com.text.setText('<p>Установите режим <b><font color="blue">"РЕA8"</font></b> на программаторе.</p>'
                         '<p>Работа программатора в резервном режиме немного отличается от обычной. '
                         'Для выбора <b>режима удерживайте кнопку "РЕ"</b> и кнопками 5 и 6 установливайте значение. '
                         'Для выбора <b>подрежима одновременно удерживайте кнопки "РЕ" и "ре"</b> и кнопками 5 и 6 '
                         'установите значение подрежима.</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>'
                         )


class DI29(QtCore.QState):
    def onEntry(self, QEvent):
        com.do1.setValue([0] * 16 + com.do1.value[16:])
        com.do1.setValue(0, 8)
        com.text.setText('<p>На нижнем индикаторе необходимо установить значение '
                         '<b><font color="green">2900</font></b>.</p>'
                         '<p>Работа программатора в резервном режиме немного отличается от обычной. '
                         'Для выбора разряда ипользуйте кнопку "ре", на текущий разряд указывает точка. '
                         'Кнопками 5 и 6 установите в двух первых разрядах нижнего ряда индикаторов значение 29.</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>')


class DIConfigR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        com.do1.setValue([0] * 16 + com.do1.value[16:])
        com.opc.connect_bu_di_power(True, 110)
        com.args = ((0, '02', 'ДВХ1'),
                    (1, '04', 'ДВХ2'),
                    (2, '08', 'ДВХ3'),
                    (3, '01', 'ДВХ4'),
                    (8, '10', 'ДВХ6 (Работа/стоп)'),
                    (6, '20', 'ДВХ7 (Поезд. реж.)'),
                    )

        bu.di_min = 0
        bu.di_max = len(com.args)

        bu.di_res_r = [0] * len(com.args)
        com.idx = 0


class DIShowTableR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        br2 = 2
        com.freq.setClear(br2)

        com.do1.setValue([0] * 16 + com.do1.value[16:])
        di_in = com.args[com.idx][0]
        com.do1.setValue(True, di_in)

        table_header = '<table ' \
                       'border="1" ' \
                       'style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" ' \
                       'cellspacing="0" ' \
                       'cellpadding="0">'

        table_bottom = '</table>'

        row1 = '<tr><td  width="100">Вход БУ</td>'
        row2 = '<tr><td  width="100">Значение</td>'

        for i in range(bu.di_min, bu.di_max):
            text1 = com.args[i][2]
            text2 = com.args[i][1]
            cell_state = bu.di_res_r[i]

            if cell_state > 0 and i == com.idx:
                color = '#60c060'
            elif cell_state > 0:
                color = '#80ff80'
            elif cell_state < 0 and i == com.idx:
                color = '#c06060'
            elif cell_state < 0:
                color = '#ff8080'
            elif cell_state == 0 and i == com.idx:
                color = '#c0c0c0'
            else:
                color = '#ffffff'

            cell1 = f'<td width="80" bgcolor="{color}">{text1}</td>'
            cell2 = f'<td width="80" bgcolor="{color}">{bu.di_reg+text2}</td>'

            row1 += cell1
            row2 += cell2
        row1 += '</tr>'
        row2 += '</tr>'

        com.text.setText(f'<p>Для каждого столбца таблицы необходимо проверить совпадают ли '
                         f'показания нижнего индикатора программатора со значениями указанными '
                         f'во второй строке таблицы</p>'
                         f'<p>{table_header}{row1}{row2}{table_bottom}</p>'
                         f'<p>Поворотом валкодера "BR3" можно перемещаться по столбцам таблицы<br>'
                         f'Нажмите кнопку "ВВЕРХ" если значения совпадают<br>'
                         f'Нажмите кнопку "ВНИЗ если значения не совпадают"<br>'
                         f'Нажмите кнопку "ПРИНЯТЬ" для продолжения<br>'
                         f'Нажмите кнопку "НАЗАД" для выхода в меню</p>')


class DIKeyOkR(QtCore.QState):
    next = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com, bu

        if com.idx == bu.di_max - 1:
            if bu.di_res_r[com.idx] == 0:
                bu.di_res_r[com.idx] = 1
            self.done.emit()
        else:
            bu.di_res_r[com.idx] = 1
            self.next.emit()


class DISuccessR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu.di_res_r[com.idx] = 1


class DIFailR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        bu.di_res_r[com.idx] = -1


class DIResultR(QtCore.QState):
    def onEntry(self, QEvent):
        global com, bu
        if -1 in bu.di_res_r:
            com.frm_main.check_bu.btn_di_r.state = 'fail'
        elif all(bu.di_res):
            com.frm_main.check_bu.btn_di_r.state = 'ok'

        bu.di_res_r = [(com.args[i][2], bu.di_res_r[i]) for i in range(bu.di_max)]

        ok = [bu.di_res_r[i][0] for i in range(bu.di_max) if bu.di_res_r[i][1] > 0]
        fail = [bu.di_res_r[i][0] for i in range(bu.di_max) if bu.di_res_r[i][1] < 0]
        pas = [bu.di_res_r[i][0] for i in range(bu.di_max) if bu.di_res_r[i][1] == 0]
        ok = ', '.join(ok)
        fail = ', '.join(fail)
        pas = ', '.join(pas)

        res = ''
        if ok:
            res += '<p>Входы прошедшие проверку:<br>'
            res += ok
            res += '</p>'
        if fail:
            res += '<p>Входы провалившие проверку:<br>'
            res += fail
            res += '</p>'
        if pas:
            res += '<p>Проверка была пропущена для входов:<br>'
            res += pas
            res += '</p>'
        res += '<p>Нажмите "ПРИНЯТЬ" для продолжения</p>'
        com.text.setText(res)


class FICheckR(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        bu.fi_res_r = ''
        bu.fi_note_r = ''
        com.text.setText('<p>Установите на программаторе режим <b><font color="blue">"РЕ70"</font></b>.</p>'
                         '<p>Работа программатора в резервном режиме немного отличается от обычной. '
                         'Для выбора <b>режима удерживайте кнопку "РЕ"</b> и кнопками 5 и 6 установливайте значение режима. '
                         'Для выбора <b>подрежима одновременно удерживайте кнопки "РЕ" и "ре"</b> и кнопками 5 и 6 '
                         'установите значение подрежима.</p>'
                         '<p>На нижнем ряде индикаторов программатора должно быть: '
                         '<b><font color="green">0124</font></b></p><p></p>'
                         'Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font>,'
                         '<br>Если условие не выполняется нажмите <font color="red">"ВНИЗ"</font>.</p>'
                         )


class FiConfigR(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.do2.setValue(com.do2.value[:12] + [1, 1, 1] + com.do2.value[15:])
        com.idx = -1
        com.args = (
            ('РЕ00', 'верхнего', '0495-0502', 'ЧВХ1 - ДЧД (рез.)', [1030, 0, 0]),)


class FiFailR(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        args = com.args[com.idx]
        bu.fi_res_r = 'НЕ НОРМА'
        bu.fi_note_r += f'Неисправен частотный вход {args[3]}.;'


class FiDoneR(QtCore.QState):
    def onEntry(self, QEvent):
        global com
        com.do2.setValue(com.do2.value[:12] + [0, 0, 0] + com.do2.value[15:])
        com.gen.setValue([0, 0, 0])
        if not bu.fi_res_r:
            bu.fi_res = 'норма'
            com.frm_main.check_bu.btn_fi_r.state = 'ok'
        else:
            com.frm_main.check_bu.btn_fi_r.state = 'fail'


class ShimCheckR(QtCore.QState):
    def onEntry(self, QEvent):
        com.frm.img.clear()
        com.frm.arr = []
        com.freq.setActive(False)
        com.frm_main.disconnectmenu()
        com.frm_main.stl.setCurrentWidget(com.frm)
        com.img.setPixmap(com.frm.img_prog2)
        bu.shim_res_r = ''
        bu.shim_note_r = ''
        com.args = ['0,6-0,9', 0, 0]
        com.idx = 0
        com.val = 0
        bu.shim_i1_r = 0
        bu.shim_i2_r = 0
        bu.shim_res1_r = ''
        bu.shim_res2_r = ''
        bu.shim_res3_r = ''
        com.pa3.setActive()
        com.text.setText('<p>Установите на программаторе режим <b><font color="blue">"PE80"</font></b>. '
                         '<p>Работа программатора в резервном режиме немного отличается от обычной. '
                         'Для выбора <b>режима удерживайте кнопку "РЕ"</b> и кнопками 5 и 6 установливайте значение. '
                         'Для выбора <b>подрежима одновременно удерживайте кнопки "РЕ" и "ре"</b> и кнопками 5 и 6 '
                         'установите значение подрежима.</p>'
                         '<p>Нижний ряд индикаторов должен показывать <b><font color="green">"0000"</font></b>'
                         '</p><p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>'
                         )

        com.do2.setValue(1, 6)  # PA3
        if com.dev_type == 'ЭРЧМ30T3-06':
            com.opc.connect_bu_di_power(True, 110)
            com.do1.setValue(0, 8)  # work/stop


class ShimSaveI1R(QtCore.QState):
    def onEntry(self, QEvent):
        if 0.9 <= com.val <= 1.05:
            com.val = 0.9
        bu.shim_i1_r = com.val
        if not (0.6 <= com.val <= 0.9):
            bu.shim_note_r += 'Минимальный ток в силовой цепи платы резервирования факт:' \
                              ' {:.3f} А, норма: 0,6-0,9 А.;'.format(com.val)
            bu.shim_res_r = 'НЕ НОРМА'

        com.val = 0
        com.idx = 0
        com.args[0] = '2,1-2,4'
        com.text.setText('<p>Установите при помощи кнопки 6 значение '
                         '<b><font color="green">"1023"</font></b> (или максимально возможное значение) '
                         'на нижнем индикаторе программатора. </p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>')


class ShimSaveI2R(QtCore.QState):
    def onEntry(self, QEvent):
        if 2.4 <= com.val <= 2.55:
            com.val = 2.4
        bu.shim_i2_r = com.val
        if not (2.1 <= com.val <= 2.4):
            bu.shim_note_r += 'Максимальный ток в силовой цепи платы резервирования факт: ' \
                              '{} А, норма: 2,1-2,9 А.;'.format(com.val)
            bu.shim_res_r = 'НЕ НОРМА'

        com.text.setText('<p>Нажмите и удерживайте кнопку 6 "МЕНЬШЕ" программатора. Значения нижнего ряда '
                         'индикаторов будут уменьшаться.'
                         'При этом будет построен график тока силовой цепи.</p>'
                         )


class ShimGraphStartR(QtCore.QState):
    start = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        global com
        com.frm.img.clear()
        com.img.setMinimumHeight(com.frm.GR_HEIGHT)
        com.args = [(0, abs(com.pa3.value))]
        com.frm.arr = com.args
        com.frm.img.update()
        com.t1 = time.perf_counter()
        if abs(com.pa3.value) < bu.shim_i2_r - 0.01:
            self.start.emit()


class ShimGraphR(QtCore.QState):
    done = QtCore.pyqtSignal()

    def onEntry(self, QEvent):
        com.t2 = time.perf_counter()
        dt = com.t2 - com.t1
        v = abs(com.pa3.value)
        com.args.append((dt, v))
        com.text.setText('<p>График тока силовой цепи.</p>'
                         '<p>Текущее значение тока {:5.3f} А, с начала испытания прошло {:.1f} с.</p>'
                         ''.format(v, dt))
        if dt > 50 or v < bu.shim_i1_r + 0.05:
            self.done.emit()
        com.frm.arr = com.args
        com.frm.img.update()


class ShimGraphFinishR(QtCore.QState):
    def onEntry(self, QEvent):
        bu.shim_graph_r = com.args[:]

        com.text.setText(
            '<p>График должен монотонно уменьшаться. Не должно быть "пиков", '
            '"провалов" и "плато" на всем протяжении графика.</p>'
            '<p>Если это условие выполняется нажмите <font color="green">"ПРИНЯТЬ"</font>,'
            '<br>Если условие не выполняется нажмите <font color="red">"ВНИЗ"</font>.</p>')


class ShimFailR(QtCore.QState):
    def onEntry(self, QEvent):
        bu.shim_note_r += 'График тока силовой цепи не соответствует требованиям ТУ.;'
        bu.shim_res_r = 'НЕ НОРМА'


class ShimFinishR(QtCore.QState):
    def onEntry(self, QEvent):
        global com

        com.img.setMinimumHeight(0)
        com.do2.setValue(0, 6)  # PA3
        com.opc.connect_bu_di_power(False)
        com.do1.setValue(0, 8)  # work/stop
        if not bu.shim_res_r:
            bu.shim_res_r = 'норма'
            com.frm_main.check_bu.btn_shim_r.state = 'ok'
        else:
            com.frm_main.check_bu.btn_shim_r.state = 'fail'
        com.pa3.setActive(False)

        if 0.6 <= bu.shim_i1_r <= 0.9:
            bu.shim_res1_r = 'норма'
            res1 = '<font color="green">норма</font>'
        else:
            bu.shim_res1_r = 'НЕ НОРМА'
            res1 = '<font color="red">НЕ НОРМА</font>'

        if 2.1 <= bu.shim_i2_r <= 2.4:
            res2 = '<font color="green">норма</font>'
            bu.shim_res2_r = 'норма'
        else:
            res2 = '<font color="red">НЕ НОРМА</font>'
            bu.shim_res2_r = 'НЕ НОРМА'

        if not bu.shim_note_r.count('График'):
            res3 = '<font color="green">норма</font>'
            bu.shim_res3_r = 'норма'
        else:
            res3 = '<font color="red">НЕ НОРМА {}</font>'
            bu.shim_res3_r = 'НЕ НОРМА'

        com.frm.arr = []
        com.text.setText('<p>Результаты проверки силового канала платы резервирования:</p>'
                         '<p>Минимальный ток - факт: {:5.3f} А, норма: 0,6-0,9 А, результат: {}<br>'
                         'Максимальный ток - факт: {:5.3f} А, норма: 2,1-2,4 А, результат: {}<br>'
                         'Монотонность графика: {}</p>'
                         '<p><br>Нажмите "ПРИНЯТЬ" для продолжения</p>'
                         ''.format(bu.shim_i1_r, res1, bu.shim_i2_r, res2, res3))


class Protocol(QtCore.QState):
    num: int = 0

    def onEntry(self, QEvent):
        global com, bu
        settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        protocol_path = Path(settings.value('protocol/path', 'c:\\протоколы\\'))
        last_date = settings.value('protocol/date', '01-01-2019')
        self.num = settings.value('protocol/num', 0, int)
        today = datetime.datetime.today()
        month = int(str(last_date).split('-')[1])
        if month != today.month:
            self.num = 0
        self.num += 1
        protocol_path = protocol_path.joinpath(f'{today.year:0>4}-{today.month:0>2}\\')

        if not protocol_path.exists():
            protocol_path.mkdir(parents=True, exist_ok=True)
        protocol_path = protocol_path.joinpath(
            f'N {self.num} {today.day:0>2}-{today.month:0>2}-{today.year:0>4} ИУ {bu.dev_type} завN'
            f' {com.frm_main.auth.num} {com.frm_main.auth.date}.pdf')

        com.frm_print.updatePreview()
        com.frm_main.stl.setCurrentWidget(com.frm_print)
        wr = QtGui.QPdfWriter(protocol_path)
        self.preview(wr)

        settings.setValue('protocol/num', self.num)
        settings.setValue('protocol/date', today.strftime('%d-%m-%Y'))

    def preview(self, printer):
        SPACE = 62
        # V_SPACE = 20

        layout = QtGui.QPageLayout()
        layout.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        layout.setOrientation(QtGui.QPageLayout.Portrait)
        # layout.setMargins(20, 10, 5, 15, QtPrintSupport.QPrinter.Millimeter)
        printer.setPageLayout(layout)
        printer.setResolution(300)
        painter = QtGui.QPainter()

        painter.begin(printer)
        color = QtGui.QColor(QtCore.Qt.black)
        pen = QtGui.QPen(color)
        brush = QtGui.QBrush(color)
        font = QtGui.QFont('Segoi ui', 10)
        header_font = QtGui.QFont('Segoi ui', 14)
        painter.setPen(pen)
        painter.setBrush(brush)
        protocol_num = self.num
        protocol_date = datetime.datetime.today().strftime('%d-%m-%Y')

        # Заголовок
        # x, y = 200, 30
        x, y = 625, 94
        painter.setFont(header_font)
        painter.drawText(x, y, f'Протокол испытания № {protocol_num: <3d} от  {protocol_date}')
        painter.setFont(font)
        # Шапка
        # x = 50
        x = 156
        y += SPACE * 2.5
        painter.drawText(x, y, f'Тип исполнительного устройства: {iu.dev_type}')
        y += SPACE
        painter.drawText(x, y, f'Зав. № {frm_main.auth.num}     Дата изготовления: {frm_main.auth.date}')
        y += SPACE
        painter.drawText(x, y, f'Тепловоз № {frm_main.auth.locomotive}     Секция: {frm_main.auth.section}')
        # Шапка таблицы
        y += SPACE * 1.5
        # w = [0, 400, 520, 620]
        w = [0, 1250, 1625, 1937]

