#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui

class TT_loadrc2(IPlugin):
    name = "CANON loader"

    def __init__(self):
        self.type = 1   #loader
        self.extensions = ['jpg', 'JPG', 'jpeg', 'JPEG'] 
        self.UserName = "CANON loader"

    def getType(self):
        return self.type

    def getUserName(self):
        return self.UserName

    def getName(self):
        return self.UserName

    def getFilesExtension(self):
        return self.extensions

    def activate(self):
        pass

    def deactivate(self):
        print "Ive been deactivated!"

    def load(self):
        print "loader"

    def show(self):
        w = QtGui.QWidget()
        w.resize(250, 150)
        w.move(300, 300)
        
        return w