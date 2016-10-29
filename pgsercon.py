#!/usr/bin/env python

import sys, os, json
from PyQt5.QtWidgets import (
    QWidget,QTableWidgetItem,
    QHBoxLayout, QGridLayout,
    QVBoxLayout,
    QDialog,
    QSplitter,
    QLineEdit,
    QApplication,
    QComboBox, QHeaderView, QHeaderView,
    QListWidget,
    QLabel, QMenu, QAction,
    QPushButton, QListWidgetItem,
    QFileDialog,QMessageBox,
    QTableWidget, QAbstractItemView
)
from PyQt5.QtGui import (QBrush,QColor,QCursor)
from PyQt5.QtCore import Qt, QSize
import webbrowser
from psutil import virtual_memory
import platform
import math

#from PySide import QtCore, QtGui

urlbase = 'https://www.postgresql.org/docs/'
htmlist = {
    "File Locations" : "/static/runtime-config-file-locations.html" ,
    "Connections and Authentication" : "/static/runtime-config-connection.html" ,
    "Resource Usage" : "/static/runtime-config-resource.html" ,
    "Write-Ahead Log" : "/static/runtime-config-wal.html" ,
    "Replication" : "/static/runtime-config-replication.html" ,
    "Query Tuning" : "/static/runtime-config-query.html" ,
    "Process Title" : "/static/runtime-config-logging.html" ,
    "Reporting and Logging" : "/static/runtime-config-logging.html" ,
    "Statistics" : "/static/runtime-config-statistics.html" ,
    "Autovacuum" : "/static/runtime-config-autovacuum.html" ,
    "Client Connection Defaults" : "/static/runtime-config-client.html" ,
    "Lock Management" : "/static/runtime-config-locks.html" ,
    "Version and Platform Compatibility" : "/static/runtime-config-compatible.html" ,
    "Error Handling" : "/static/runtime-config-error-handling.html" ,
    "Preset Options" : "/static/runtime-config-preset.html" ,
    "Developer Options" : "/static/runtime-config-developer.html" 
}

WINDOWS = 1000
OSX =1001
LINUX = 1002
ERROS = 1009




class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PostgreSQL Server Configuration File")
        self.dic = {} # {group_name : par_name: [type, value, unit, description, enum]}
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        #title=",".join(os.listdir("./pgsercon.app/"))
        self.setWindowTitle(self.basedir)

        self.templates = {}
        self.os = ERROS
        self.memory = -1
        self.connections = -1
        self.version = 0
        self.initUI()


    def initUI(self):
        widget = QHBoxLayout(self)

        self.left = QWidget()
        self.leftl = QVBoxLayout(self.left)

        # Postgres version:
        self.combo = QComboBox()
        list = os.listdir(self.basedir)
        clist = []

        for l in list:
            if 'param' in l:
                clist.append('Postgres %s' %l[6:])

        for l in clist:
            self.combo.addItem(l)

        self.combo.activated.connect(self.choosePversion)
        self.leftl.addWidget(self.combo)

        # templates
        temp = QWidget()
        templay = QHBoxLayout(temp)
        self.clearButton = QPushButton('Clear')
        self.clearButton.clicked.connect(self.clearConfig)
        templay.addWidget(self.clearButton)
        self.template = QPushButton('Insert Template...')
        self.template.clicked.connect(self.insertTemplate)
        templay.addWidget(self.template)
        templay.setStretch(0, 1)
        templay.setStretch(1, 2)
        self.leftl.addWidget(temp)


        # config file
        self.config = QTableWidget(self)
        self.config.insertColumn(0)
        self.config.insertColumn(1)
        self.config.insertColumn(2)
        self.config.setColumnHidden(2, True)
        self.config.horizontalHeader().setStretchLastSection(True)
        self.config.setHorizontalHeaderLabels(('Name', 'Value'))
        self.config.verticalHeader().setVisible(False)
        self.leftl.addWidget(self.config)
        self.config.cellDoubleClicked.connect(self.findPar)
        self.config.cellPressed.connect(self.checkAllPar)
        self.config.cellChanged.connect(self.checkAllPar)
        self.config.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Config file loader
        cfg = QWidget()
        cfgl = QHBoxLayout(cfg)
        # self.cfglabel = QLabel()
        # cfgl.addWidget(self.cfglabel)
        button = QPushButton('Load File...')
        button.clicked.connect(self.loadFile)
        cfgl.addWidget(button)
        button = QPushButton('Save File...')
        button.clicked.connect(self.saveFile)
        cfgl.addWidget(button)
        self.leftl.addWidget(cfg)

        self.mid = QListWidget(self)
        self.mid.itemClicked.connect(self.choosePar)

        # Table with all default values
        self.right = QTableWidget(self)
        self.right.setMouseTracking(True)
        self.right.insertColumn(0)
        self.right.insertColumn(1)
        self.right.insertColumn(2)
        self.right.insertColumn(3)
        self.right.insertColumn(4)
        self.right.insertColumn(5)
        self.right.insertColumn(6)
        self.right.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        #self.right.horizontalHeader().setStretchLastSection(True)
        self.right.setHorizontalHeaderLabels(('Use', 'Name', 'Type', 'Default', 'Unit', 'Description', ''))
        self.right.verticalHeader().setVisible(True)
        self.right.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.right.itemClicked.connect(self.changeCfg)
        self.right.cellEntered.connect(self.changeCsr)
        #self.right.setWordWrap(True)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left)
        splitter.addWidget(self.mid)
        splitter.addWidget(self.right)

        widget.addWidget(splitter)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 6)


        self.setGeometry(100, 100, 1600, 900)
        #self.setWindowTitle('QSplitter')
        self.show()
        self.combo.setCurrentIndex(self.combo.count()-1)
        self.choosePversion(idx = self.combo.count()-1)

        #self.temp_list.setCurrentIndex(0)
        #self.updateTemplates()


    # def updateTemplates(self):
    #     ver = self.combo.currentText()[9:]
    #     self.templates = templates.templates(ver, self.dic)
    #     self.temp_list.clear()
    #     self.temp_list.addItem('Choose template')
    #
    #     for t in sorted(self.templates, ):
    #         self.temp_list.addItem(t)


    def value(self, par):
        for key in self.dic:
            if par in self.dic[key]:
                return self.dic[key][par][1]

    def unit(self, par):
        for key in self.dic:
            if par in self.dic[key]:
                return self.dic[key][par][2]


    def clearConfig(self):
        self.config.setRowCount(0)
        self.choosePar(litem = self.mid.currentItem())



    def onRenameHtml(self, var):
        if self.mid.currentItem().text() == 'Other':
            QMessageBox.about(self, 'HTML not found', 'HTML for this parameter not found')
            return 0

        html = """%s%s%s#GUC-%s""" %(urlbase, self.combo.currentText()[9:], htmlist[self.mid.currentItem().text()], var.replace("_", '-').upper())
        webbrowser.open(html)


    def loadFile(self):
        fdialog = QFileDialog(self)
        fdialog.setNameFilters(["Postgres file (postgresql.conf)", "All files (*.*)"])
        fdialog.selectNameFilter("Postgres file (postgresql.conf)")

        if fdialog.exec_():
            fname = fdialog.selectedFiles()[0]
        else:
            return 0

        if not os.path.isfile(fname):
            return 0

        self.config.setRowCount(0)
        f = open(fname, 'r')
        for l in f:
            if len(l.strip()) == 0 or l.strip()[0] == '#':
                continue

            par = l.split('#')[0].split('=')[0].strip()
            val = l.split('#')[0].split('=')[1].strip()
            self.insertConfig(par,val)

        f.close()
        self.config.resizeColumnToContents(0)
        self.sortConf()
        self.checkAllPar()

    def sortConf(self):
        for row in range(self.config.rowCount()):
            par = self.config.item(row,0).text()
            found = False
            for r in range(self.mid.count()):
                for p in self.dic[self.mid.item(r).text()]:
                    if par == p:
                        self.config.item(row,2).setText("%s" %("0%s" %r if r < 10 else "%s" %r))
                        found = True

            if not found:
                r = self.mid.count()
                self.config.item(row, 2).setText("%s" %("0%s" %r if r < 10 else "%s" %r))

        self.config.sortItems(2)


    def saveFile(self):
        file = QFileDialog(self).getSaveFileName()

        if file == '':
            return 0

        f = open(file[0], 'w')

        for r in range(self.config.rowCount()):
            par = self.config.item(r,0).text()
            obj = self.config.cellWidget(r, 1)
            #print(type(obj))
            if type(obj) == type(QComboBox()):
                val = obj.currentText()
            else:
                val = self.config.item(r,1).text()

            f.write("%s = %s\n" %(par,val))

        f.close()


    def choosePversion(self, idx):
        #print('ok')
        self.dic = {}
        self.var = 0
        self.mid.clear()
        self.right.setRowCount(0)

        ver = self.combo.currentText().split(' ')[-1]

        if not os.path.isfile('params%s' %ver):
            return 0

        #open('params%s' % ver, 'r')
        with open('params%s' % ver, 'r') as file:
            self.dic = json.load(file)


        for key in self.dic:
            self.mid.addItem(key)

        self.mid.sortItems()
        self.mid.setSpacing(2)
        self.checkAllPar()
        self.sortConf()
        file.close()
        self.version = ver
        #self.updateTemplates()


    def choosePar(self, litem):
        if litem is None:
            return 0

        self.right.setRowCount(0)

        for par in self.dic[litem.text()]:
            idx = self.right.rowCount()
            self.right.insertRow(idx)

            #checkbox
            item = QTableWidgetItem()
            if len(self.config.findItems(par, Qt.MatchExactly)) != 0:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.right.setItem(idx, 0, item)

            # name
            item = QTableWidgetItem(par)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 1, item)

            # type
            item = QTableWidgetItem(self.dic[litem.text()][par][0])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 2, item)

            # default
            item = QTableWidgetItem(self.dic[litem.text()][par][1])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 3, item)

            # Unit
            item = QTableWidgetItem(self.dic[litem.text()][par][2])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 4, item)

            # description
            item = QTableWidgetItem(self.dic[litem.text()][par][3])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.TextWordWrap)
            item.setToolTip(self.dic[litem.text()][par][3])
            self.right.setItem(idx, 5, item)


            item = QTableWidgetItem('More...')
            font = item.font()
            font.setUnderline(True)
            item.setFont(font)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable )
            brush = QBrush()
            brush.setColor(Qt.blue)
            item.setForeground(brush)
            self.right.setItem(idx, 6, item)



        self.right.resizeColumnToContents(0)
        self.right.resizeColumnToContents(1)
        self.right.resizeColumnToContents(2)
       # self.right.resizeColumnToContents(3)
        self.right.resizeColumnToContents(4)
        self.right.resizeColumnToContents(6)


    def findPar(self, r, c):
        if c != 0:
            return 0

        par = self.config.item(r,0).text()
        #obj = self.config.cellWidget(r, 1)
        # if '%s' %type(obj) == "<class 'PyQt4.QtGui.QComboBox'>":
        #     val = obj.currentText()
        # else:
        #     val = self.config.item(r,1).text()
        self.config.item(r,c).setSelected(True)
        found = False

        if len(self.dic) == 0:
            return 0
        #print(par)

        for key in self.dic:
            if par in self.dic[key]:
                #print(key)
                item = self.mid.findItems(key, Qt.MatchExactly)[0]
                if item is not None:
                    self.mid.setCurrentItem(item)
                    self.choosePar(item)

                    item = self.right.findItems(par, Qt.MatchExactly)[0]
                    self.right.setCurrentItem(item)
                    item.setSelected(True)
                    found = True
                    break

        if not found:
            QMessageBox.about(self,'Parameter Not found', 'This parameter is not standard Postgres parameter')


    def checkAllPar(self):
        for r in range(self.config.rowCount()):
            self.checkPar(r)

        self.choosePar(litem=self.mid.currentItem())

    def checkPar(self, row):
        if self.config.item(row, 0) is not None:
            par = self.config.item(row, 0).text()
        else:
            return 0

        obj = self.config.cellWidget(row, 1)
        #print(obj)
            #val = self.config.item(row, 1).text()

            #obj = self.config.cellWidget(row, 1)
        if type(obj) == type(QComboBox()):
            val = obj.currentText()
            #print(val)
        else:
            if self.config.item(row, 1) is not None:
                val = self.config.item(row,1).text()
            else:
                return 0
        found = False
        white = True

        if self.config.item(row, 0).background().color() == QColor(200, 255, 200, 255):
            return 0

        for key in self.dic:
            if par in self.dic[key]:
                found = True

                if self.dic[key][par][1] != str(val):
                    #print(l[2], val)
                    white = False
                    self.config.item(row,0).setBackground(QBrush(QColor(200, 255, 255, 255)))

                    if type(obj) != type(QComboBox()):
                        self.config.item(row, 1).setBackground(QBrush(QColor(200, 255, 255, 255)))

                break

        if len(self.dic) == 0:
            found = True

        # colr red if not found
        if not found:
            white = False
            self.config.item(row, 0).setBackground(QBrush(QColor(255, 200, 200, 255)))
            if type(obj) != type(QComboBox()):
                self.config.item(row, 1).setBackground(QBrush(QColor(255, 200, 200, 255)))

        # color white when same as default
        if white:
            self.config.item(row, 0).setBackground(Qt.white)

            if type(obj) != type(QComboBox()):
                self.config.item(row, 1).setBackground(QBrush(Qt.white))



    def changeCfg(self, item):
        row = item.row()

        if item.column() == 0 and item.checkState() == 2:
            par = self.right.item(row,1).text()
            val = self.right.item(row, 3).text()
            color = QColor(200, 255, 200, 255)
            self.insertConfig(par,val,color)
            return 0

        if item.column() == 0 and item.checkState() == 0:
            i = self.config.findItems(self.right.item(row,1).text(), Qt.MatchExactly)[0]
            if i is not None:
                self.config.removeRow(i.row())

        if item.column() == 6:
            self.onRenameHtml(self.right.item(item.row(), 1).text())

        #self.checkAllPar()


    def changeCsr(self, r, c):
        if c == 6:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)


    def insertConfig(self, par, val, color = Qt.white):
        type = ''

        for key in self.dic:
            if par in self.dic[key]:
                #pkey = key
                type = self.dic[key][par][0]
                break

        self.config.insertRow(self.config.rowCount())

        item = QTableWidgetItem(par)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        item.setBackground(QBrush(color))

        item.setToolTip('Double-click name to jump to description')
        self.config.setItem(self.config.rowCount() - 1, 0, item)

        if type == 'bool':
            item = QComboBox()
            item.addItem('on')
            item.addItem('off')

            if val == 'on':
                item.setCurrentIndex(0)
            else:
                item.setCurrentIndex(1)

            item.currentIndexChanged.connect(self.checkAllPar)
            self.config.setCellWidget(self.config.rowCount() - 1, 1, item)
        elif type == 'enum':
            enum = self.dic[key][par][4].strip('}').strip('{').split(",")
            item = QComboBox()

            for i in enum:
                item.addItem(i)

            item.setCurrentIndex(item.findText(val,Qt.MatchExactly))
            item.currentIndexChanged.connect(self.checkAllPar)
            self.config.setCellWidget(self.config.rowCount() - 1, 1, item)
        else:
            item = QTableWidgetItem(val)
            item.setBackground(QBrush(color))
            item.setToolTip('Double-click value to edit')
            self.config.setItem(self.config.rowCount() - 1, 1, item)

        item = QTableWidgetItem()
        self.config.setItem(self.config.rowCount() - 1, 2, item)

        self.config.resizeColumnToContents(0)

    def bytes(self, s = ''):
        if s == 'kB' or s == 'KB':
            return 1024
        elif s == 'MB':
            return 1024 * 1024
        elif s == '8kB':
            return 8 * 1024
        else:
            return 1


    def insertTemplate(self):

        tempWidget = templateWidget(parent = self, os = self.os, mem = self.memory, conn = self.connections)

        if tempWidget.exec_() == 0:
            return 0

        self.os = tempWidget.os
        self.memory = tempWidget.memory # in bytes
        self.connections = tempWidget.connections
        mem = self.memory  # in bytes
        shared_buffs = int(mem / 4 / self.bytes(self.unit('shared_buffers')))

        if self.os == WINDOWS:
            shared_buffs = int(512 * 1024 * 1024 / self.bytes(self.unit('shared_buffers')))

        effective_cache_size = int(mem / 2 / self.bytes(self.unit('shared_buffers')))
        checkpoint_segments = '32'

        if self.version == '9.6' or self.version == '9.5':
            checkpoint_segments = '__NONE__'

        checkpoint_completion_target = 0.9
        work_mem = int(math.floor((float(mem) - float(shared_buffs)) / self.bytes(self.unit('shared_buffers')) / int(self.connections) / 5)) # 5 - number of tables accessed at the same time

        templates = {"port" : "5432",
                     "max_connections": "%s" %self.connections,
                     "shared_buffers" : "%s" %shared_buffs,
                     "effective_cache_size" : "%s" %effective_cache_size,
                     "checkpoint_segments" : "%s" %checkpoint_segments,
                     "checkpoint_completion_target" : "%s" %checkpoint_completion_target,
                     "work_mem" : "%s" %work_mem
                     }

        for temp in templates:
            if len(self.config.findItems(temp, Qt.MatchExactly)):
                continue

            if templates[temp] == '__NONE__':
                continue

            found = False

            for key in self.dic:
                if temp in self.dic[key]:
                    val = templates[temp]

                    if val == '__DEFAULT__':
                        val = self.dic[key][temp][1]

                    self.insertConfig(temp,val)
                    found = True

            if not found:
                QMessageBox.about(self, 'Invalid argument', 'Could not create insert %s. It is not valid parameter in this version' %temp)

        self.config.resizeColumnToContents(0)
        self.sortConf()
        self.checkAllPar()



class templateWidget(QDialog):
    def __init__(self, parent, os = ERROS, mem = -1, conn = -1):
        super(templateWidget, self).__init__(parent=parent)
        self.parent = parent

        self.os = os
        self.memory = mem
        self.connections = conn
        self.initUI()


    def initUI(self):
        lay = QVBoxLayout(self)
        topWidget = QWidget()
        layout = QGridLayout(topWidget)
        self.defaultButton = QPushButton('Get Default Values')
        self.defaultButton.clicked.connect(self.defaultButtonClicked)
        layout.addWidget(self.defaultButton, 0, 1)

        # OS
        label = QLabel('OS')
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(label, 1,0)
        self.OSComboBox = QComboBox()
        self.OSComboBox.addItem('WINDOWS')
        self.OSComboBox.addItem('OSX')
        self.OSComboBox.addItem('LINUX')
        layout.addWidget(self.OSComboBox, 1,1)

        # Memory
        label = QLabel('Memory')
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(label, 2, 0)
        self.memoryEdit = QLineEdit()
        layout.addWidget(self.memoryEdit, 2, 1)
        label = QLabel('GB')
        layout.addWidget(label, 2, 2)

        # Connections
        label = QLabel('Max Connections')
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(label, 3, 0)
        self.connectionsEdit = QLineEdit()
        layout.addWidget(self.connectionsEdit, 3,1)

        lowWidget = QWidget()
        layout = QHBoxLayout(lowWidget)

        # OK
        button = QPushButton('OK')
        button.clicked.connect(self.accept)
        layout.addWidget(button)

        # Cancel
        button = QPushButton('Cancel')
        button.clicked.connect(self.reject)
        layout.addWidget(button)

        lay.addWidget(topWidget)
        lay.addWidget(lowWidget)

        self.defaultButtonClicked()


    def defaultButtonClicked(self):
        if platform.system() == 'Darwin':
            self.os = OSX
        elif platform.system() == 'Linux':
            self.os = LINUX
        elif platform.system() == 'Windows':
            self.os = WINDOWS
        else:
            QMessageBox.about(self, 'Could not identify Operation System.\nPlease choose correct OS from list')
            self.os = ERROS

        self.memory = virtual_memory().total
        self.connections = self.parent.value('max_connections')
        #print(self.parent.dic )
        self.updateEditValues()


    def updateEditValues(self):
        self.OSComboBox.setCurrentIndex(-1 if self.os == ERROS else self.os - 1000)
        self.memoryEdit.setText('' if self.memory == -1 else str(self.memory / (1024*1024*1024)))
        self.connectionsEdit.setText('' if self.connections == -1 else str(self.connections))

    def accept(self):
        s = self.OSComboBox.currentText()

        if s == "WINDOWS":
            self.os = WINDOWS
        elif s == 'OSX':
            self.os = OSX
        elif s == 'LINUX':
            self.os == LINUX

        self.memory = float(self.memoryEdit.text()) * 1024 * 1024 * 1024
        self.connections = int(self.connectionsEdit.text())

        super(templateWidget, self).accept()








if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    sys.exit(app.exec())
