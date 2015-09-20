#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from threading import Thread, RLock
import subprocess
import shlex
import websocket
import csv
import time


class Communicator(QtCore.QThread):
    def __init__(self, parent = None):
        super(Communicator, self).__init__()
        self.parent= parent

    def __del__(self):
        print "Communicator ukoncovani ..."
        self.exiting = True
        self.wait()

    def IsAstometryInstalled(self):
        status = False
        try:
            process = subprocess.Popen(shlex.split("solve-field"), stdout=None)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
            status = True
        except Exception, e:
            print "ASTROMETRY.NET isnt installed"
        return status

    def run(self):
        while not self.exiting:
            time.sleep(1)
        print "Communicator ukoncen"

    def IsAstometryInstalledaaa(self, command):
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                #self.logger.info(output.strip())
                print output.strip()
        status = process.poll()
        return status

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

        thread = Communicator(self)
        thread.start()

        try:
            thread.IsAstometryInstalled()
        except Exception, e:
            raise e

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

