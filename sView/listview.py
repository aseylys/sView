from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout
from PyQt5 import QtSql, QtCore
import os

class ScriptList(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)

    def buildModel(self, db, table):
        self.model = QtSql.QSqlTableModel(self, db)
        self.model.setTable(os.path.basename(table.replace('.db', '')))
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.select()

        self.setModel(self.model)
        '''
        for row in self.model.rowCount():
            print(self.model.record(row).value("Timing"))
        '''