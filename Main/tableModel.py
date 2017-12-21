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
        #sets header data
        return super(QtSql.QSqlTableModel, self).headerData(section, orientation, role)


    def flags(self, index):
        #sets the flags for the columns, only the Notes column is editable
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable


    def data(self, index, role):
        #Align all non-executable steps in the middle, only applies to second column
        if role == QtCore.Qt.TextAlignmentRole:
            data = QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole)
            if data:
                if index.column() == 2:
                    #If it's not an executable step, align it in the center, else left 
                    if (not utils.getCP(data).endswith('.prc') and 
                        not bool(re.search('START|GV SET|CLK', data.split('     ')[0], re.I))):
                            return QtCore.Qt.AlignCenter
                    else: return QtCore.Qt.AlignLeft
                #Aligns step # and timing cols
                if index.column() in [0, 1, 6]:
                    return QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter

        #Coloring logic
        if role == QtCore.Qt.BackgroundRole:
            data = QtSql.QSqlTableModel.data(self, self.index(index.row(), 3), QtCore.Qt.DisplayRole)
            if data:
                #If executed, color grey
                if '1' in QtSql.QSqlTableModel.data(self, self.index(index.row(), 6), QtCore.Qt.DisplayRole):
                    return QtGui.QBrush(QtGui.QColor(204, 201, 204))
                else:
                    #If not executed color accordingly, MILESTONE=blue, CONTIGENCY=red
                    if 'MILESTONE' in QtSql.QSqlTableModel.data(self, self.index(index.row(), 2), QtCore.Qt.DisplayRole):
                        if 'ABORT'in data or 'CONTINGENCY' in data: return QtGui.QBrush(QtGui.QColor(255, 131, 114))
                        else: return QtGui.QBrush(QtGui.QColor(139, 183, 191))
            
        return QtSql.QSqlTableModel.data(self, index, role)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return QtSql.QSqlTableModel.setData(self, index, value, role)


    def editScript(self, change, sRow, steps, desc):
        #Different options on script editing
        #It's pretty self expalnantory
        self.database().transaction()

        if change == 'ADD':   
            for i in range(len(steps)):
                print(len(steps))
                _row = sRow + i
                print(_row)
                self.insertRow(_row)
                self.setData(self.index(_row, 0), _row)
                for row in range(self.rowCount()):
                    if row >= _row:
                        self.setData(self.index(row, 0), row + 1)
                self.setData(self.index(_row, 1), '')
                self.setData(self.index(_row, 2), steps[i])
                self.setData(self.index(_row, 3), desc)
                self.setData(self.index(_row, 4), '')
                self.setData(self.index(_row, 5), '')
                self.setData(self.index(_row, 6), '')

        if change == 'CHANGE':
            for i in range(len(steps)):
                _row = sRow + i
                self.setData(self.index(_row, 0), _row)
                for row in range(self.rowCount()):
                    if row >= _row:
                        self.setData(self.index(row, 0), row + 1)
                self.setData(self.index(_row, 1), self.data(self.index(_row, 1), role = QtCore.Qt.DisplayRole))
                self.setData(self.index(_row, 2), steps[i])
                self.setData(self.index(_row, 3), desc)
                self.setData(self.index(_row, 4), '')
                self.setData(self.index(_row, 5), self.data(self.index(_row, 5), role = QtCore.Qt.DisplayRole))
                #De-execute step
                self.setData(self.index(_row, 6), '')

        if change == 'REMOVE':
            self.removeRow(sRow)
            for row in range(self.rowCount()):
                if row >= sRow:
                    self.setData(self.index(row, 0), row)

        if self.submitAll(): 
            self.database().commit()
            self.select()
            return True

        else:
            #If for some reason the database wasn't updated, 
            #it'll roll it's last change back
            self.database().rollback() 
            return False