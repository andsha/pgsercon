#!/usr/bin/env python

import sys, os, json
from PyQt4.QtGui import (
    QWidget,QTableWidgetItem,
    QHBoxLayout, QCheckBox,
    QVBoxLayout,
    QListWidget,
    QSplitter,
    QStyleFactory,
    QApplication, QBrush,
    QComboBox, QHeaderView, QHeaderView,
    QListWidget, QCursor,
    QLabel, QMenu, QAction,
    QPushButton, QListWidgetItem,
    QFileDialog,QMessageBox, QColor,
    QTableWidget, QAbstractItemView
)

from PyQt4.QtCore import Qt, QSize
import webbrowser
import templates

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




class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PostgreSQL Server Configuration File")
        self.dic = {} # {group_name : par_name: [type, default value, description, enum]}
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        self.templates = {}
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
        label = QLabel('Insert template')
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        templay.addWidget(label)
        self.temp_list = QComboBox()
        self.temp_list.addItem('Choose template')

        for t in self.templates:
            self.temp_list.addItem(t)

        self.temp_list.activated.connect(self.insertTemplate)
        self.temp_list.setSizeAdjustPolicy(0)

        templay.addWidget(self.temp_list)
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
        self.config.currentCellChanged.connect(self.checkAllPar)
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
        self.right.horizontalHeader().setResizeMode(4, QHeaderView.Stretch)
        #self.right.horizontalHeader().setStretchLastSection(True)
        self.right.setHorizontalHeaderLabels(('Use', 'Name', 'Type', 'Default', 'Description', ''))
        self.right.verticalHeader().setVisible(True)
        self.right.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.right.itemClicked.connect(self.changeCfg)
        self.right.cellEntered.connect(self.changeCsr)
        self.right.setWordWrap(True)

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

        self.temp_list.setCurrentIndex(0)
        self.updateTemplates()


    def updateTemplates(self):
        ver = self.combo.currentText()[9:]
        self.templates = templates.templates(ver)
        self.temp_list.clear()
        self.temp_list.addItem('Choose template')

        for t in sorted(self.templates, ):
            self.temp_list.addItem(t)



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

        f = open(file, 'w')

        for r in range(self.config.rowCount()):
            par = self.config.item(r,0).text()
            obj = self.config.cellWidget(r, 1)
            #print(type(obj))
            if '%s' % type(obj) == "<class 'PyQt4.QtGui.QComboBox'>":
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

        if not os.path.isfile(self.basedir + '/params%s' %ver):
            return 0

        with open(self.basedir + '/params%s' %ver, 'r') as file:
            self.dic = json.load(file)

        for key in self.dic:
            self.mid.addItem(key)

        self.mid.sortItems()
        self.mid.setSpacing(2)
        self.checkAllPar()
        self.sortConf()
        file.close()
        self.updateTemplates()


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

            # description
            item = QTableWidgetItem(self.dic[litem.text()][par][2])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.TextWordWrap)
            item.setToolTip(self.dic[litem.text()][par][2])
            self.right.setItem(idx, 4, item)


            item = QTableWidgetItem('More...')
            font = item.font()
            font.setUnderline(True)
            item.setFont(font)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable )
            brush = QBrush()
            brush.setColor(Qt.blue)
            item.setForeground(brush)
            self.right.setItem(idx, 5, item)



        self.right.resizeColumnToContents(0)
        self.right.resizeColumnToContents(1)
        self.right.resizeColumnToContents(5)


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

    def checkPar(self, row):
        if self.config.item(row, 0) is not None:
            par = self.config.item(row, 0).text()
        else:
            return 0

        obj = self.config.cellWidget(row, 1)
            #val = self.config.item(row, 1).text()

            #obj = self.config.cellWidget(row, 1)
        if '%s' % type(obj) == "<class 'PyQt4.QtGui.QComboBox'>":
            val = obj.currentText()
        else:
            if self.config.item(row, 1) is not None:
                val = self.config.item(row,1).text()
            else:
                return 0

        found = False
        white = True

        if self.config.item(row, 0).backgroundColor() == QColor(200, 255, 200, 255):
            return 0

        for key in self.dic:
            if par in self.dic[key]:
                found = True

                if self.dic[key][par][1] != str(val):
                    #print(l[2], val)
                    white = False
                    self.config.item(row,0).setBackgroundColor(QColor(200, 255, 255, 255))

                    if '%s' % type(obj) != "<class 'PyQt4.QtGui.QComboBox'>":
                        self.config.item(row, 1).setBackgroundColor(QColor(200, 255, 255, 255))

                break

        if len(self.dic) == 0:
            found = True

        # colr red if not found
        if not found:
            white = False
            self.config.item(row, 0).setBackgroundColor(QColor(255, 200, 200, 255))
            if '%s' % type(obj) != "<class 'PyQt4.QtGui.QComboBox'>":
                self.config.item(row, 1).setBackgroundColor(QColor(255, 200, 200, 255))

        # color white when same as default
        if white:
            self.config.item(row, 0).setBackgroundColor(Qt.white)

            if '%s' % type(obj) != "<class 'PyQt4.QtGui.QComboBox'>":
                self.config.item(row, 1).setBackgroundColor(Qt.white)



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

        if item.column() == 5:
            self.onRenameHtml(self.right.item(item.row(), 1).text())

        self.checkAllPar()


    def changeCsr(self, r, c):
        if c == 5:
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
        item.setBackgroundColor(color)
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
            enum = self.dic[key][par][3].strip('}').strip('{').split(",")
            item = QComboBox()

            for i in enum:
                item.addItem(i)

            item.setCurrentIndex(item.findText(val,Qt.MatchExactly))
            item.currentIndexChanged.connect(self.checkAllPar)
            self.config.setCellWidget(self.config.rowCount() - 1, 1, item)
        else:
            item = QTableWidgetItem(val)
            item.setBackgroundColor(color)
            item.setToolTip('Double-click value to edit')
            self.config.setItem(self.config.rowCount() - 1, 1, item)

        item = QTableWidgetItem()
        self.config.setItem(self.config.rowCount() - 1, 2, item)

        self.config.resizeColumnToContents(0)


    def insertTemplate(self, idx):
        if idx == 0:
            return 0

        #i = self.config.rowCount()
        for par in self.templates[self.temp_list.itemText(idx)]:
            items = self.config.findItems(par, Qt.MatchExactly)

            if len(items) == 0:
                val = self.templates[self.temp_list.itemText(idx)][par]

                #print(par, val)
                if val == '__DEFAULT__':
                    for key in self.dic:
                        for p in self.dic[key]:
                            #print(p)
                            if p == par:
                                #print(par, p[2])
                                val = self.dic[key][p][1]

                self.insertConfig(par,val)

        self.config.resizeColumnToContents(0)
        self.sortConf()
        self.checkAllPar()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    sys.exit(app.exec())
