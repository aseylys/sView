# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, uic

form, base = uic.loadUiType('ui/CpViewer.ui')

#TODO
#lineEdit validators
class CpViewer(QtWidgets.QDialog, base):
    def __init__(self, cp, parent = None):
        QtWidgets.QDialog.__init__(self, parent)

        
        self.setupUi(self)

        text = open(cp, 'r').read()
        self.textBrowse.setText(text)

        self.closeBut.clicked.connect(self.accept)



    