#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from PyQt4.QtOpenGL import *
from OpenGL.GL import *
from threading import Thread, RLock
import subprocess
import shlex
import websocket
import csv
import time
from PIL import Image
import libtiff
import pyfits
import numpy as np


class GLWidget(QGLWidget):
    def __init__(self, parent = None):
        super(WfWidget, self).__init__(parent)

    def paintGL(self):
        glColor3f(0.0, 0.0, 1.0)
        glRectf(-5, -5, 5, 5)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(20, 20, 0)
        glEnd()

    def resizeGL(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-50, 50, -50, 50, -50.0, 50.0)
        glViewport(0, 0, w, h)

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)


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
        #image = tif.read_image()
        image = np.swapaxes(tif.read_image(), 0, 0)

        hdu = pyfits.PrimaryHDU(image)
        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto('new.fits')

        print image, image.shape, type(image), np.swapaxes(image,2,0).shape
       
        hdu0 = pyfits.PrimaryHDU(image[:,:,0])
        hdu1 = pyfits.PrimaryHDU(image[:,:,1])
        hdu2 = pyfits.PrimaryHDU(image[:,:,2])

        data = image[:,:,0] + image[:,:,1] + image[:,:,2]
        dataH = pyfits.PrimaryHDU(data)
        hdulist = pyfits.HDUList([dataH])
        hdulist.writeto('new.fits')


        #ima = Image.fromarray(np.swapaxes(image,2,0))
        #imb = Image.fromarray(image[1], 'RGB')
        #imc = Image.fromarray(image[2], 'RGB')

        #ima.save("ahoj.png")
        #imb.show()
        #imc.show()



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
            #self.content = QtGui.QHBoxLayout(self.contentWidget)
            self.content = QtGui.QSplitter(QtCore.Qt.Horizontal)
            #self.Aboute = QtGui.QVBoxLayout()

            ChbCollapseLeftPanel = QtGui.QCheckBox()
            ChbCollapseLeftPanel.setObjectName("ChbCollapse")
            self.VbxProjectToolBox = QtGui.QVBoxLayout()
            '''
            self.ProjectToolBox = QtGui.QToolBox()
            #self.Aboute.addWidget(self.ProjectToolBox)
            
            self.FoldelTBitem = QtGui.QVBoxLayout()
            BtnOpenFolder = QtGui.QPushButton("Open working folder")
            self.FoldelTBitem.addWidget(BtnOpenFolder)
            FoldelTBitemWid = QtGui.QWidget()
            FoldelTBitemWid.setLayout(self.FoldelTBitem)
            self.ProjectToolBox.addItem(FoldelTBitemWid, QtCore.QString("Project Folder"))
            '''
            #self.AbouteGroup = QtGui.QGroupBox("ASTROMETRY setting")
            #self.Aboute = QtGui.QVBoxLayout(self.win)
            #self.AbouteProject = QtGui.QVBoxLayout(self.win)
            #BtnOpenFolder = QtGui.QPushButton("Open working folder")
            #self.Aboute.addWidget(BtnOpenFolder)
            #self.Aboute.addLayout(self.AbouteProject)
            #self.AbouteGroup.setLayout(self.Aboute)
            #self.Aboute = QtGui.QVBoxLayout()
            #self.AbouteGroup.setLayout(self.Aboute)
            '''
            self.ProcessingGroup = QtGui.QGroupBox("Processing")
            self.ProcessingFrame = QtGui.QVBoxLayout(self.win)
            self.ProcessingToolBar = QtGui.QHBoxLayout(self.win)
            self.ProcessingShower = QtGui.QVBoxLayout(self.win)
            self.ProcessingInfoLine = QtGui.QHBoxLayout(self.win)
            #self.ProcessingView = QGLWidget()
            #self.ProcessingShower.addWidget(self.ProcessingView)
            self.ProcessingFrame.addLayout(self.ProcessingToolBar)
            self.ProcessingFrame.addLayout(self.ProcessingShower)
            self.ProcessingFrame.addLayout(self.ProcessingInfoLine)
            self.ProcessingGroup.setLayout(self.ProcessingFrame)
            '''

            self.FrameProjectToolBox = QtGui.QFrame()
            self.FrameProjectToolBox.setFrameShape(QtGui.QFrame.StyledPanel)

            self.LeftPanel()
            self.content.addWidget(ChbCollapseLeftPanel)
            self.content.addWidget(self.FrameProjectToolBox)
            #self.content.addStretch(12)
            #self.content.addWidget(self.ProcessingGroup,12)
            self.contentWidget.setLayout(self.content)

            #BtnOpenFolder.clicked.connect(self.ChooseWorkingDir)
            ChbCollapseLeftPanel.stateChanged.connect(self.CollapseLP)
            return self.win

    def LeftPanel(self):
        parent = self.VbxProjectToolBox
        DockProjectFolder = QtGui.QDockWidget("Data source folder")
        DockProjectFolder.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetVerticalTitleBar)
        DockProjectFolder.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        DockAstrometrySetting = QtGui.QDockWidget("Astrometry setting")
        DockAstrometrySetting.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetVerticalTitleBar)
        DockAstrometryOut = QtGui.QDockWidget("Astrometry output data")
        DockAstrometryOut.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetVerticalTitleBar)

        WidgetProjectFolder = QtGui.QWidget()
        self.LayoutProjectFolder = QtGui.QVBoxLayout()

        BtnOpenFolder = QtGui.QPushButton("Open working folder")
        self.LayoutProjectFolder.addWidget(BtnOpenFolder)
        WidgetProjectFolder.setLayout(self.LayoutProjectFolder)
        DockProjectFolder.setWidget(WidgetProjectFolder)

        parent.addWidget(DockProjectFolder)
        parent.addWidget(DockAstrometrySetting)
        parent.addWidget(DockAstrometryOut)
        BtnOpenFolder.clicked.connect(self.ChooseWorkingDir)
        #parent.addWidget(DockAstrometrySetting)

    def CollapseLP(self, state):
        if state == QtCore.Qt.Checked:
            print "ANO"
            self.Local = True
        else:
            print "NE"
            self.Local = False


    def AstrometryMainTools(self):
        self.FolderAstrometryMainToolsItem = QtGui.QVBoxLayout()
        FolderAstrometryMainToolsItemWid = QtGui.QWidget()
        FolderAstrometryMainToolsItemWid.setLayout(self.FolderAstrometryMainToolsItem)
        self.ProjectToolBox.addItem(FolderAstrometryMainToolsItemWid, QtCore.QString("Astrometry Tools"))


    def ChooseWorkingDir(self):
        FileDialog = QtGui.QFileDialog()
        FileDialog.setFileMode(2)
        self.VorkingDir = FileDialog.getExistingDirectory(self.win, 'Open file', '/home')
        print "WorkingDir: ", self.VorkingDir

        self.FolderModel = QtGui.QFileSystemModel()
        self.FolderModel.setRootPath(self.VorkingDir)
        self.FolderTree =  QtGui.QTreeView()
        self.FolderTree.setModel(self.FolderModel)
        self.FolderTree.setRootIndex(self.FolderModel.index(self.VorkingDir) )
        self.FolderTree.setColumnWidth(0, 800)

        self.LayoutProjectFolder.addWidget(self.FolderTree)
        #self.LayoutProjectFolder.addStretch(1)
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
