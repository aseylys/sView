# -*- coding: utf-8 -*-
import sys, os, logging, utils
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMenu
from PyQt5 import uic, QtSql, QtCore, QtGui
from tableModel import TableModel
from settingsDia import Settings


logging.basicConfig(level = logging.INFO)
form, base = uic.loadUiType('ui/sView.ui')

#Ctrl+Click to copy CP
#Shift+Click to copy params
class MainWindow(base, form):
    def __init__(self):
        super(base, self).__init__()
        self.setupUi(self)
        self.openMenu.triggered.connect(self.connDB)
        self.openSettings.triggered.connect(self.settings)
        self.model = None
        self.cpDir = ''
        #Create Context Menu if right clicked
        self.tableView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self.tableContextMenu)

        self.tableView.clicked.connect(self.getRowData)
        self.cb = QApplication.clipboard()
        self.cb.clear(mode = self.cb.Clipboard)
    
    def connDB(self):
        #Attempt to connect to SQL file chosen in Dialog
        file = QFileDialog.getOpenFileName(self, 
            'Connect to Script',  
            os.path.dirname(os.path.realpath(__file__)),
            'Database Files (*.db)' 
            )[0]
        logging.info(' Connecting to: ' + file)
        self.scriptName = os.path.basename(file.replace('.db', '').replace('_', ' '))
        self.setWindowTitle(self.scriptName + ' - sView')
        try:
            db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
            db.setDatabaseName(file)

            if not db.open():
                QMessageBox.critical(None, 'Cannot Connect to DB',
                     'Unable to establish a database connection.',
                     QMessageBox.Cancel
                )
            else: self.buildModel(db, file)
        except:
            logging.error(' An Error Occurred: ' + sys.exc_info()[0])


    def settings(self):
        setDia = Settings(self)
        if setDia.exec_():
            if setDia.result():
                self.cpDir = setDia.directory
                logging.info(' Set CP Dir to ' + self.cpDir)


    def buildModel(self, db, table):
        #Builds and formats the table
        self.model = TableModel(self, db)
        self.model.setTable(os.path.basename(table.replace('.db', '')))
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.select()
        self.tableView.setModel(self.model)
        #Hide irrelevant cols
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(4, True)
        #Auto Resize cols
        self.tableView.resizeColumnToContents(2)
        self.tableView.resizeColumnToContents(3)
        self.tableView.resizeRowsToContents()
 

    def tableContextMenu(self, pos):
        #Handles the menu that appears when right clicking
        if self.model:
            menu = QMenu()
            stepx = menu.addAction('Mark Step as Executed')
            stepdx = menu.addAction('Clear Step Execution')
            menu.addSeparator()
            viewcp = menu.addAction('View CP')

            if not self.cpDir: 
                logging.info(' CP Directory Not Selected')
                viewcp.setEnabled(False)

            action = menu.exec_(self.tableView.mapToGlobal(pos))
            index = self.model.index(self.tableView.rowAt(pos.y()), 2)

            if action == viewcp:
                cp = utils.getCP(self.model.data(index, role = QtCore.Qt.DisplayRole).strip())

            if action == stepx:
                if self.model:
                    index = self.model.index(self.tableView.rowAt(pos.y()), 2)
                    self.model.setData(index, True, TableModel.ExecuteRole)
                    self.model.dataChanged.emit(self.model.index(index.row(), 0),
                                                  self.model.index(index.row(), self.model.columnCount()-1),
                                                  [QtCore.Qt.BackgroundRole])
            if action == stepdx:
                if self.model:
                    index = self.model.index(self.tableView.rowAt(pos.y()), 2)
                    self.model.setData(index, False, TableModel.ExecuteRole)
                    self.model.dataChanged.emit(self.model.index(index.row(), 0),
                                                  self.model.index(index.row(), self.model.columnCount()-1),
                                                  [QtCore.Qt.BackgroundRole])

    def getRowData(self, index):
        cp = self.model.index(index.row(), 2)
        data = self.model.data(cp, role = QtCore.Qt.DisplayRole).strip()
        modifiers = QApplication.keyboardModifiers()
        if data.strip():
            if modifiers == QtCore.Qt.ControlModifier:
                params = utils.getParams(data)
                logging.info(' Copied Params: ' + params)
            else:
                cb_cp = utils.getCP(data)
                logging.info(' Copied CP: ' + cb_cp)
                self.cb.setText(cb_cp, mode = self.cb.Clipboard)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())