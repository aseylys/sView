# -*- coding: utf-8 -*-
from PyQt5 import QtSql, QtCore, QtGui
import utils
import re

class STableModel(QtSql.QSqlTableModel):
    #Script Table Model, connects to whatever the designated script name is
    #in the .db 
    def __init__(self, parent = None, db = QtSql.QSqlDatabase()):
        QtSql.QSqlTableModel.__init__(self, parent, db)


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        #Names the last section
        if section == 5 and orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Notes'
        return super(QtSql.QSqlTableModel, self).headerData(section, orientation, role)


    def flags(self, index):
        #sets the flags for the columns, only the Notes column is editable
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable


    def data(self, index, role):
        #Align all non-executable steps in the middle, only applies to second column
        if role == QtCore.Qt.TextAlignmentRole:
            data = QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole)
            if data:
                if (not utils.getCP(data).endswith('.prc') and 'START' not in data.split('     ')[0]
                    and 'GV SET' not in data.split('     ')[0] and 'CLK' not in data.split('     ')[0]):
                    if index.column() == 2: return QtCore.Qt.AlignCenter

        #Coloring junk
        if role == QtCore.Qt.BackgroundRole:
            data = QtSql.QSqlTableModel.data(self, self.index(index.row(), 3), QtCore.Qt.DisplayRole)
            if data:
                if 'MILESTONE' in QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole):
                    if 'ABORT'in data or 'CONTINGENCY' in data: return QtGui.QBrush(QtGui.QColor(204, 56, 36))
                    else: return QtGui.QBrush(QtGui.QColor(72, 177, 196))
            if '1' in QtSql.QSqlTableModel.data(self, self.index(index.row(), 6), QtCore.Qt.DisplayRole):
                return QtGui.QBrush(QtCore.Qt.lightGray)
            

        return QtSql.QSqlTableModel.data(self, index, role)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return QtSql.QSqlTableModel.setData(self, index, value, role)


    def editScript(self, change, sRow, steps, desc):
        self.database().transaction()

        if change == 'ADD':   
            for i in range(len(steps)):
                _row = sRow + i
                self.insertRow(_row)
                self.setData(self.index(float(_row), 0), float(_row))
                for row in range(self.rowCount()):
                    if row >= _row:
                        self.setData(self.index(float(row), 0), row + 1)
                self.setData(self.index(_row, 1), '')
                self.setData(self.index(_row, 2), steps[i])
                self.setData(self.index(_row, 3), desc)
                self.setData(self.index(_row, 4), '')
                self.setData(self.index(_row, 5), '')
                self.setData(self.index(_row, 6), '')

        if change == 'CHANGE':
            for i in range(len(steps)):
                _row = sRow + i
                self.setData(self.index(float(_row), 0), float(_row))
                for row in range(self.rowCount()):
                    if row >= _row:
                        self.setData(self.index(float(row), 0), row + 1)
                self.setData(self.index(_row, 1), '')
                self.setData(self.index(_row, 2), steps[i])
                self.setData(self.index(_row, 3), desc)
                self.setData(self.index(_row, 4), '')
                self.setData(self.index(_row, 5), '')
                self.setData(self.index(_row, 6), '')

        if change == 'REMOVE':
            self.removeRow(sRow)
            for row in range(self.rowCount()):
                if row >= sRow:
                    self.setData(self.index(row, 0), float(row))

        if self.submitAll(): 
            self.database().commit()
            self.select()
            return True
        else:
            self.database().rollback() 
            return False


class PTableModel(QtSql.QSqlTableModel):
    #Model for the PACR List which connects to the PACR table in the .db
    def __init__(self, parent = None, db = QtSql.QSqlDatabase()):
        QtSql.QSqlTableModel.__init__(self, parent, db)


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        return super(QtSql.QSqlTableModel, self).headerData(section, orientation, role)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable


    def data(self, index, role):
        return QtSql.QSqlTableModel.data(self, index, role)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return QtSql.QSqlTableModel.setData(self, index, value, role)

