# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, uic
import os


form, base = uic.loadUiType('ui/settings.ui')

class Settings(QtWidgets.QDialog, form):
    def __init__(self, parent = None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setupUi(self)
        self.directory = parent.cpDir
        self.cpDir.setText(self.directory)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)

        self.browseBut.clicked.connect(self.browseDir)

    def browseDir(self):
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(self, 
            'Select a Folder',  
            os.path.dirname(os.path.realpath(__file__)),
            QtWidgets.QFileDialog.ShowDirsOnly 
            )
        self.cpDir.setText(self.directory)




if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    myWindow = Settings(None)
    myWindow.show()
    app.exec_()