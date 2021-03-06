# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, uic


class QuickNote(QtWidgets.QDialog, uic.loadUiType('ui/quickNote.ui')[0]):
    #The note dialog, only way to add a note
    def __init__(self, note, parent = None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.noteText = ''
        self.noteEdit.setPlainText(note)
        self.closeBut.clicked.connect(self.retNote)
        self.okBut.clicked.connect(self.retNote)


    def retNote(self):
        self.noteText = self.noteEdit.toPlainText()
        self.accept()


class CpViewer(QtWidgets.QDialog, uic.loadUiType('ui/cpviewer.ui')[0]):
    #Cp viewing dialog, does  nothign but displays the content of a cp
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

    