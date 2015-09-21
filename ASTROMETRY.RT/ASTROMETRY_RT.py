#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from threading import Thread, RLock
import subprocess
import shlex
import websocket
import csv
import time
from PIL import Image
import libtiff
import numpy as np


class Communicator(QtCore.QThread):
    def __init__(self, parent = None):
        super(Communicator, self).__init__()
        self.exiting = False
        self.parent= parent

    def __del__(self):
        print "Communicator ukoncovani ..."
        self.exiting = True
        self.wait()

    def IsAstometryInstalled(self):
        try:
            process = subprocess.Popen(shlex.split("solve-field"), stdout=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
            return True
        except Exception, e:
            print "ASTROMETRY.NET isnt installed  ", e
            return False

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

    def showActualImage(self):
        actual = self.parent.actualFile

        tif = libtiff.TIFF.open(actual)
        image = tif.read_image()
        print image, image.shape, type(image)

        im = Image.fromarray(image)
        im.show()



class ASTROMETRY_RT(IPlugin):
    name = "ASTROMETRY real-time"
    def __init__(self):
        self.supportedExtensions = ['cr2', 'CR2', 'jpg', 'JPG', 'tiff', 'TIFF' ]
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

        self.thread = Communicator(self)
        self.thread.start()

        if not self.thread.IsAstometryInstalled():
            self.win = QtGui.QWidget()
            QtGui.QLabel("ASTROMETRY.NET isnt availible",self.win)
            return self.win
        else:
            self.win = QtGui.QWidget()
            self.contentWidget = QtGui.QWidget(self.win)
            self.content = QtGui.QHBoxLayout(self.contentWidget)

            self.AbouteGroup = QtGui.QGroupBox("ASTROMETRY setting")
            self.Aboute = QtGui.QVBoxLayout(self.win)
            self.AbouteProject = QtGui.QVBoxLayout(self.win)
            BtnOpenFolder = QtGui.QPushButton("Open working folder")
            self.Aboute.addWidget(BtnOpenFolder)
            self.Aboute.addLayout(self.AbouteProject)
            self.AbouteGroup.setLayout(self.Aboute)
        
            self.ProcessingGroup = QtGui.QGroupBox("Processing")
            self.ProcessingFrame = QtGui.QVBoxLayout(self.win)
            self.ProcessingToolBar = QtGui.QHBoxLayout(self.win)
            self.ProcessingShower = QtGui.QVBoxLayout(self.win)
            self.ProcessingInfoLine = QtGui.QHBoxLayout(self.win)
            self.ProcessingFrame.addLayout(self.ProcessingToolBar)
            self.ProcessingFrame.addLayout(self.ProcessingShower)
            self.ProcessingFrame.addLayout(self.ProcessingInfoLine)
            self.ProcessingGroup.setLayout(self.ProcessingFrame)
            
            self.content.addWidget(self.AbouteGroup,1)
            self.content.addWidget(self.ProcessingGroup,3)

            BtnOpenFolder.clicked.connect(self.ChooseWorkingDir)
            return self.win


    def  ChooseWorkingDir(self):
        FileDialog = QtGui.QFileDialog()
        FileDialog.setFileMode(2)
        self.VorkingDir = FileDialog.getExistingDirectory(self.win, 'Open file', '/home')
        print "WorkingDir: ", self.VorkingDir

        ChbAutoProcessing = QtGui.QCheckBox("Auto processing")
        self.FolderModel = QtGui.QFileSystemModel()
        self.FolderModel.setRootPath(self.VorkingDir)
        self.FolderTree =  QtGui.QTreeView()
        self.FolderTree.setModel(self.FolderModel)

        self.AbouteProject.addWidget(ChbAutoProcessing)
        self.AbouteProject.addWidget(self.FolderTree)
        self.FolderTree.clicked.connect(self.ClickedFile)


    def ClickedFile(self, qt = None):
        file = str(qt.model().filePath(qt))
        print file
        extension = str(file).split(".")[-1]
        print "extension: ", extension
        if extension in self.supportedExtensions:
            print "JE TO TAM"
            self.actualFile = file
            self.thread.showActualImage()


    def treefunction(self, index):
        print index.model().itemFromIndex(index).text()
