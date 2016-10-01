#!/usr/bin/env python

import sys, os
from PyQt4.QtGui import (
    QWidget,QTableWidgetItem,
    QHBoxLayout, QCheckBox,
    QVBoxLayout,
    QListWidget,
    QSplitter,
    QStyleFactory,
    QApplication, QBrush,
    QComboBox, QHeaderView,
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
    "Resource Consumption" : "/static/runtime-config-resource.html" ,
    "Write Ahead Log" : "/static/runtime-config-wal.html" ,
    "Replication" : "/static/runtime-config-replication.html" ,
    "Query Planning" : "/static/runtime-config-query.html" ,
    "Error Reporting and Logging" : "/static/runtime-config-logging.html" ,
    "Run-time Statistics" : "/static/runtime-config-statistics.html" ,
    "Automatic Vacuuming" : "/static/runtime-config-autovacuum.html" ,
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
        self.dic = {}
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
        self.right.verticalHeader().setVisible(False)
        self.right.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.right.itemClicked.connect(self.changeCfg)
        self.right.cellEntered.connect(self.changeCsr)
        #self.right.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.right.customContextMenuRequested.connect(self.on_context_menu)


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
        self.updateTemplates()
        #self.choosePversion(self.combo.count()-1)


    # def on_context_menu(self, point):
    #     item = self.right.itemAt(point)
    #
    #     if item and item.column() == 4:
    #         menu = QMenu()
    #         act = menu.addAction('Show more info')
    #         action = menu.exec_(self.right.mapToGlobal(point))
    #         menu.popup(QCursor.pos())
    #
    #         if action == act:
    #             self.onRenameHtml(self.right.item(item.row(),1).text())


    def updateTemplates(self):
        ver = self.combo.currentText()[9:]
        self.templates = templates.templates(ver)

        self.temp_list.clear()

        for t in sorted(self.templates, ):
            self.temp_list.addItem(t)



    def clearConfig(self):
        self.config.setRowCount(0)





    def onRenameHtml(self, var):
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

        #self.cfglabel.setText(fname.split('/')[-1])
        self.config.setRowCount(0)

        idx = 0

        f = open(fname, 'r')
        for l in f:
            if len(l.strip()) == 0 or l.strip()[0] == '#':
                continue

            par = l.split('#')[0].split('=')[0].strip()
            val = l.split('#')[0].split('=')[1].strip()
            self.config.insertRow(idx)
            item = QTableWidgetItem(str(par))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setToolTip('Double-click for description')
            self.config.setItem(idx, 0, item)
            item = QTableWidgetItem(val)
            item.setToolTip('Double-click to edit')
            self.config.setItem(idx, 1, item)
            item = QTableWidgetItem()
            self.config.setItem(idx, 2, item)
            idx += 1


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
                    if par == p[0]:
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

        f = open(self.basedir + '/params%s' %ver, 'r')

        for l in f:
            li = l.rstrip('\n').split('\t')

            if li[0] not in self.dic:
                self.dic[li[0]] = [li[1:]]
            else:
                self.dic[li[0]].append(li[1:])

        for key in self.dic:
            self.mid.addItem(key)

        self.mid.sortItems()
        self.mid.setSpacing(2)
        self.checkAllPar()
        self.sortConf()
        f.close()

        self.updateTemplates()

        #print (self.dic)
        #self.var = 1

    def choosePar(self, litem):
        self.right.setRowCount(0)
        #print(self.dic['Other'])
        #print(self.dic[litem.text()])
        for idx, l in enumerate(self.dic[litem.text()]):
            self.right.insertRow(idx)

            #checkbox
            item = QTableWidgetItem()
            if len(self.config.findItems(l[0], Qt.MatchExactly)) != 0:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.right.setItem(idx, 0, item)

            # name
            item = QTableWidgetItem(l[0])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 1, item)

            # type
            item = QTableWidgetItem(l[1])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 2, item)

            # default
            item = QTableWidgetItem(l[2])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 3, item)

            # description
            item = QTableWidgetItem(l[3])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.right.setItem(idx, 4, item)

            item = QTableWidgetItem('More...')
            font = item.font()
            font.setUnderline(True)
            item.setFont(font)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
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
        val = self.config.item(r, 1).text()
        self.config.item(r,c).setSelected(True)
        found = False

        if len(self.dic) == 0:
            return 0
        #print(par)

        for key in self.dic:
            for l in self.dic[key]:
                if par in l:
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
            QMessageBox.about(self,'Parameter Not found', 'This parameter is not standard')


    def checkAllPar(self):
        for r in range(self.config.rowCount()):
            self.checkPar(r)

    def checkPar(self, row):
        if self.config.item(row, 0) is not None:
            par = self.config.item(row, 0).text()
        else:
            return 0

        if self.config.item(row, 1) is not None:
            val = self.config.item(row, 1).text()
        else:
            return 0

        found = False
        white = True

        # if self.config.item(row, 0).backgroundColor().red() == 255 \
        #     and self.config.item(row, 0).backgroundColor().green() == 200\
        #     and self.config.item(row, 0).backgroundColor().blue() == 255:

        if self.config.item(row, 0).backgroundColor() == QColor(200, 255, 200, 255):
            return 0

        for key in self.dic:
            for l in self.dic[key]:
                if par in l:
                    found = True

                    if str(l[2]) != str(val):
                        #print(l[2], val)
                        white = False
                        self.config.item(row,0).setBackgroundColor(QColor(200, 255, 255, 255))
                        self.config.item(row, 1).setBackgroundColor(QColor(200, 255, 255, 255))

                    break

        if len(self.dic) == 0:
            found = True

        # colr red if not found
        if not found:
            white = False
            self.config.item(row, 0).setBackgroundColor(QColor(255, 200, 200, 255))
            self.config.item(row, 1).setBackgroundColor(QColor(255, 200, 200, 255))

        # color white when same as default
        if white:
            self.config.item(row, 0).setBackgroundColor(Qt.white)
            self.config.item(row, 1).setBackgroundColor(Qt.white)



    def changeCfg(self, item):
        for c in range(self.right.columnCount()):
            for r in range(self.right.rowCount()):
                self.right.item(r,c).setSelected(False)

        if item is not None:
            row = item.row()
            for c in range(self.right.columnCount()):
                self.right.item(row, c).setSelected(True)

        if item.column() == 0 and item.checkState() == 2:
            row = item.row()
            idx = self.config.rowCount()
            self.config.insertRow(idx)
            i = QTableWidgetItem(self.right.item(row,1).text())
            i.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            i.setBackgroundColor(QColor(200, 255, 200, 255))
            self.config.setItem(idx, 0, i)
            i = QTableWidgetItem(self.right.item(row, 3).text())
            i.setBackgroundColor(QColor(200, 255, 200, 255))
            #i.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.config.setItem(idx, 1, i)

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


    def insertTemplate(self, idx):
        i = self.config.rowCount()
        for par in self.templates[self.temp_list.itemText(idx)]:
            items = self.config.findItems(par, Qt.MatchExactly)

            if len(items) == 0:
                val = self.templates[self.temp_list.itemText(idx)][par]
                #print(par, val)
                self.config.insertRow(i)
                item = QTableWidgetItem(par)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setToolTip('Double-click name to jump to description')
                self.config.setItem(i, 0, item)
                item = QTableWidgetItem(val)
                item.setToolTip('Double-click value to edit')
                self.config.setItem(i, 1, item)
                item = QTableWidgetItem()
                self.config.setItem(i, 2, item)
                i += 1



        self.config.resizeColumnToContents(0)
        self.sortConf()
        self.checkAllPar()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    sys.exit(app.exec())
