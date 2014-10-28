# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from cnDrop import *
import threading

class StartQT4(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.resize(640,400)
        self.move(200,200)
        self.setWindowTitle('CampusNetDrop')

        ## LOGIC HANDLER
        self.cnDrop = CampusNetDrop()

        ## LOG
        logTable = LogTable()

        ## TABS
        tabs = TabBar(self.cnDrop)

        self.cnDrop.setLogTable(logTable)
        self.cnDrop.setDlTab(tabs.downloadTab)
        self.cnDrop.initDlTab()

        ## LAYOUT
        boxLayout = QtGui.QVBoxLayout()
        boxLayout.addWidget(tabs)
        boxLayout.addWidget(logTable)
        self.setLayout(boxLayout)

class TabBar(QtGui.QTabWidget):
    def __init__(self, cnDropHandler, parent=None):
        self.cnDrop = cnDropHandler
        QtGui.QTabWidget.__init__(self, parent)
        self.resize(500,250)
        self.downloadTab = DownloadTab(self.cnDrop)   
        self.configurationTab = ConfigurationTab(self.cnDrop)
        self.addTab(self.downloadTab,"Download")
        self.addTab(self.configurationTab,"Configure login")

class DownloadTab(QtGui.QWidget):
    def __init__(self, cnDropHandler, parent=None):
        self.cnDrop = cnDropHandler
        QtGui.QWidget.__init__(self, parent)
        vBox = QtGui.QVBoxLayout()
        hBox = QtGui.QHBoxLayout()

        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Course name","Add student folder","Download path", "ElementID"])

        button1 = QtGui.QPushButton("Download contents")
        button1.clicked.connect(self.downloadCourseContents)
        button2 = QtGui.QPushButton("Configure downloads")
        button2.clicked.connect(self.getCourses)
        
        hBox.addWidget(button1)
        hBox.addStretch(1)
        hBox.addWidget(button2)

        vBox.addWidget(self.tree)
        vBox.addLayout(hBox)
        self.setLayout(vBox)

        # Event
        self.tree.itemDoubleClicked.connect(self.onDoubleClickItem)

    def downloadCourseContents(self):
        t = threading.Thread(target=self.cnDrop.downloadCourseContents)
        t.start()

    def getCourses(self):
        t = threading.Thread(target=self.cnDrop.getCourses)
        t.start()
        
        
    def onDoubleClickItem(self, item, column):
        if column==2:
            folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
            if folder:
                item.setText(2,str(folder))

    def clear(self):
        self.tree.clear()

    def writeCourse(self, coursename,elementID,dlCourse=False,studentfolder=False,path=""):
        item = QtGui.QTreeWidgetItem()
        item.setText(0,str(coursename))
        item.setText(3,str(elementID))
        item.setText(1,"Add student folder to download")
        if str(path)=="":
            item.setText(2,"DOUBLE CLICK HERE TO SET PATH")
        else:
            item.setText(2,str(path))
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        if dlCourse:
            item.setCheckState(0,QtCore.Qt.Checked)
        else:
            item.setCheckState(0,QtCore.Qt.Unchecked)
        if studentfolder:
            item.setCheckState(1,QtCore.Qt.Checked)
        else:
            item.setCheckState(1,QtCore.Qt.Unchecked)
        self.tree.addTopLevelItem(item)

class ConfigurationTab(QtGui.QWidget):
    def __init__(self, cnDropHandler, parent=None):
        self.cnDrop = cnDropHandler
        QtGui.QWidget.__init__(self, parent)
        vBox = QtGui.QVBoxLayout()
        hBox1= QtGui.QHBoxLayout()
        hBox2= QtGui.QHBoxLayout()
        hBox3= QtGui.QHBoxLayout()

        header = QtGui.QLabel("Login:")
        label1 = QtGui.QLabel("DTU Login:")
        label2 = QtGui.QLabel("Password:")
        textedit1 = QtGui.QLineEdit("sXXXXXX")
        textedit2 = QtGui.QLineEdit("")
        textedit2.setEchoMode(QtGui.QLineEdit.Password)
        button = QtGui.QPushButton("Save login")
        button.clicked.connect(lambda: self.cnDrop.login(str(textedit1.text()), str(textedit2.text())))

        hBox1.addWidget(label1)
        hBox1.addWidget(textedit1)
        hBox2.addWidget(label2)
        hBox2.addWidget(textedit2)
        hBox3.addStretch(1)
        hBox3.addWidget(button)

        vBox.addWidget(header)
        vBox.addLayout(hBox1)
        vBox.addLayout(hBox2)
        vBox.addLayout(hBox3)

        vBox.addStretch(1)

        self.setLayout(vBox)

class LogTable(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Log Class","Message"])
        # items=[]
        # for i in range(1,100):
        #     items.append(QtGui.QTreeWidgetItem(["LogClass","Message"+str(i)]))
        # self.addTopLevelItems(items)
        # self.scrollToItem(items[-1],QtGui.QAbstractItemView.PositionAtBottom)

    def writeLog(self,logId, *argv):
        if len(argv)==0:
            argv = [""]
        # 1XX: Info
        # 2XX: Error
        # 3XX: Download
        logId = str(logId)
        logs = { '199': "by Rasmus Jones - rasmusjones.com",
                 '100': "Trying to login user %s." % (argv[0]),
                 '101': "Login successful. User saved.",
                 '102': "You DO NOT have to login again after a restart.",
                 '103': "Fetching course names.",
                 '104': "Courses displayed in the table.",
                 '105': "Tick the first box to add course to the download list.",
                 '106': "Tick the second box to add the student folder to the download list.",
                 '107': "Double click the 'Download path' column in order to set the download path for that course.",
                 '108': "Creating folder %s." % (argv[0]),
                 '109': "Latest version already downloaded. %s" % (argv[0]),
                 '110': "Downloading file %s" % (argv[0]),
                 '111': "Finished %s." % (argv[0]),
                 '112': "Starting %s." % (argv[0]),
                 '200': "No connection to the internet.",
                 '201': "Wrong login.",
                 '202': "Login not configured. Go to the 'Configure login' tab.",
                 '203': "Please tick some courses.",
                 '204': "Please set a 'Download path' for all ticked courses.",
                 '205': "Please click 'Configure downloads'."}
        logClass = ["INFO", "ERROR"]

        item = QtGui.QTreeWidgetItem([logClass[int(logId[0])-1],logs[logId]])
        self.addTopLevelItem(item)
        self.scrollToItem(item,QtGui.QAbstractItemView.PositionAtBottom)



