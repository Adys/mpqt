#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from PySide.QtCore import *
from PySide.QtGui import *

from storm import MPQ


class MPQt(QApplication):
	def __init__(self, argv):
		QApplication.__init__(self, argv)
		self.mainWindow = MainWindow()
		self.mainWindow.setWindowTitle("MPQt")
		self.mainWindow.statusBar().showMessage("Ready")
		
		arguments = OptionParser()
		
		_, files = arguments.parse_args(argv[1:])
		
		for name in files:
			self.open(name)
		
		self.open("/home/adys/wow/Data/art.MPQ")
	
	def open(self, name):
		mpq = MPQ(name)
		self.mainWindow.model.setFile(mpq)
		self.mainWindow.setWindowTitle("%s - MPQt" % (name))

class MainWindow(QMainWindow):
	def __init__(self, *args):
		QMainWindow.__init__(self, *args)
		
		self.__addMenus()
		
		self.__addToolbar()
		
		self.model = MPQArchiveTreeModel()
		
		#view = QListView()
		view = QTreeView()
		
		view.setModel(self.model)
		view.setSortingEnabled(True)
		self.setCentralWidget(view)
		
		#self.statusBar().showMessage("Ready") # perf leak!
	
	def __addMenus(self):
		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction("&New", self.actionNew, "Ctrl+N")
		fileMenu.addAction("&Open...", self.actionOpen, "Ctrl+O")
		fileMenu.addAction("Open &Recent")
		fileMenu.addSeparator()
		fileMenu.addAction("&Quit", self, SLOT("close()"), "Ctrl+Q")
		
		fileMenu = self.menuBar().addMenu("&Help")
		fileMenu.addAction("About", lambda: None)
	
	def __addToolbar(self):
		toolbar = self.addToolBar("Toolbar")
		toolbar.addAction("New")
		toolbar.addAction("Open")
		fileMask = QLineEdit()
		fileMask.setPlaceholderText("File mask")
		toolbar.addWidget(fileMask)
	
	def actionNew(self):
		print "actionNew()"
	
	def actionOpen(self):
		print "actionOpen()"


def hsize(i):
	"Human-readable file size"
	for x in ("%i", "%3.1f K", "%3.1f M", "%3.1f G", "%3.1f T"):
		if i < 1024.0:
			return x % (i)
		i /= 1024.0


class MPQArchiveListModel(QAbstractListModel):
	def __init__(self, *args):
		QAbstractListModel.__init__(self, *args)
		self.rows = []
	
	def data(self, index, role):
		return "test"
		print index.row()
		file = self.rows[index.row()]
		return file.plainpath
	
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return "Name"
		
		return QAbstractItemModel.headerData(self, section, orientation, role)
	
	def rowCount(self, parent):
		if parent.isValid():
			return 0
	
	def setFile(self, file):
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		lf = file.list()
		for i in range(10):
			self.rows.append(lf.next())
		self.emit(SIGNAL("layoutChanged()"))


COLUMN_NAME = 0
COLUMN_SIZE = 1

class MPQArchiveTreeModel(QAbstractItemModel):
	_COLS = ("Name", "Size")
	
	def __init__(self, *args):
		QAbstractItemModel.__init__(self, *args)
		self.rows = []
	
	def columnCount(self, parent):
		return len(self._COLS)
	
	def data(self, index, role):
		if not index.isValid() or role != Qt.DisplayRole:
			return
		
		file = self.rows[index.row()]
		
		column = index.column()
		if column == COLUMN_NAME:
			#return file.filename
			return file.plainpath
		
		if column == COLUMN_SIZE:
			return hsize(file.filesize)
		
		return -1
	
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._COLS[section]
		return QAbstractItemModel.headerData(self, section, orientation, role)
	
	def index(self, row, column, parent):
		return self.createIndex(row, column)
	
	def parent(self, index):
		return QModelIndex() # crash!
	
	def rowCount(self, parent):
		return len(self.rows)
	
	def setFile(self, file):
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		self.rows = list(file.list())[:50]
		self.emit(SIGNAL("layoutChanged()"))



def main():
	import signal
	import sys
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = MPQt(sys.argv)
	
	app.mainWindow.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
