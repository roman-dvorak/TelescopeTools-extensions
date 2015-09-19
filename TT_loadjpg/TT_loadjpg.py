#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui

class TT_loadjpg(IPlugin):
    name = "JPG loader"
    

    def __init__(self):
        self.type = 1   #loader
        self.extensions = ['cr2', 'CR2'] 
        self.UserName = "JPG loader"

    def getType(self):
        return self.type

    def getUserName(self):
        return self.UserName

    def getName(self):
        return self.UserName

    def getFilesExtension(self):
        return self.extensions

    def activate(self):
        print "activated"

    def deactivate(self):
        print "Ive been deactivated!"

    def load(self):
        print "loader"

    def show(self, parent):
        self.parent = parent
        ## Win
        ## ScroolArea
        ## ContentWidget
        ## HorizontalLayout 

        self.win = QtGui.QWidget()

        self.horizontalLayout = QtGui.QVBoxLayout(self.win)
        self.horizontalLayout.setGeometry(0,0,900, 900)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.contentWidet = QtGui.QWidget()
        self.contentWidet.setGeometry(0,0,900, 900)
        self.content = QtGui.QHBoxLayout(self.contentWidet)
        self.scrollArea.setWidget(self.contentWidet)
        self.horizontalLayout.addWidget(self.scrollArea)

        AbouteGroup = QtGui.QGroupBox("Aboute system")
        Aboute = QtGui.QVBoxLayout(self.win)
        Aboute.addWidget(QtGui.QLabel("system",self.win))
        AbouteGroup.setLayout(Aboute)

        self.content.addWidget(AbouteGroup)
        self.content.addStretch()

        return self.win
    
