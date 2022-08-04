import sqlite3
from PyQt5.Qt import *
from PyQt5.QtGui import *

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.db = None
        self.cmd = None

        self.makeInterface()

    def makeInterface(self):
        self.setStyleSheet('background-color: #1F2633; color: white;')
        self.setFixedSize(1000, 700)

        self.filePath = QLineEdit(self)
        self.filePath.setPlaceholderText('DataBase File Path')
        self.filePath.setFixedWidth(500)
        self.filePath.move(175, 20)

        self.loadDb = QPushButton('Load', self)
        self.loadDb.clicked.connect(self.loadDataBase)
        self.loadDb.move(725, 20)

        self.textZone = QPlainTextEdit(self)
        self.textZone.setPlaceholderText('Command to execute')
        self.textZone.setFixedSize(470, 560)
        self.textZone.move(20, 70)

        self.run = QPushButton('Run Script', self)
        self.run.setFixedWidth(470)
        self.run.move(20, 650)
        self.run.clicked.connect(self.execute)

        self.table = QTableWidget(self)
        self.table.setFixedSize(470, 610)
        self.table.move(510, 70)

    def loadDataBase(self):
        self.db = sqlite3.connect(self.filePath.text())

    def execute(self):
        self.cmd = self.textZone.toPlainText()

        try:
            data = self.db.execute(self.textZone.toPlainText())
        except:
            pass
        else:
            data = data.fetchall()
            self.render(data)

    def render(self, data):
        rows = len(data)
        cols = len(data[0])

        self.table.setColumnCount(cols)
        self.table.setRowCount(rows)

        tableName = self.getTableName()

        dataCols = self.db.execute("pragma table_info(" + tableName + ")")
        dataCols = dataCols.fetchall()

        k = 0

        for column in dataCols:
            self.table.setHorizontalHeaderItem(k, QTableWidgetItem(column[1]))
            k += 1

        dataList = []

        for row in data:
            subList = []

            for element in row:
                subList.append(str(element))
            dataList.append(subList)

        for i in range(len(dataList)):
            for j in range(len(dataList[0])):
                self.table.setItem(i, j, QTableWidgetItem(dataList[i][j]))

    def getTableName(self):
        cmd = self.cmd.lower()
        index = cmd.index('from')
        index += 5
        while cmd[index] == ' ':
            index += 1

        tableName = ''
        while index != len(cmd) and cmd[index] != ' ' and cmd[index] != ';':
            tableName += cmd[index]
            index += 1

        return tableName

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    application = App()
    application.show()
    app.exec()
