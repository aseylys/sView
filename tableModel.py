# -*- coding: utf-8 -*-
from PyQt5 import QtSql, QtCore, QtGui
import utils
import re

class STableModel(QtSql.QSqlTableModel):
    #Script Table Model, connects to whatever the designated script name is
    #in the .db 
    ExecuteRole = QtCore.Qt.UserRole + 1

    def __init__(self, parent = None, db = QtSql.QSqlDatabase()):
        QtSql.QSqlTableModel.__init__(self, parent, db)
        self.d = {}
        

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        #Names the last section
        if section == 5 and orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Notes'
        return super(QtSql.QSqlTableModel, self).headerData(section, orientation, role)


    def flags(self, index):
        #sets the flags for the columns, only the Notes column is editable
        #if index.column() == 5:
            #return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable


    def data(self, index, role):
        if role == self.ExecuteRole:
            _id = self.data(self.index(index.row(), self.fieldIndex("Step")), 
                            QtCore.Qt.DisplayRole)
            if _id in self.d.keys():
                return self.d[_id]
            return False

        #Align all non-executable steps in the middle, only applies to second column
        if role == QtCore.Qt.TextAlignmentRole:
            data = QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole)
            if data:
                if (not utils.getCP(data).endswith('.prc') and 'START' not in data.split('     ')[0]
                    and 'GV SET' not in data.split('     ')[0] and 'CLK' not in data.split('     ')[0]):
                    if index.column() == 2: return QtCore.Qt.AlignCenter

        #Coloring junk
        if role == QtCore.Qt.BackgroundRole:
            if self.data(index, self.ExecuteRole):
                return QtGui.QBrush(QtCore.Qt.lightGray)
            data = QtSql.QSqlTableModel.data(self, self.index(index.row(), 3), QtCore.Qt.DisplayRole)
            if data:
                if 'MILESTONE' in QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole):
                    if 'ABORT'in data or 'CONTINGENCY' in data: return QtGui.QBrush(QtCore.Qt.red)
                    else: return QtGui.QBrush(QtCore.Qt.cyan)

        return QtSql.QSqlTableModel.data(self, index, role)


    def getId(self, index):
        ix = self.fieldIndex("Step")
        return self.data(self.index(index.row(), ix), QtCore.Qt.DisplayRole)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == self.ExecuteRole:
            self.d[self.getId(index)] = value
            return True
        return QtSql.QSqlTableModel.setData(self, index, value, role)


    '''
    def roleNames(self):
        rn = QtSql.QSqlTableModel.roleNames(self)
        rn[self.SelectRole] = QtCore.QByteArray(b'execute')
        return rn
    '''

    def editScript(self, change, pModel, pRow, sRow):
        self.database().transaction()
        role = QtCore.Qt.DisplayRole
        steps = pModel.data(pModel.index(pRow, 6), role).split(';')
        desc = pModel.data(pModel.index(pRow, 5), role)

        if change == 'Add':   
            for i in range(len(steps)):
                _row = sRow + i
                self.insertRow(_row)
                self.setData(self.index(_row, 0), str(_row))
                for row in range(self.rowCount()):
                    if row >= _row:
                        self.setData(self.index(float(row), 0), row + 1)
                self.setData(self.index(_row, 1), '')
                self.setData(self.index(_row, 2), steps[i])
                self.setData(self.index(_row, 3), desc)
                self.setData(self.index(_row, 4), '')
                self.setData(self.index(_row, 5), '')

        if change == 'Change':
            #self.setData(self.index(sRow, 0), str(sRow))
            self.setData(self.index(sRow, 1), '')
            if len(steps) > 0:
                self.setData(self.index(sRow, 2), steps[0])
            else:
                self.setData(self.index(sRow, 2), '')
            self.setData(self.index(sRow, 3), desc)
            self.setData(self.index(sRow, 4), '')
            self.setData(self.index(sRow, 5), '')

        if change == 'Remove':
            self.removeRow(sRow)
            for row in range(self.rowCount()):
                if row >= sRow:
                    self.setData(self.index(row, 0), row)


        if self.submitAll(): 
            self.database().commit()
            self.select()
            return True
        else: return False

    def changeStep(self, pModel, pRow, sRow):
        self.database().transaction()

class ProxyModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, left, right, role = QtCore.Qt.DisplayRole):
            leftData = self.sourceModel().data(left, role)
            rightData = self.sourceModel().data(right, role)
            return int(leftData) < int(rightData)

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


