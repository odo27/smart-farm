import sys
import random
import decimal
import datetime
import statistics
import psycopg2
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QProgressBar, QPushButton, QInputDialog, QRadioButton, QGroupBox, QComboBox, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Update(QThread):

    def setdata(self, sensorid_ic, median_ic, error_ic, straight_ic, shift_ic, table, sensorid, median, error_min, error_max, shift_a, shift_b, graph_sensorid):
        self.sensorid_ic = sensorid_ic
        self.median_ic = median_ic
        self.error_ic = error_ic
        self.straight_ic = straight_ic
        self.shift_ic = shift_ic
        self.table = table
        self.sensorid = [graph_sensorid]
        self.median = median
        self.error_min = error_min
        self.error_max = error_max
        self.shift_a = shift_a
        self.shift_b = shift_b
        self.graph_sensorid = graph_sensorid
        self.conn = psycopg2.connect('host=xxx.xxx.xx.xx dbname=xxxxxxxxx user=xxxxxxxx password=xxxxxxxxxx')
        self.cur = self.conn.cursor()
    
    def run(self):
        while True:
            if self.sensorid != []:
                for i in self.sensorid:
                    self.cur.execute("select * from sensingvalues where sensorid = %s order by regdate desc;" % i)
                    globals()['sensorid{0}'.format(i)] = self.cur.fetchall()
            else:
                return

            for i in self.sensorid:
                data = []
                self.cur.execute("select * from %s where sensorid = %s order by regdate desc limit 1;" % (self.table, i))
                file_date = self.cur.fetchone()
                if file_date == None:
                    pass
                else:
                    for j in globals()['sensorid{0}'.format(i)]:
                        if j[1] > file_date[1] - datetime.timedelta(days=3):
                            data.append(j)
                    globals()['sensorid{0}'.format(i)] = data

            if self.median_ic:
                if self.median != '':
                    for i in self.sensorid:
                        for j in globals()['sensorid{0}'.format(i)]:
                            median_list = []
                            median_index = globals()['sensorid{0}'.format(i)].index(j)
                            median_index_tmp = globals()['sensorid{0}'.format(i)].index(j)
                            if median_index + int(self.median) > len(globals()['sensorid{0}'.format(i)]):
                                break
                            for k in range(int(self.median)):
                                median_list.append(globals()['sensorid{0}'.format(i)][median_index_tmp][3])
                                median_index_tmp += 1
                            globals()['sensorid{0}'.format(i)][median_index] = list(globals()['sensorid{0}'.format(i)][median_index])
                            globals()['sensorid{0}'.format(i)][median_index][3] = statistics.median(median_list)
                            globals()['sensorid{0}'.format(i)][median_index] = tuple(globals()['sensorid{0}'.format(i)][median_index])

            if self.straight_ic:
                for i in self.sensorid:
                    data_x = []
                    data_y = []
                    data_range = []
                    data_range2 = []
                    data_selected = []
                    data_selected2 = []
                    data_selected3 = []
                    for j in globals()['sensorid{0}'.format(i)]:
                        data_x.append(j[1])
                        data_y.append(j[3])
                    for k in data_x:
                        if data_range2 == []:
                            data_range2.append([k, data_y[data_x.index(k)]])
                        elif k.date() == data_range2[-1][0].date(): 
                            data_range2.append([k, data_y[data_x.index(k)]])
                        else:
                            data_range.append(data_range2)
                            data_range2 = []
                            data_range2.append([k, data_y[data_x.index(k)]])
                    for j in data_range:
                        data_range3 = []
                        for k in j:
                            data_range3.append(k[1])
                        data_selected.append(data_range3.index(min(data_range3)))
                    count = 0
                    for j in data_selected:
                        data_selected2.append(data_range[count][j][0])
                        count += 1
                    for j in data_selected2:
                        for k in data_x:
                            if j == k:
                                data_selected3.append([k, data_y[data_x.index(k)]])
                    m = 0
                    while m < len(data_selected3) - 1:
                        if data_selected3[m][1] > data_selected3[m+1][1]:
                            n = data_x.index(data_selected3[m][0])
                            while n < data_x.index(data_selected3[m+1][0]):
                                data_y[n] = data_y[n] + (data_selected3[m+1][1] - data_selected3[m][1]) / decimal.Decimal((data_selected3[m][0] - data_selected3[m+1][0]).days*86400 + (data_selected3[m][0] - data_selected3[m+1][0]).seconds) * decimal.Decimal((data_x[n] - data_selected3[m+1][0]).days*86400 + (data_x[n] - data_selected3[m+1][0]).seconds) - data_selected3[m+1][1]
                                n += 1
                        if data_selected3[m][1] < data_selected3[m+1][1]:
                            n = data_x.index(data_selected3[m][0])
                            while n < data_x.index(data_selected3[m+1][0]):
                                data_y[n] = data_y[n] - (data_selected3[m+1][1] - data_selected3[m][1]) / decimal.Decimal((data_selected3[m][0] - data_selected3[m+1][0]).days*86400 + (data_selected3[m][0] - data_selected3[m+1][0]).seconds) * decimal.Decimal((data_selected3[m][0] - data_x[n]).days*86400 + (data_selected3[m][0] - data_x[n]).seconds) - data_selected3[m][1]
                                n += 1
                        m += 1
                    cnt = 0
                    for j in data_y:
                        globals()['sensorid{0}'.format(i)][cnt] = list(globals()['sensorid{0}'.format(i)][cnt])
                        globals()['sensorid{0}'.format(i)][cnt][3] = j
                        globals()['sensorid{0}'.format(i)][cnt] = tuple(globals()['sensorid{0}'.format(i)][cnt])
                        cnt += 1

            if self.shift_ic:
                if self.shift_a != '':
                    if self.shift_b != '':
                        for i in self.sensorid:
                            for j in globals()['sensorid{0}'.format(i)]:
                                shift_index = globals()['sensorid{0}'.format(i)].index(j)
                                globals()['sensorid{0}'.format(i)][shift_index] = list(globals()['sensorid{0}'.format(i)][shift_index])
                                globals()['sensorid{0}'.format(i)][shift_index][3] = decimal.Decimal(float(self.shift_a)) * j[3] + decimal.Decimal(float(self.shift_b))
                                globals()['sensorid{0}'.format(i)][shift_index] = tuple(globals()['sensorid{0}'.format(i)][shift_index])

            for i in self.sensorid:
                for j in globals()['sensorid{0}'.format(i)]:
                    if j[3] < 0:
                        index = globals()['sensorid{0}'.format(i)].index(j)
                        globals()['sensorid{0}'.format(i)][index] = list(globals()['sensorid{0}'.format(i)][index])
                        globals()['sensorid{0}'.format(i)][index][3] = decimal.Decimal(0)
                        globals()['sensorid{0}'.format(i)][index] = tuple(globals()['sensorid{0}'.format(i)][index])

            if self.error_ic:
                if self.error_min != '':
                    if self.error_max != '':
                        for i in self.sensorid:
                            for j in globals()['sensorid{0}'.format(i)]:
                                error_index = globals()['sensorid{0}'.format(i)].index(j)
                                if error_index+1 == len(globals()['sensorid{0}'.format(i)]):
                                    break
                                if globals()['sensorid{0}'.format(i)][error_index][3] == globals()['sensorid{0}'.format(i)][error_index+1][3]:
                                    globals()['sensorid{0}'.format(i)][error_index] = list(globals()['sensorid{0}'.format(i)][error_index])
                                    globals()['sensorid{0}'.format(i)][error_index][3] += decimal.Decimal(float(self.error_min) + random.random() * (float(self.error_max) - float(self.error_min)))
                                    globals()['sensorid{0}'.format(i)][error_index] = tuple(globals()['sensorid{0}'.format(i)][error_index])      

            if file_date == None:
                pass
            else:
                for i in self.sensorid:
                    data = []
                    for j in globals()['sensorid{0}'.format(i)]:
                        if file_date[1] < j[1]:
                            data.append(j)
                    globals()['sensorid{0}'.format(i)] = data

            query = "insert into "+self.table+" (sensorid, regdate, channel, svalue, value2, value1, dup, dac, sensingtype, realdate, suba, subb) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            for i in self.sensorid:
                for j in globals()['sensorid{0}'.format(i)]:
                    self.cur.execute(query, j)
            self.conn.commit()
            self.sleep(30)


class Graph(QThread):

    def setdata(self, sensorid_ic, median_ic, error_ic, straight_ic, shift_ic, table, sensorid, median, error_min, error_max, shift_a, shift_b, graph_sensorid, graph_start, graph_finish):
        self.sensorid_ic = sensorid_ic
        self.median_ic = median_ic
        self.error_ic = error_ic
        self.straight_ic = straight_ic
        self.shift_ic = shift_ic
        self.table = table
        self.sensorid = [graph_sensorid]
        self.median = median
        self.error_min = error_min
        self.error_max = error_max
        self.shift_a = shift_a
        self.shift_b = shift_b
        self.graph_sensorid = graph_sensorid
        self.graph_start = graph_start
        self.graph_finish = graph_finish
        self.conn = psycopg2.connect('host=xxx.xxx.xx.xx dbname=xxxxxxxxx user=xxxxxxxx password=xxxxxxxxxx')
        self.cur = self.conn.cursor()
    
    def run(self):
        if self.sensorid != []:
            for i in self.sensorid:
                self.cur.execute("select * from sensingvalues where sensorid = %s order by regdate desc;" % i)
                globals()['sensorid{0}'.format(i)] = self.cur.fetchall()
        else:
            return
        
        start_year = int(self.graph_start.split('-')[0])
        start_month = int(self.graph_start.split('-')[1])
        start_day = int(self.graph_start.split('-')[2])
        finish_year = int(self.graph_finish.split('-')[0])
        finish_month = int(self.graph_finish.split('-')[1])
        finish_day = int(self.graph_finish.split('-')[2])

        data = []
        for i in self.sensorid:
            for j in globals()['sensorid{0}'.format(i)]:
                if  datetime.date(start_year, start_month, start_day) - datetime.timedelta(days=3) < j[1].date() < datetime.date(finish_year, finish_month, finish_day) + datetime.timedelta(days=3):
                    data.append(j)
            globals()['sensorid{0}'.format(i)] = data
        if self.median_ic:
            if self.median != '':
                for i in self.sensorid:
                    for j in globals()['sensorid{0}'.format(i)]:
                        median_list = []
                        median_index = globals()['sensorid{0}'.format(i)].index(j)
                        median_index_tmp = globals()['sensorid{0}'.format(i)].index(j)
                        if median_index + int(self.median) > len(globals()['sensorid{0}'.format(i)]):
                            break
                        for k in range(int(self.median)):
                            median_list.append(globals()['sensorid{0}'.format(i)][median_index_tmp][3])
                            median_index_tmp += 1
                        globals()['sensorid{0}'.format(i)][median_index] = list(globals()['sensorid{0}'.format(i)][median_index])
                        globals()['sensorid{0}'.format(i)][median_index][3] = statistics.median(median_list)
                        globals()['sensorid{0}'.format(i)][median_index] = tuple(globals()['sensorid{0}'.format(i)][median_index])
        
        if self.straight_ic:
            for i in self.sensorid:
                data_x = []
                data_y = []
                data_range = []
                data_range2 = []
                data_selected = []
                data_selected2 = []
                data_selected3 = []
                for j in globals()['sensorid{0}'.format(i)]:
                    data_x.append(j[1])
                    data_y.append(j[3])
                for k in data_x:
                    if data_range2 == []:
                        data_range2.append([k, data_y[data_x.index(k)]])
                    elif k.date() == data_range2[-1][0].date(): 
                        data_range2.append([k, data_y[data_x.index(k)]])
                    else:
                        data_range.append(data_range2)
                        data_range2 = []
                        data_range2.append([k, data_y[data_x.index(k)]])
                for j in data_range:
                    data_range3 = []
                    for k in j:
                        data_range3.append(k[1])
                    data_selected.append(data_range3.index(min(data_range3)))
                count = 0
                for j in data_selected:
                    data_selected2.append(data_range[count][j][0])
                    count += 1
                for j in data_selected2:
                    for k in data_x:
                        if j == k:
                            data_selected3.append([k, data_y[data_x.index(k)]])
                m = 0
                while m < len(data_selected3) - 1:
                    if data_selected3[m][1] > data_selected3[m+1][1]:
                        n = data_x.index(data_selected3[m][0])
                        while n < data_x.index(data_selected3[m+1][0]):
                            data_y[n] = data_y[n] + (data_selected3[m+1][1] - data_selected3[m][1]) / decimal.Decimal((data_selected3[m][0] - data_selected3[m+1][0]).days*86400 + (data_selected3[m][0] - data_selected3[m+1][0]).seconds) * decimal.Decimal((data_x[n] - data_selected3[m+1][0]).days*86400 + (data_x[n] - data_selected3[m+1][0]).seconds) - data_selected3[m+1][1]
                            n += 1
                    if data_selected3[m][1] <= data_selected3[m+1][1]:
                        n = data_x.index(data_selected3[m][0])
                        while n < data_x.index(data_selected3[m+1][0]):
                            data_y[n] = data_y[n] - (data_selected3[m+1][1] - data_selected3[m][1]) / decimal.Decimal((data_selected3[m][0] - data_selected3[m+1][0]).days*86400 + (data_selected3[m][0] - data_selected3[m+1][0]).seconds) * decimal.Decimal((data_selected3[m][0] - data_x[n]).days*86400 + (data_selected3[m][0] - data_x[n]).seconds) - data_selected3[m][1]
                            n += 1
                    m += 1
                cnt = 0
                for j in data_y:
                    globals()['sensorid{0}'.format(i)][cnt] = list(globals()['sensorid{0}'.format(i)][cnt])
                    globals()['sensorid{0}'.format(i)][cnt][3] = j
                    globals()['sensorid{0}'.format(i)][cnt] = tuple(globals()['sensorid{0}'.format(i)][cnt])
                    cnt += 1
                           
        if self.shift_ic:
            if self.shift_a != '':
                if self.shift_b != '':
                    for i in self.sensorid:
                        for j in globals()['sensorid{0}'.format(i)]:
                            shift_index = globals()['sensorid{0}'.format(i)].index(j)
                            globals()['sensorid{0}'.format(i)][shift_index] = list(globals()['sensorid{0}'.format(i)][shift_index])
                            globals()['sensorid{0}'.format(i)][shift_index][3] = decimal.Decimal(float(self.shift_a)) * j[3] + decimal.Decimal(float(self.shift_b))
                            globals()['sensorid{0}'.format(i)][shift_index] = tuple(globals()['sensorid{0}'.format(i)][shift_index])

        for i in self.sensorid:
            for j in globals()['sensorid{0}'.format(i)]:
                if j[3] < 0:
                    index = globals()['sensorid{0}'.format(i)].index(j)
                    globals()['sensorid{0}'.format(i)][index] = list(globals()['sensorid{0}'.format(i)][index])
                    globals()['sensorid{0}'.format(i)][index][3] = decimal.Decimal(0)
                    globals()['sensorid{0}'.format(i)][index] = tuple(globals()['sensorid{0}'.format(i)][index])

        if self.error_ic:
            if self.error_min != '':
                if self.error_max != '':
                    for i in self.sensorid:
                        for j in globals()['sensorid{0}'.format(i)]:
                            error_index = globals()['sensorid{0}'.format(i)].index(j)
                            if error_index+1 == len(globals()['sensorid{0}'.format(i)]):
                                break
                            if globals()['sensorid{0}'.format(i)][error_index][3] == globals()['sensorid{0}'.format(i)][error_index+1][3]:
                                globals()['sensorid{0}'.format(i)][error_index] = list(globals()['sensorid{0}'.format(i)][error_index])
                                globals()['sensorid{0}'.format(i)][error_index][3] += decimal.Decimal(float(self.error_min) + random.random() * (float(self.error_max) - float(self.error_min)))
                                globals()['sensorid{0}'.format(i)][error_index] = tuple(globals()['sensorid{0}'.format(i)][error_index])  
            
        i = self.graph_sensorid
        graph_x = []
        graph_y = []
        for j in globals()['sensorid{0}'.format(i)]:
            if datetime.date(start_year, start_month, start_day) - datetime.timedelta(days=1) < j[1].date() < datetime.date(finish_year, finish_month, finish_day) + datetime.timedelta(days=1):
                graph_x.append(j[1])
                graph_y.append(j[3])
        
        ex.fig.clear()
        ax = ex.fig.add_subplot(1,1,1)
        ax.plot(graph_x, graph_y)
        ex.canvas.draw()


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.thread_update = Update()
        self.thread_graph = Graph()


        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.canvas)


        self.language_group = QGroupBox('Language')

        self.language = 'eng'
        self.language_btn_eng = QRadioButton('English')
        self.language_btn_eng.clicked.connect(self.language_btn_eng_clicked)
        self.language_btn_eng.setChecked(True)
        self.language_btn_kor = QRadioButton('한국어')
        self.language_btn_kor.clicked.connect(self.language_btn_kor_clicked)

        language_group_layout = QHBoxLayout()
        language_group_layout.addWidget(self.language_btn_eng)
        language_group_layout.addWidget(self.language_btn_kor)
        self.language_group.setLayout(language_group_layout)


        self.file_group = QGroupBox('File')

        self.file_box = QComboBox()
        #table = self.search_table()
        #for i in table:
        #    self.file_box.addItem(i)

        self.file_btn_create = QPushButton('Create')
        self.file_btn_create.clicked.connect(self.file_btn_create_clicked)
        self.file_btn_delete = QPushButton('Delete')
        self.file_btn_delete.clicked.connect(self.file_btn_delete_clicked)
        file_btn_layout = QHBoxLayout()
        file_btn_layout.addWidget(self.file_btn_create)
        file_btn_layout.addWidget(self.file_btn_delete)

        file_group_layout = QVBoxLayout()
        file_group_layout.addWidget(self.file_box)
        file_group_layout.addLayout(file_btn_layout)
        self.file_group.setLayout(file_group_layout)

        self.sensorid_group = QGroupBox('Sensorid')

        self.sensorid = []
        self.sensorid_btn = QPushButton('Type')
        self.sensorid_btn.clicked.connect(self.sensorid_btn_clicked)

        self.sensorid_group_layout = QVBoxLayout()
        self.sensorid_group_layout.addWidget(self.sensorid_btn)
        self.sensorid_group.setLayout(self.sensorid_group_layout)


        self.median_group = QGroupBox('Median')
        self.median_group.setCheckable(True)
        self.median_group.setChecked(False)
        
        self.unit_number = ''
        self.unit_number_lbl = QLabel('Unit number: ')
        self.unit_number_lbl.setAlignment(Qt.AlignCenter)
        self.unit_number_btn = QPushButton('Type')
        self.unit_number_btn.clicked.connect(self.unit_number_btn_clicked)

        median_group_layout = QHBoxLayout()
        median_group_layout.addWidget(self.unit_number_lbl)
        median_group_layout.addWidget(self.unit_number_btn)
        self.median_group.setLayout(median_group_layout)


        self.error_group = QGroupBox('Error')
        self.error_group.setCheckable(True)
        self.error_group.setChecked(False)

        self.error_min = ''
        self.error_min_lbl = QLabel()
        self.error_min_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl = QLabel(' < error < ')
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_max = ''
        self.error_max_lbl = QLabel()
        self.error_max_lbl.setAlignment(Qt.AlignCenter)
        self.error_min_btn = QPushButton('min')
        self.error_min_btn.clicked.connect(self.error_min_btn_clicked)
        self.error_max_btn = QPushButton('max')
        self.error_max_btn.clicked.connect(self.error_max_btn_clicked)
        
        error_lbl_layout = QHBoxLayout()
        error_lbl_layout.addWidget(self.error_min_lbl)
        error_lbl_layout.addWidget(self.error_lbl)
        error_lbl_layout.addWidget(self.error_max_lbl)

        error_btn_layout = QHBoxLayout()
        error_btn_layout.addWidget(self.error_min_btn)
        error_btn_layout.addWidget(self.error_max_btn)

        error_group_layout = QVBoxLayout()
        error_group_layout.addLayout(error_lbl_layout)
        error_group_layout.addLayout(error_btn_layout)
        self.error_group.setLayout(error_group_layout)


        self.straight_group = QGroupBox('Straight')
        self.straight_group.setCheckable(True)
        self.straight_group.setChecked(False)


        self.shift_group = QGroupBox('Shift')
        self.shift_group.setCheckable(True)
        self.shift_group.setChecked(False)

        self.shift_lbl = QLabel('ax+b')
        self.shift_lbl.setAlignment(Qt.AlignCenter)
        self.shift_a = ''
        self.shift_a_lbl = QLabel('x ')
        self.shift_a_lbl.setAlignment(Qt.AlignCenter)
        self.shift_a_btn = QPushButton('a')
        self.shift_a_btn.clicked.connect(self.shift_a_btn_clicked)
        self.shift_b = ''
        self.shift_b_lbl = QLabel('+ ')
        self.shift_b_lbl.setAlignment(Qt.AlignCenter)
        self.shift_b_btn = QPushButton('b')
        self.shift_b_btn.clicked.connect(self.shift_b_btn_clicked)

        shift_a_layout = QHBoxLayout()
        shift_a_layout.addWidget(self.shift_a_lbl)
        shift_a_layout.addWidget(self.shift_a_btn)
        shift_b_layout = QHBoxLayout()
        shift_b_layout.addWidget(self.shift_b_lbl)
        shift_b_layout.addWidget(self.shift_b_btn)

        shift_group_layout = QVBoxLayout()
        shift_group_layout.addWidget(self.shift_lbl)
        shift_group_layout.addLayout(shift_a_layout)
        shift_group_layout.addLayout(shift_b_layout)
        self.shift_group.setLayout(shift_group_layout)


        self.multiple_graph_group = QGroupBox('Multiple graph')
        self.multiple_graph_group.setCheckable(True)
        self.multiple_graph_group.setChecked(False)

        self.graph_box_cnt = 0
        self.multiple_graph_add_btn = QPushButton('+')
        self.multiple_graph_add_btn.clicked.connect(self.multiple_graph_add_btn_clicked)
        self.multiple_graph_del_btn = QPushButton('-')
        self.multiple_graph_del_btn.clicked.connect(self.multiple_graph_del_btn_clicked)

        multiple_graph_edit_layout = QHBoxLayout()
        multiple_graph_edit_layout.addWidget(self.multiple_graph_add_btn)
        multiple_graph_edit_layout.addWidget(self.multiple_graph_del_btn)

        self.multiple_graph_group_layout = QVBoxLayout()
        self.multiple_graph_group_layout.addLayout(multiple_graph_edit_layout)
        self.multiple_graph_group.setLayout(self.multiple_graph_group_layout)


        self.graph_group = QGroupBox('Graph')
        self.graph_sensorid = ''
        self.graph_sensorid_lbl = QLabel('Sensorid: ')
        self.graph_sensorid_lbl.setAlignment(Qt.AlignCenter)
        self.graph_sensorid_btn = QPushButton('Type')
        self.graph_sensorid_btn.clicked.connect(self.graph_sensorid_btn_clicked)
        self.graph_start = ''
        self.graph_start_lbl = QLabel('Start date: ')
        self.graph_start_lbl.setAlignment(Qt.AlignCenter)
        self.graph_start_btn = QPushButton('Type')
        self.graph_start_btn.clicked.connect(self.graph_start_btn_clicked)
        self.graph_finish = ''
        self.graph_finish_lbl = QLabel('Finish date: ')
        self.graph_finish_lbl.setAlignment(Qt.AlignCenter)
        self.graph_finish_btn = QPushButton('Type')
        self.graph_finish_btn.clicked.connect(self.graph_finish_btn_clicked)
        self.graph_show = False
        self.graph_show_btn = QPushButton('Show')
        self.graph_show_btn.clicked.connect(self.graph_show_btn_clicked)

        graph_sensorid_layout = QHBoxLayout()
        graph_sensorid_layout.addWidget(self.graph_sensorid_lbl)
        graph_sensorid_layout.addWidget(self.graph_sensorid_btn)

        graph_start_layout = QHBoxLayout()
        graph_start_layout.addWidget(self.graph_start_lbl)
        graph_start_layout.addWidget(self.graph_start_btn)

        graph_finish_layout = QHBoxLayout()
        graph_finish_layout.addWidget(self.graph_finish_lbl)
        graph_finish_layout.addWidget(self.graph_finish_btn)

        graph_group_layout = QVBoxLayout()
        graph_group_layout.addLayout(graph_sensorid_layout)
        graph_group_layout.addLayout(graph_start_layout)
        graph_group_layout.addLayout(graph_finish_layout)
        graph_group_layout.addWidget(self.graph_show_btn)
        self.graph_group.setLayout(graph_group_layout)


        self.update_group = QGroupBox('Update')
        self.update_pbar = QProgressBar()
        self.update_btn = QPushButton('Update')
        self.update_btn.clicked.connect(self.update_btn_clicked)
        self.update_stop_btn = QPushButton('Stop')
        self.update_stop_btn.clicked.connect(self.update_stop_btn_clicked)
        
        update_btn_layout = QHBoxLayout()
        update_btn_layout.addWidget(self.update_btn)
        update_btn_layout.addWidget(self.update_stop_btn)

        update_group_layout = QVBoxLayout()
        update_group_layout.addWidget(self.update_pbar)
        update_group_layout.addLayout(update_btn_layout)
        self.update_group.setLayout(update_group_layout)

        self.download_group = QGroupBox('Download')
        self.download_btn = QPushButton('CSV')
        self.download_btn.clicked.connect(self.download_btn_clicked)
        download_layout = QVBoxLayout()
        download_layout.addWidget(self.download_btn)
        self.download_group.setLayout(download_layout)

        self.save_group = QGroupBox('Save')
        save_group_layout = QVBoxLayout()
        save_group_layout.addWidget(self.file_group)
        save_group_layout.addWidget(self.update_group)
        save_group_layout.addWidget(self.download_group)
        self.save_group.setLayout(save_group_layout)

        pixmap = QPixmap('logo.png')
        pixmap = pixmap.scaledToWidth(200)
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setPixmap(pixmap)

        version_label = QLabel('Version 1.7')
        version_label.setAlignment(Qt.AlignCenter)
        team_label = QLabel('Developed by TEAM ASAP')
        team_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(logo_lbl)
        layout.addWidget(self.language_group)
        layout.addWidget(self.graph_group)
        layout.addWidget(self.median_group)
        layout.addWidget(self.straight_group)
        layout.addWidget(self.shift_group)
        layout.addWidget(self.error_group)
        layout.addWidget(self.save_group)
        layout.addWidget(self.multiple_graph_group)
        layout.addWidget(version_label)
        layout.addWidget(team_label)

        gui_layout = QGridLayout()

        gui_layout.addLayout(left_layout, 0, 0)
        gui_layout.addLayout(layout, 0, 1)
        
        gui_layout.setColumnStretch(0, 8)
        gui_layout.setColumnStretch(1, 1)
        
        self.setLayout(gui_layout)
        self.setWindowTitle('Telofarm')
        self.setGeometry(160, 90, 1600, 900)
        self.show()
    
    def language_btn_eng_clicked(self):
        self.language = 'eng'
        self.setWindowTitle('Telofarm')
        self.language_group.setTitle('Language')
        self.file_group.setTitle('File')
        self.file_btn_create.setText('Create')
        self.file_btn_delete.setText('Delete')
        self.sensorid_group.setTitle('Sensorid')
        self.sensorid_btn.setText('Type')
        self.median_group.setTitle('Median')
        self.unit_number_lbl.setText('Unit number: %s' % self.unit_number)
        self.unit_number_btn.setText('Type')
        self.error_group.setTitle('Error')
        self.error_lbl.setText(' < error < ')
        self.error_min_btn.setText('min')
        self.error_max_btn.setText('max')
        self.straight_group.setTitle('Straight')
        self.shift_group.setTitle('Shift')
        self.multiple_graph_group.setTitle('Multiple graph')
        self.graph_group.setTitle('Graph')
        self.graph_sensorid_lbl.setText('Sensorid: %s' % self.graph_sensorid)
        self.graph_sensorid_btn.setText('Type')
        self.graph_start_lbl.setText('Start date: %s' % self.graph_start)
        self.graph_start_btn.setText('Type')
        self.graph_finish_lbl.setText('Finish date: %s' % self.graph_finish)
        self.graph_finish_btn.setText('Type')
        self.graph_show_btn.setText('Show')
        self.save_group.setTitle('Save')
        self.update_group.setTitle('Update')
        self.update_btn.setText('Update')
        self.update_stop_btn.setText('Stop')
        self.download_group.setTitle('Download')
        self.download_btn.setText('CSV')

    def language_btn_kor_clicked(self):
        self.language = 'kor'
        self.setWindowTitle('텔로팜')
        self.language_group.setTitle('언어')
        self.file_group.setTitle('파일')
        self.file_btn_create.setText('생성')
        self.file_btn_delete.setText('삭제')
        self.sensorid_group.setTitle('고유번호')
        self.sensorid_btn.setText('입력')
        self.median_group.setTitle('중간값')
        self.unit_number_lbl.setText('적용수: %s(개)' % self.unit_number)
        self.unit_number_btn.setText('입력')
        self.error_group.setTitle('오차')
        self.error_lbl.setText(' < 오차 < ')
        self.error_min_btn.setText('최소')
        self.error_max_btn.setText('최대')
        self.straight_group.setTitle('직선')
        self.shift_group.setTitle('이동')
        self.multiple_graph_group.setTitle('다중 그래프')
        self.graph_group.setTitle('그래프')
        self.graph_sensorid_lbl.setText('고유번호: %s' % self.graph_sensorid)
        self.graph_sensorid_btn.setText('입력')
        self.graph_start_lbl.setText('시작날짜: %s' % self.graph_start)
        self.graph_start_btn.setText('입력')
        self.graph_finish_lbl.setText('종료날짜: %s' % self.graph_finish)
        self.graph_finish_btn.setText('입력')
        self.graph_show_btn.setText('보기')
        self.save_group.setTitle('저장')
        self.update_group.setTitle('업데이트')
        self.update_btn.setText('업데이트')
        self.update_stop_btn.setText('일시정지')
        self.download_group.setTitle('다운로드')
        self.download_btn.setText('엑셀파일')

    
    def search_table(self):
        self.conn = psycopg2.connect('host=xxx.xxx.xx.xx dbname=xxxxxxxxx user=xxxxxxxx password=xxxxxxxxxx')
        self.cur = self.conn.cursor()

        self.cur.execute("select * from pg_tables;")
        tables = self.cur.fetchall()
        table = []
        for i in tables:
            if i[0] == 'public':
                table.append(i[1])
        table.sort()

        return table

    def file_btn_create_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Create', 'File name:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '생성', '파일명:')

        if ok:
            self.cur.execute("create table %s (like sensingvalues);" % text)
            self.conn.commit()

            self.file_box.clear()
            table = self.search_table()
            for i in table:
                self.file_box.addItem(i)
    
    def file_btn_delete_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Delete', 'Password:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '삭제', '비밀번호:')

        if ok:
            if text == 'admin':
                self.cur.execute("drop table %s;" % str(self.file_box.currentText()))
                self.conn.commit()

                self.file_box.clear()
                table = self.search_table()
                for i in table:
                    self.file_box.addItem(i)

    def sensorid_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Sensorid', 'Sensorid:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '고유번호', '고유번호:')
        
        if ok:
            self.sensorid = text.split()
            sensorid_tmp = []
            for i in self.sensorid:
                if i in sensorid_tmp:
                    pass
                else:
                    sensorid_tmp.append(i)
            self.sensorid = sensorid_tmp
    
    def unit_number_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Median', 'Unit number:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '중간값', '적용수(개):')
        
        if ok:
            self.unit_number = text
            if self.language == 'eng':
                self.unit_number_lbl.setText('Unit number: %s' % text)
            elif self.language == 'kor':
                self.unit_number_lbl.setText('적용수: %s(개)' % text)
    
    def error_min_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Error', 'Minimum:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '오차', '최소:')
        
        if ok:
            self.error_min = text
            self.error_min_lbl.setText(text)
    
    def error_max_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Error', 'Maximum:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '오차', '최대:')
        
        if ok:
            self.error_max = text
            self.error_max_lbl.setText(text)
    
    def shift_a_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Shift', 'a:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '이동', 'a:')
        
        if ok:
            self.shift_a = text
            self.shift_a_lbl.setText('x %s' % text)
    
    def shift_b_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Shift', 'b:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '이동', 'b:')
        
        if ok:
            self.shift_b = text
            if text[0] == '-':
                self.shift_b_lbl.setText('- %s' % text[1:])
            else:
                self.shift_b_lbl.setText('+ %s' % text)
    
    def multiple_graph_add_btn_clicked(self):
        self.graph_box_cnt += 1
        globals()['graph_box{0}'.format(self.graph_box_cnt)] = QComboBox()
        table = self.search_table()
        for i in table:
            globals()['graph_box{0}'.format(self.graph_box_cnt)].addItem(i)
        self.multiple_graph_group_layout.addWidget(globals()['graph_box{0}'.format(self.graph_box_cnt)])
    
    def multiple_graph_del_btn_clicked(self):
        if self.graph_box_cnt > 0:
            self.multiple_graph_group_layout.removeWidget(globals()['graph_box{0}'.format(self.graph_box_cnt)])
            globals()['graph_box{0}'.format(self.graph_box_cnt)].deleteLater()
            globals()['graph_box{0}'.format(self.graph_box_cnt)] = None
            self.graph_box_cnt -= 1
    
    def graph_sensorid_btn_clicked(self):
        if self.language == 'eng':
            text, ok = QInputDialog.getText(self, 'Graph', 'Sensorid:')
        elif self.language == 'kor':
            text, ok = QInputDialog.getText(self, '그래프', '고유번호:')
        
        if ok:
            self.graph_sensorid = text
            if self.language == 'eng':
                self.graph_sensorid_lbl.setText('Sensorid: %s' % text)
            elif self.language == 'kor':
                self.graph_sensorid_lbl.setText('고유번호: %s' % text)

    def graph_start_btn_clicked(self):
        if self.language == 'eng':
            text1, ok = QInputDialog.getText(self, 'Year', 'Year:')
            text2, ok = QInputDialog.getText(self, 'Month', 'Month:')
            text3, ok = QInputDialog.getText(self, 'Day', 'Day:')
        elif self.language == 'kor':
            text1, ok = QInputDialog.getText(self, '연', '연:')
            text2, ok = QInputDialog.getText(self, '월', '월:')
            text3, ok = QInputDialog.getText(self, '일', '일:')
        
        if ok:
            self.graph_start = text1+'-'+text2+'-'+text3
            if self.language == 'eng':
                self.graph_start_lbl.setText('Start date: %s-%s-%s' % (text1, text2, text3))
            elif self.language == 'kor':
                self.graph_start_lbl.setText('시작날짜: %s-%s-%s' % (text1, text2, text3))
    
    def graph_finish_btn_clicked(self):
        if self.language == 'eng':
            text1, ok = QInputDialog.getText(self, 'Year', 'Year:')
            text2, ok = QInputDialog.getText(self, 'Month', 'Month:')
            text3, ok = QInputDialog.getText(self, 'Day', 'Day:')
        elif self.language == 'kor':
            text1, ok = QInputDialog.getText(self, '연', '연:')
            text2, ok = QInputDialog.getText(self, '월', '월:')
            text3, ok = QInputDialog.getText(self, '일', '일:')
        
        if ok:
            self.graph_finish = text1+'-'+text2+'-'+text3
            if self.language == 'eng':
                self.graph_finish_lbl.setText('Finish date: %s-%s-%s' % (text1, text2, text3))
            elif self.language == 'kor':
                self.graph_finish_lbl.setText('종료날짜: %s-%s-%s' % (text1, text2, text3))
    
    def graph_show_btn_clicked(self):

        if self.multiple_graph_group.isChecked():
            if self.graph_box_cnt > 0:
                start_year = int(self.graph_start.split('-')[0])
                start_month = int(self.graph_start.split('-')[1])
                start_day = int(self.graph_start.split('-')[2])
                finish_year = int(self.graph_finish.split('-')[0])
                finish_month = int(self.graph_finish.split('-')[1])
                finish_day = int(self.graph_finish.split('-')[2])
                self.fig.clear()
                for i in range(1, self.graph_box_cnt+1):
                    self.cur.execute("select * from %s where sensorid = %s order by regdate desc;" % (globals()['graph_box{0}'.format(i)].currentText(), self.graph_sensorid))
                    graph = self.cur.fetchall()
                    graph_x = []
                    graph_y = []
                    for j in graph:
                        if datetime.date(start_year, start_month, start_day) < j[1].date() < datetime.date(finish_year, finish_month, finish_day):
                            graph_x.append(j[1])
                            graph_y.append(j[3])
                    
                    if self.graph_box_cnt == 1:
                        globals()['ax{0}'.format(i)] = self.fig.add_subplot(1,1,i)
                        globals()['ax{0}'.format(i)].plot(graph_x, graph_y)
                    elif self.graph_box_cnt == 2:
                        globals()['ax{0}'.format(i)] = self.fig.add_subplot(1,2,i)
                        globals()['ax{0}'.format(i)].plot(graph_x, graph_y)
                    elif self.graph_box_cnt == 3:
                        globals()['ax{0}'.format(i)] = self.fig.add_subplot(2,2,i)
                        globals()['ax{0}'.format(i)].plot(graph_x, graph_y)
                    elif self.graph_box_cnt == 4:
                        globals()['ax{0}'.format(i)] = self.fig.add_subplot(2,2,i)
                        globals()['ax{0}'.format(i)].plot(graph_x, graph_y)
                    else:
                        globals()['ax{0}'.format(i)] = self.fig.add_subplot(int(self.graph_box_cnt/2)+1,2,i)
                        globals()['ax{0}'.format(i)].plot(graph_x, graph_y)
                    for tick in globals()['ax{0}'.format(i)].get_xticklabels():
                        tick.set_rotation(27)
                self.canvas.draw()
                
        else:
            self.thread_graph.setdata(self.sensorid_group.isChecked(), self.median_group.isChecked(), self.error_group.isChecked(), self.straight_group.isChecked(), self.shift_group.isChecked(), self.file_box.currentText(), self.sensorid, self.unit_number, self.error_min, self.error_max, self.shift_a, self.shift_b, self.graph_sensorid, self.graph_start, self.graph_finish)
            self.thread_graph.start()
    
    def update_btn_clicked(self):
        self.update_pbar.setRange(0,0)
        self.thread_update.setdata(self.sensorid_group.isChecked(), self.median_group.isChecked(), self.error_group.isChecked(), self.straight_group.isChecked(), self.shift_group.isChecked(), self.file_box.currentText(), self.sensorid, self.unit_number, self.error_min, self.error_max, self.shift_a, self.shift_b, self.graph_sensorid)
        self.thread_update.start()
    
    def update_stop_btn_clicked(self):
        self.thread_update.quit()
        self.update_pbar.setRange(0,100)

    def download_btn_clicked(self):
        if self.language == 'eng':
            fname = QFileDialog.getSaveFileName(self, 'Save directory')
        else:
            fname = QFileDialog.getSaveFileName(self, '저장 위치')
        
        if fname[0]:
            table = self.file_box.currentText()
            tablecsv = fname[0]+'.csv'
            fout = open(tablecsv, 'w')
            self.cur.copy_to(fout, table, sep="|")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())