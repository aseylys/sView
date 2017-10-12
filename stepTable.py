# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
import utils
import re

class pStepsTable(QtWidgets.QTableWidget):
    #Custom QTableWidget for the PACR substeps
    def __init__(self, parent = None):
        QtWidgets.QTableWidget.__init__(self, parent)


    def info(self):
        return ';'.join([self.item(_row, 1).text() for _row in range(self.rowCount())])


    def addRow(self):
        _row = self.rowCount()
        self.insertRow(_row)
        col1 = QtWidgets.QTableWidgetItem(str(self.rowCount()))
        col1.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        col1.setTextAlignment(QtCore.Qt.AlignCenter)
        self.setItem(_row, 0, col1)


    def delRow(self, row):
        self.removeRow(row)
        for _row in range(self.rowCount()):
            col1 = QtWidgets.QTableWidgetItem(str(_row + 1))
            col1.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(_row, 0, col1)


    def populate(self, data):
        self.reset()
        if data:
            data = data.split(';')
            for _row in range(len(data)):
                self.addRow()
                self.setItem(_row, 1, QtWidgets.QTableWidgetItem(data[_row]))
        else: return


    def reset(self):
        if self.rowCount() > 0:
            while self.rowCount() > 0: self.removeRow(0)