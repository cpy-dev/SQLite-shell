#!/usr/bin/python3

import sqlite3
import terminalpy
from PyQt5.Qt import *
from PyQt5.QtWidgets import QMessageBox

__version__ = '2.0.0'

class App(QWidget):
    def __init__(self):
        super(App, self).__init__()

        self.db = None
        self.cmd = None

        self.lastOpenedDb = None
        self.t = terminalpy.Terminal(True)

        self.checkFilesExistence()
        self.makeInterface()

    def checkFilesExistence(self):
        homePath = self.t.type('echo $HOME')

        try: self.t.type(f'cd {homePath}/.sqliteshell')
        except: self.t.type(f'mkdir {homePath}/.sqliteshell/')

        try: self.t.type(f'cd {homePath}/.sqliteshell/cache')
        except: self.t.type(f'mkdir {homePath}/.sqliteshell/cache')

        try: self.t.type(f'cd {homePath}/.sqliteshell/log')
        except: self.t.type(f'mkdir {homePath}/.sqliteshell/log')

        self.t.type(f'touch {homePath}/.sqliteshell/log/sqliteshell.log')
        self.t.type(f'touch {homePath}/.sqliteshell/cache/sqliteshell.cache')

    def getLastOpenedDb(self):
        homePath = self.t.type('echo $HOME')

        with open(f'{homePath}/.sqliteshell/cache/sqliteshell.cache', 'r') as cache:
            self.lastOpenedDb = cache.read()

        print('"', self.lastOpenedDb, '"')

        if self.lastOpenedDb[-1] == ' ':
            self.lastOpenedDb = self.lastOpenedDb[0:-1]

        self.filePath.setText(self.lastOpenedDb)
        self.loadDataBase()

    def saveLastOpenDb(self):
        homePath = self.t.type('echo $HOME')

        with open(f'{homePath}/.sqliteshell/cache/sqliteshell.cache', 'w') as cache:
            cache.write(self.filePath.text())

    def log(self):
        homePath = self.t.type('echo $HOME')

        with open(f'{homePath}/.sqliteshell/log/sqliteshell.log', 'a') as log:
            log.write(self.textZone.toPlainText() + '\n')

    def makeInterface(self):
        self.setStyleSheet('background-color: #1F2633; color: white;')
        self.resize(1000, 700)
        self.setWindowTitle('SQLite-Shell')

        layout = QGridLayout()
        topLayout = QHBoxLayout()

        self.filePath = QLineEdit()
        self.filePath.setPlaceholderText('File Path')
        self.filePath.setStyleSheet('padding: 5px; margin: 5px;')
        topLayout.addWidget(self.filePath, 2)

        self.getLastOpenedDb()

        self.loadDb = QPushButton('Load')
        self.loadDb.clicked.connect(self.loadDataBase)
        self.loadDb.setStyleSheet('padding: 5px; margin: 5px; margin-left: 10px')
        topLayout.addWidget(self.loadDb, 1)

        layout.addLayout(topLayout, 0, 0, 1, 2)

        self.textZone = QPlainTextEdit(self)
        self.textZone.setPlaceholderText('Command(s) to execute')
        layout.addWidget(self.textZone, 1, 0)

        self.table = QTableWidget(self)
        layout.addWidget(self.table, 1, 1)

        self.run = QPushButton('Run Script', self)
        self.run.move(20, 650)
        self.run.clicked.connect(self.render)
        layout.addWidget(self.run, 2, 0, 1, 2)

        self.setLayout(layout)

    def loadDataBase(self):
        self.db = sqlite3.connect(self.filePath.text())
        self.saveLastOpenDb()

    def scriptAnalysis(self):
        self.cmd = self.textZone.toPlainText()
        cmd = self.textZone.toPlainText()
        cmds = []

        if ';' in cmd:
            while ';' in cmd:
                semiColonIndex = cmd.index(';')

                cmds.append(cmd[0:semiColonIndex])
                cmd = cmd[semiColonIndex+1:len(cmd)]
        cmds.append(cmd)

        return cmds

    def makeErrorPopup(self, text):
        popup = QMessageBox()
        popup.setWindowTitle('Error Message')
        popup.setText('Execution error: ' + text)
        #popup.setText('Execution error: how may have made a syntax error or you may have not loaded properly you database file. Check your script and retry')
        popup.exec_()

    def render(self):
        commands = self.scriptAnalysis()
        self.table.clear()
        if len(commands) == 1:
            try:
                data = self.db.execute(commands[0])
            except sqlite3.OperationalError as e:
                self.makeErrorPopup(str(e))
            except AttributeError:
                self.makeErrorPopup('you must load database properly. Enter full filepath and press "Load"')
            else:
                self.log()
                data = data.fetchall()
                if len(data) != 0:
                    self.db.commit()
                    # gets size of aouput data
                    rows = len(data)
                    cols = len(data[0])

                    # set table dimensions
                    self.table.setColumnCount(cols)
                    self.table.setRowCount(rows)

                    # setter for column names in table
                    columnNames = self.columnsAnalysis(commands[0])
                    k = 0

                    for columnName in columnNames:
                        self.table.setHorizontalHeaderItem(k, QTableWidgetItem(columnName))
                        k += 1

                    # elements extraction from command result
                    dataList = []
                    for row in data:
                        subList = []

                        for element in row:
                            subList.append(str(element))
                        dataList.append(subList)

                    # render on the table of the elements
                    for i in range(len(dataList)): # each row
                        for j in range(len(dataList[0])): # each column
                            self.table.setItem(i, j, QTableWidgetItem(dataList[i][j]))
                else:
                    self.table.setRowCount(0)
                    self.table.setColumnCount(0)
                    self.table.clear()
        else:
            results = [] # array of result for multi comand script

            for command in commands:
                try:
                    result = self.db.execute(command)
                except sqlite3.OperationalError as e:
                    self.makeErrorPopup(str(e))
                except AttributeError:
                    self.makeErrorPopup('you must load database properly. Enter full filepath and press "Load"')
                else:
                    self.log()
                    results.append(result.fetchall())
                    self.db.commit()
            maxColLength = 0
            rowLength = 0

            # setter for table dimensions
            for result in results:
                rowLength += len(result)+2
                colLength = len(result[0])
                if colLength > maxColLength:
                    maxColLength = colLength

            self.table.setRowCount(rowLength)
            self.table.setColumnCount(maxColLength)

            commandIndex = 0
            row = 0

            for result in results:
                if len(result) != 0:
                    # setter for column names in table
                    columnNames = self.columnsAnalysis(commands[commandIndex])
                    k = 0

                    for columnName in columnNames:
                        self.table.setItem(row, k, QTableWidgetItem(columnName))
                        k += 1
                    row += 1

                    dataList = []
                    for resultRow in result:
                        subList = []

                        for element in resultRow:
                            subList.append(str(element))
                        dataList.append(subList)

                    for i in range(len(dataList)):
                        for j in range(len(dataList[0])):
                            self.table.setItem(row, j, QTableWidgetItem(dataList[i][j]))
                        row += 1

                    for j in range(maxColLength):
                        self.table.setItem(row, j, QTableWidgetItem('---'))

                    row += 1

                    commandIndex += 1
                else:
                    self.table.setRowCount(0)
                    self.table.setColumnCount(0)
                    self.table.clear()

    def getTableName(self, cmd):
        command = cmd.lower()
        index = command.index('from')
        index += 5
        while command[index] == ' ':
            index += 1

        tableName = ''
        while index != len(command) and command[index] != ' ' and command[index] != ';':
            tableName += command[index]
            index += 1

        return tableName

    def columnsAnalysis(self, command):
        selectIndex = command.index('select')
        fromIndex = command.index('from')
        selectIndex += 6

        columns = command[selectIndex:fromIndex]
        colNames = []

        if columns.replace(' ', '') == '*':
            tableName = self.getTableName(command)

            dataCols = self.db.execute("pragma table_info(" + tableName + ")")
            dataCols = dataCols.fetchall()

            for column in dataCols:
                colNames.append(column[1])
        else:
            columnsList = columns.split(', ')

            for column in columnsList:
                if ' as ' in column:
                    nameIndex = column.index(' as ')
                    nameIndex += 4

                    name = column[nameIndex:len(column)]
                    name = name.replace(' ', '')

                    colNames.append(name)
                else:
                    columnName = column.replace(' ', '')
                    if columnName == '*':
                        tableName = self.getTableName(command)

                        dataCols = self.db.execute("pragma table_info(" + tableName + ")")
                        dataCols = dataCols.fetchall()

                        for column in dataCols:
                            colNames.append(column[1])
                    else:
                        colNames.append(columnName)
        return colNames

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    application = App()
    application.show()
    app.exec()
