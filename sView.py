# -*- coding: utf-8 -*-
import os, logging, utils, time
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMenu, QTableWidgetItem, QTableWidget
from PyQt5 import uic, QtSql, QtCore, QtGui
from tableModel import *
from settingsDia import Settings
from tableDias import CpViewer, QuickNote

logging.basicConfig(level = logging.INFO)
form, base = uic.loadUiType('ui/sView.ui')

class TimeThread(QtCore.QThread):
    #Threaded Timer, allows for background updates every 1 second
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        

    def run(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.parent.timerUpdate)
        self.timer.start(2500)
        
        self.exec_()

class MainWindow(base, form):
    def __init__(self):
        super(base, self).__init__()
        self.setupUi(self)
        self.openMenu.triggered.connect(self.connDB)
        self.openSettings.triggered.connect(self.settings)
        self.sModel = None
        self.pModel = None
        self.cpDir = ''
        self.DR = QtCore.Qt.DisplayRole

        self.user = os.getlogin() + str(time.time()).split('.')[1]

        #Create Context Menu if right clicked
        self.tableView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self.tableContextMenu)

        self.tableView.clicked.connect(self.getSData)

        #Clipboard junk for copying CP
        self.cb = QApplication.clipboard()
        self.cb.clear(mode = self.cb.Clipboard)

        ###############PACR Tab###############
        self.saveP.clicked.connect(self.savePacr)
        self.newP.clicked.connect(self.newPacr)
        self.pushP.clicked.connect(self.pushPacr)
        self.delP.clicked.connect(self.delPacr)

        #Only allows numbers in the step number box
        self.stepEdit.setValidator(QtGui.QIntValidator(0, 999, self.stepEdit))
        self.authorEdit.setText(self.user)
        self.createdEdit.setText(time.strftime("%x"))

        self.pTable.clicked.connect(self.getPData)
        self.addStep.clicked.connect(self.addpStep)
        self.delStep.clicked.connect(self.delpStep)

        self.acceptBut.clicked.connect(lambda: self.fd('A'))
        self.rejectBut.clicked.connect(lambda: self.fd('R'))
        ##################################4####
        
        thread = TimeThread(self)
        thread.start()


    def timerUpdate(self):
        #The Actual timer funciton that is called every second, 
        #updates the PACR labels and checks for updates to both tables
        if self.sModel and self.pModel:
            self.checkReview()
            if self.tabWidget.currentIndex() != 1:
                self.sModel.select()
                self.pModel.select()
                self.tableView.resizeColumnToContents(2)
                self.tableView.resizeColumnToContents(3)
                self.tableView.resizeRowsToContents()


    def settings(self):
        #Settings dialog, allows for setting the CP Director
        setDia = Settings(self)
        if setDia.exec_():
            if setDia.result():
                self.cpDir = setDia.directory
                logging.info(' Set CP Dir to ' + self.cpDir)
                self.cmdLabel.setText('Set CP Dir to: ' + self.cpDir)


    def closeEvent(self, event):
        #Resubmits everything to database on exit if models exists
        if self.sModel and self.pModel:
            logging.info(' Closing and Submitting...')
            self.sModel.submitAll()
            self.pModel.submitAll()


    def warn(self, warn):
        #Warning dialog with every warning I could think of
        warnMessage = {
            'No Database' : 'No Database Connected, Open Database',
            'Step Conflict' : 'Provided Step Number Already Exists in PACR List',
            'PACR Fields Incomplete' : 'Please fill in all of the "*" fields to save PACR',
            'No PACR Created' : 'Create a PACR First',
            'Already Pushed' : 'PACR was already pushed for review',
            'Out of Bounds' : 'Step Number is range of script',
            'Unknown' : 'An uknown error has occured',
            'File Not Found' : 'The selected CP does not seem to be in the selected directory'
        }

        QMessageBox.critical(None, warn, warnMessage[warn], QMessageBox.Ok)


    def connDB(self):
        #Attempt to connect to SQL file chosen in Dialog
        file = QFileDialog.getOpenFileName(self, 
            'Connect to Script',  
            os.path.dirname(os.path.realpath(__file__)),
            'Database Files (*.db)' 
            )[0]
        logging.info(' Connecting to: ' + file)
        self.cmdLabel.setText('Connecting to: ' + file)
        self.scriptName = os.path.basename(file.replace('.db', '').replace('_', ' '))
        self.setWindowTitle(self.scriptName + ' - sView')
        try:
            db = QtSql.QSqlDatabase.addDatabase('QSQLITE', self.user)
            db.setUserName(self.user)
            db.setDatabaseName(file)
            if not db.open():
                QMessageBox.critical(None, 'Cannot Connect to DB',
                     'Unable to establish a database connection.',
                     QMessageBox.Cancel
                )
            else: self.buildModel(db, file)
        except:
            logging.error(' An Error Occurred')


    def buildModel(self, db, table):
        #Builds and formats the Script Table
        self.sModel = STableModel(self, db)
        self.sModel.setTable(os.path.basename(table.replace('.db', '')))
        #Makes it so real-time changes to script update .db
        self.sModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        #Orders the script by Step #, the fact that I had to hardcode
        #this SQL command is retarded, you'd think there'd be a 
        #Qt command
        self.sModel.setFilter('1=1 ORDER BY Step * 1 ASC')
        self.sModel.select()
        self.tableView.setModel(self.sModel)
        #Hide irrelevant cols
        self.tableView.setColumnHidden(4, True)
        #self.tableView.setColumnHidden(6, True)
        #Auto Resize cols
        self.tableView.resizeColumnToContents(2)
        self.tableView.resizeColumnToContents(3)
        self.tableView.resizeRowsToContents()

        #Build and formats the PACR Table
        self.pModel = PTableModel(self, db)
        self.pModel.setTable('PACR')
        self.pModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.pModel.select()
        self.pTable.setModel(self.pModel)
        #Hide irrelevant cols
        self.pTable.setColumnHidden(0, True)
        self.pTable.setColumnHidden(1, True)
        self.pTable.setColumnHidden(5, True)
        self.pTable.setColumnHidden(6, True)
        self.pTable.setColumnHidden(8, True)
        self.pTable.resizeRowsToContents()

        #Calls initial review counter
        self.checkReview()    


    def tableContextMenu(self, pos):
        #Handles the menu that appears when right clicking
        if self.sModel:
            menu = QMenu()
            stepx = menu.addAction('Mark Step as Executed')
            stepdx = menu.addAction('Clear Step Execution')
            menu.addSeparator()
            viewcp = menu.addAction('View CP')
            menu.addSeparator()
            note = menu.addAction('Quick Note')

            if not self.cpDir: 
                logging.info(' CP Directory Not Selected')
                self.cmdLabel.setText('CP Directory Not Selected')
                viewcp.setEnabled(False)

            action = menu.exec_(self.tableView.mapToGlobal(pos))
            index = self.sModel.index(self.tableView.rowAt(pos.y()), 2)
            _row = index.row()
            if action == viewcp:
                cp = utils.getCP(self.sModel.data(index, role = self.DR).strip())
                if cp.endswith('.prc'):
                    logging.info(' Viewing CP: ' + cp)
                    self.cmdLabel.setText('Viewing CP: ' + cp)
                    try:
                        viewer = CpViewer(os.path.join(self.cpDir, cp), self)
                        viewer.show()
                    except FileNotFoundError:
                        self.warn('File Not Found')
                
            #Handles step execution
            if action == stepx:
                index = self.sModel.index(self.tableView.rowAt(pos.y()), 6)
                self.sModel.setData(index, '1')
                logging.info(' Executed Step: ' + str(_row + 1))
                self.cmdLabel.setText('Executed Step: ' + str(_row + 1))
                
            if action == stepdx:
                index = self.sModel.index(self.tableView.rowAt(pos.y()), 6)
                self.sModel.setData(index, '')
                logging.info(' De-Executed Step: ' + str(_row + 1))
                self.cmdLabel.setText('De-Executed Step: ' + str(_row + 1))

            if action == note:
                index = self.sModel.index(self.tableView.rowAt(pos.y()), 5)
                note = QuickNote(self.sModel.data(index, role = self.DR), self)
                if note.exec_():
                    if note.result():
                        self.sModel.setData(index, note.noteText)


    def getSData(self, index):
        #Data handling inside row
        #If clicked: copy CP
        #If Ctrl + Click: copy Params
        data = self.sModel.data(self.sModel.index(index.row(), 2), role = self.DR).strip()
        _modifiers = QApplication.keyboardModifiers()
        if data.strip():
            if _modifiers == QtCore.Qt.ControlModifier:
                params = utils.getParams(data)
                logging.info(' Copied Params: ' + params)
                #self.cmdLabel.setText('Copied Params: ' + params)
                self.cb.setText(params, mode = self.cb.Clipboard)
            else:
                cb_cp = utils.getCP(data)
                logging.info(' Copied CP: ' + cb_cp)
                #self.cmdLabel.setText('Copied CP: ' + cb_cp)
                self.cb.setText(cb_cp, mode = self.cb.Clipboard)


    def getPData(self, index):
        #Populates the fields based on currently selected row
        logging.info(' Selected PACR ID: ' + str(index.row() + 1))

        #Sets all the fields to selected row
        _row = index.row()
        self.idLabel.setText(str(_row + 1))
        self.createdEdit.setText(self.pModel.data(self.pModel.index(_row, 0), 
                                    role = self.DR))
        self.authorEdit.setText(self.pModel.data(self.pModel.index(_row, 1), 
                                    role = self.DR))
        self.stepEdit.setText(self.pModel.data(self.pModel.index(_row, 2), 
                                    role = self.DR))
        self.typeBox.setCurrentIndex(self.typeBox.findText(self.pModel.data(self.pModel.index(_row, 3), 
                                    role = self.DR), QtCore.Qt.MatchFixedString))
        self.respBox.setCurrentIndex(self.respBox.findText(self.pModel.data(self.pModel.index(_row, 4), 
                                    role = self.DR), QtCore.Qt.MatchFixedString))
        self.rationale.setPlainText(self.pModel.data(self.pModel.index(_row, 5),
                                    role = self.DR))
        self.pSteps.populate(self.pModel.data(self.pModel.index(_row, 6),
                                    role = self.DR))
        self.stateLabel.setText(self.pModel.data(self.pModel.index(_row, 7), 
                                    role = self.DR))
        self.fdLabel.setText(self.pModel.data(self.pModel.index(_row, 8), 
                                    role = self.DR))

        #Changes State style depending on state
        #Also changes button functinality
        if self.stateLabel.text() == 'Dev':
            self.stateLabel.setStyleSheet('background-color: rgb(128, 128, 128); font: 75 8pt "MS Shell Dlg 2";')
            self.acceptBut.setEnabled(False)
            self.rejectBut.setEnabled(False)
            #Only the user who created the PACR can edit it
            if self.pModel.data(self.pModel.index(_row, 1), role = self.DR) == self.user:
                self.saveP.setEnabled(True)
                self.delP.setEnabled(True)
            else: 
                self.saveP.setEnabled(False)
                self.delP.setEnabled(False)
            self.pushP.setEnabled(True)
        elif self.stateLabel.text() == 'Review':
            self.stateLabel.setStyleSheet('background-color: rgb(255, 255, 0); font: 75 8pt "MS Shell Dlg 2";')
            self.acceptBut.setEnabled(True)
            self.rejectBut.setEnabled(True)
            if self.pModel.data(self.pModel.index(_row, 1), role = self.DR) == self.user:
                self.saveP.setEnabled(True)
                self.delP.setEnabled(True)
            else: 
                self.saveP.setEnabled(False)
                self.delP.setEnabled(False)
            self.pushP.setEnabled(False)
        else:
            self.stateLabel.setStyleSheet('background-color: rgb(85, 255, 0); font: 75 8pt "MS Shell Dlg 2";')
            self.acceptBut.setEnabled(False)
            self.rejectBut.setEnabled(False)
            self.saveP.setEnabled(False)
            self.pushP.setEnabled(False)
            self.delP.setEnabled(False)


    def resetPFields(self):
        #Resets all fields to their initial cofigs
        self.saveP.setEnabled(True)
        self.pushP.setEnabled(True)
        self.idLabel.setText('')
        self.authorEdit.setText(self.user)
        self.createdEdit.setText(time.strftime("%x"))
        self.stepEdit.setText('')
        self.typeBox.setCurrentIndex(0) 
        self.respBox.setCurrentIndex(0)
        self.rationale.setPlainText('')
        self.pSteps.reset()


    def newPacr(self):
        #Creates a new PACR with blank form to fill out
        #PACR ID is determined by the model count
        self.resetPFields()
        if self.pModel:
            _row = self.pModel.rowCount()

            self.pModel.insertRow(_row)
            #Still haven't worked out the bugs for programitically setting curindex
            #self.pTable.setCurrentIndex(self.pModel.index(_row, 0))
            logging.info(' Created New PACR ID: ' + str(_row + 1))
            self.idLabel.setText(str(_row + 1))
            self.stateLabel.setText('Dev')
            self.pModel.setData(self.pModel.index(_row, 7), 'Dev')
            self.pModel.setData(self.pModel.index(_row, 1), self.authorEdit.text())
            self.pModel.setData(self.pModel.index(_row, 0), self.createdEdit.text())
        
        else: self.warn('No Database')


    def savePacr(self):
        #Saves PACR and submits all to .db if the form is completed
        #Steps and rationale don't have to be filled to be valid form
        def _save():
            #Private save funct, mostly to avoid copying lines of code
            logging.info(' Saving PACR ID: '  + str(_row + 1))
                            
            self.pModel.setData(self.pModel.index(_row, 2), self.stepEdit.text())
            self.pModel.setData(self.pModel.index(_row, 3), self.typeBox.currentText())
            self.pModel.setData(self.pModel.index(_row, 4), self.respBox.currentText())
            self.pModel.setData(self.pModel.index(_row, 5), self.rationale.toPlainText())

            self.pModel.setData(self.pModel.index(_row, 6), self.pSteps.info())
        #Fields that need to be completed for it to be valid
        fields = [self.createdEdit.text(), 
                    self.authorEdit.text(), self.stepEdit.text(),
                    self.typeBox.currentText(), self.respBox.currentText()]

        #Validates that all "*" fields are completed and then adds to db
        if self.pModel:
            if self.pModel.rowCount() >= 1:
                if all(field for field in fields):
                    #Checks to make sure there are no Step # conflicts
                    _steps = [self.pModel.data(self.pModel.index(row, 2), self.DR) 
                                    for row in range(self.pModel.rowCount())]
                    _row = self.pTable.currentIndex().row()
                    stepNum = self.stepEdit.text()
                    #If editing an already Pushed PACR, Pull it back
                    if self.pModel.data(self.pModel.index(_row, 7), role = self.DR) != 'Dev':
                        self.pModel.setData(self.pModel.index(_row, 7), 'Dev')
                        self.pActsNum.setText(str(int(self.pActsNum.text()) - 1))
                        logging.info(' Pulled PACR: ' + str(_row + 1))
                        self.cmdLabel.setText('Pulled PACR: ' + str(_row + 1))
                        self.pushP.setEnabled(True)
                        self.fdLabel.setText('')
                        self.checkReview()

                    if stepNum != 0 and int(stepNum) < self.sModel.rowCount() + 1:
                        if self.typeBox.currentText() != 'Change':
                            if stepNum not in _steps or stepNum == self.pModel.data(self.pModel.index(_row, 2), self.DR): _save()
                            else: self.warn('Step Conflict')
                        else:
                            _save()
                    #Various warnings to not implement logic
                    else: self.warn('Out of Bounds')
                else: self.warn('PACR Fields Incomplete')
            else: self.warn('No PACR Created')
        else: self.warn('No Database')


    def pushPacr(self):
        #Push a PACR out for review by the FD
        _row = self.pTable.currentIndex().row()
        if self.pModel.data(self.pModel.index(_row, 7), role = self.DR) == 'Dev':
            self.savePacr()
            #Disables re-pushing without saving
            self.pushP.setEnabled(False)
            self.saveP.setEnabled(True)

            logging.info(' Pushed PACR ID: ' + str(_row + 1))
            self.cmdLabel.setText('Pushed PACR ID: ' + str(_row + 1))
            self.pModel.setData(self.pModel.index(_row, 7), 'Review')
            self.pushP.setEnabled(False)
            self.checkReview()
            self.pModel.submitAll()
            

        else: self.warn('Already Pushed')


    def delPacr(self):
        if self.pModel:
            if self.pModel.rowCount() > 0:
                _row = self.pTable.currentIndex().row()

                #self.pModel.deleteRowFromTable(_row)
                self.pModel.removeRow(_row)
                if self.pModel.submitAll(): self.pModel.database().commit()
                self.pModel.select()
                logging.info(' Deleted PACR ID: ' + str(_row + 1))
                self.cmdLabel.setText('Deleted PACR ID: ' + str(_row + 1))
                self.checkReview()
            else: self.warn('No PACR Created')
        else: self.warn('No Database')


    def addpStep(self):
        #Adds step to a pacr
        if self.pModel:
            if self.pModel.rowCount() > 0: self.pSteps.addRow()
            else: self.warn('No PACR Created')
        else: self.warn('No Database')


    def delpStep(self):
        #Deletes step from pacr
        if self.pModel:
            _row = self.pSteps.currentRow()
            logging.info(' Deleted Row: ' + str(_row))
            self.pSteps.delRow(_row)

        else: self.warn('No Database')


    def checkReview(self):
        #Checks whether there is a PACR waiting to be reviewed and sets the PACR review counter and color
        pActions = 0
        if self.pModel:
            for _row in range(self.pModel.rowCount()):
                if self.pModel.data(self.pModel.index(_row, 7), role = self.DR) == 'Review':
                    pActions += 1
        self.pActsNum.setText(str(pActions))
        if int(self.pActsNum.text()) > 0:
            self.pActsLabel.setStyleSheet('background-color: rgb(255, 255, 0); font: 75 8pt "MS Shell Dlg 2";')
        else:
            self.pActsLabel.setStyleSheet('')


    def fd(self, action):
        #Preforms necessary operations after FD approval or rejection
        _row = self.pTable.currentIndex().row()
        if self.pModel.submitAll(): 
            self.pModel.database().commit()
            self.pModel.select()
        if action == 'A':
            #If approved pushes the PACR into the script
            steps = self.pModel.data(self.pModel.index(_row, 6), role = self.DR).split(';')
            desc = self.pModel.data(self.pModel.index(_row, 5), role = self.DR)
            fdSig = str(os.getlogin() + ' ' + time.strftime("%x"))
            print(self.pModel.data(self.pModel.index(_row, 7), role = self.DR))

            self.pModel.setData(self.pModel.index(_row, 8), fdSig)
            self.pModel.setData(self.pModel.index(_row, 7), 'Approved')
            print(self.pModel.data(self.pModel.index(_row, 7), role = self.DR))
            print(self.pModel.rowCount())
            self.stateLabel.setText(str(self.pModel.data(self.pModel.index(_row, 7), role = self.DR)))
            self.pActsNum.setText(str(int(self.pActsNum.text()) - 1))
            self.fdLabel.setText(fdSig)

            logging.info(' Approved PACR: ' + str(_row + 1))
            self.cmdLabel.setText('Approved PACR: ' + str(_row + 1))

            self.rejectBut.setEnabled(False)
            self.acceptBut.setEnabled(False)
            self.saveP.setEnabled(False)
            self.pushP.setEnabled(False)
            if not self.pacr2step(_row, steps, desc): self.warn('Unknown')            

        if action == 'R':
            #If rejected pulls the PACR back to state 'Dev'
            self.saveP.setEnabled(True)
            self.pushP.setEnabled(True)
            self.pModel.setData(self.pModel.index(_row, 7), 'Dev', QtCore.Qt.EditRole)
            self.stateLabel.setText(str(self.pModel.data(self.pModel.index(_row, 7), role = self.DR)))

            logging.info(' Rejected PACR: ' + str(_row + 1))
            self.cmdLabel.setText('Rejected PACR: ' + str(_row + 1))

            self.rejectBut.setEnabled(False)
            self.acceptBut.setEnabled(False)

        self.checkReview()
        

    def pacr2step(self, pRow, steps, desc):
        #Preforms PACR operations on main script table
        pChange = self.pModel.data(self.pModel.index(pRow, 3), role = self.DR).upper()
        sRow = int(self.pModel.data(self.pModel.index(pRow, 2), role = self.DR)) - 1
        if self.sModel.editScript(pChange, sRow, steps, desc):
            logging.info(' ' + pChange + ' preformed with PACR ID: ' + str(pRow + 1))
            self.cmdLabel.setText(pChange + ' preformed with PACR ID: ' + str(pRow + 1))


            self.tableView.resizeColumnToContents(2)
            self.tableView.resizeColumnToContents(3)
            self.tableView.resizeRowsToContents()
            return True

        else: 
            self.warn('Unknown')
            return False



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())