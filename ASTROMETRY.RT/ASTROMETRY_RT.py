#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from threading import Thread, RLock
import websocket
import csv
import time


class Communicator(QtCore.QThread):

    def __init__(self, parent = None, win = None):
        super(Communicator, self).__init__()
        self.parent= parent
        


    def __del__(self):
        print "Communicator ukoncovani ..."
        self.exiting = True
        self.wait()

        self.updateUI()


    def run(self):
        while not self.exiting:
            time.sleep(1)
        print "Communicator ukoncen"


class ASTROMETRY_RT(IPlugin):
    name = "ASTROMETRY real-time"

    def __init__(self):
        self.type = 3
        self.UserName = "MLAB RA driver"
        self.Local = False

    def getType(self):
        return self.type

    def getUserName(self):
        return self.UserName

    def getName(self):
        return self.UserName

    def activate(self):
        print "activated"

    def deactivate(self):
        print "Ive been deactivated!"

    def load(self):
        print "loader"

    def OnSync(self, data = None):
        print "local sync"
        self.thread.sync()

    def show(self, parent):
        self.parent = parent
        ## Win
        ## ScroolArea
        ## ContentWidget
        ## HorizontalLayout 
        ### GroupBox

        self.win = QtGui.QWidget()

        self.horizontalLayout = QtGui.QVBoxLayout()
        self.scrollArea = QtGui.QScrollArea(self.win)
        self.scrollArea.resize(900, 900)
        self.scrollArea.setWidgetResizable(True)
        self.contentWidget = QtGui.QWidget(self.win)
        self.content = QtGui.QHBoxLayout(self.contentWidget)
        self.scrollArea.setWidget(self.contentWidget)
        self.horizontalLayout.addWidget(self.scrollArea, QtCore.Qt.AlignCenter)

        AbouteGroup = QtGui.QGroupBox("ASTROMETRY init")
        Aboute = QtGui.QVBoxLayout(self.win)
        BtnLoad = QtGui.QPushButton("Load")
        Aboute.addWidget(BtnLoad)
        Aboute.addWidget(QtGui.QLabel("system",self.win))
        AbouteGroup.setLayout(Aboute)

        self.content.addWidget(AbouteGroup)


        return self.win

