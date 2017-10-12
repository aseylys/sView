# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, uic


form, base = uic.loadUiType('ui/cpviewer.ui')

class CpViewer(QtWidgets.QDialog, form):
    def __init__(self, cp, parent = None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setupUi(self)

        text = open(cp, 'r').read()
        self.textBrowse.setText(text)

        self.closeBut.clicked.connect(self.close)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    myWindow = CpViewer('C:\\Users\\trevor.doll\\Desktop\\sView\\ZFEAE01UPLOD.prc')
    myWindow.show()
    app.exec_()

    