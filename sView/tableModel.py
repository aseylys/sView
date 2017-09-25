# -*- coding: utf-8 -*-
from PyQt5 import QtSql, QtCore, QtGui
import re

class TableModel(QtSql.QSqlTableModel):
    ExecuteRole = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None, db = QtSql.QSqlDatabase()):
        QtSql.QSqlTableModel.__init__(self, parent, db)
        self.d = {}

    def data(self, index, role):
        if role == self.ExecuteRole:
            _id = self.getId(index)
            if _id in self.d.keys():
                return self.d[_id]
            return False

        if role == QtCore.Qt.BackgroundRole:
            if self.data(index, self.ExecuteRole):
                return QtGui.QBrush(QtCore.Qt.red)
            if 'MILESTONE' in QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole):
                return QtGui.QBrush(QtCore.Qt.yellow)

        return QtSql.QSqlTableModel.data(self, index, role)

    def getId(self, index):
        ix = self.fieldIndex("id")
        return self.data(self.index(index.row(), ix), QtCore.Qt.DisplayRole)

    def setData(self, index, value, role):
        if role == self.ExecuteRole:
            self.d[self.getId(index)] = value
            return True
        return QtSql.QSqlTableModel.setData(self, index, value, role)

    def roleNames(self):
        rn = QtSql.QSqlTableModel.roleNames(self)
        rn[self.SelectRole] = QtCore.QByteArray(b'execute')
        return rn