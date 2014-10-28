# -*- coding: utf-8 -*-
import sys
from cnDropUI import *
from PyQt4 import QtCore, QtGui

myappid = 'com.rasmusjones.campusnetdrop.1'

# for Windows Icon etc
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QtGui.QApplication(sys.argv)
mygui = StartQT4()
mygui.show()
app.setWindowIcon(QtGui.QIcon('LogoCampusNetDrop.png'))
mygui.setWindowIcon(QtGui.QIcon('LogoCampusNetDrop.png'))
sys.exit(app.exec_())