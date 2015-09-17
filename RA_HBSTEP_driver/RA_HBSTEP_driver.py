#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from threading import Thread, RLock


#l = RLock(False)

class RA_HBSTEP_driver(IPlugin):
    name = "MLAB RA driver"

    def __init__(self):
        self.type = 1   #loader
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

    def show(self, parent):
        self.parent = parent
        ## Win
        ## ScroolArea
        ## ContentWidget
        ## HorizontalLayout 
        ### GroupBox

        self.win = QtGui.QWidget()
        self.win.setMinimumHeight(900)
        self.win.setMinimumWidth(900)

        self.horizontalLayout = QtGui.QVBoxLayout()
        self.scrollArea = QtGui.QScrollArea(self.win)
        self.scrollArea.resize(900, 900)
        self.scrollArea.setWidgetResizable(True)
        self.contentWidget = QtGui.QWidget(self.win)
        #self.contentWidget.setGeometry(0,0,900, 900)
        self.content = QtGui.QHBoxLayout(self.contentWidget)
        self.scrollArea.setWidget(self.contentWidget)
        self.horizontalLayout.addWidget(self.scrollArea)

        AbouteGroup = QtGui.QGroupBox("RA HBSTEP")
        Aboute = QtGui.QVBoxLayout(self.win)

        LocalRA =  QtGui.QCheckBox("Remote driver", self.win)
        LocalRA.stateChanged.connect(self.ToggleLocal)

        BtnLoad = QtGui.QPushButton("Load")
        BtnLoad.clicked.connect(self.onConnect)

        Aboute.addWidget(LocalRA)
        Aboute.addWidget(BtnLoad)
        Aboute.addWidget(QtGui.QLabel("system",self.win))

        AbouteGroup.setLayout(Aboute)

        self.content.addWidget(AbouteGroup)


        return self.win

    def ToggleLocal(self, state):
        if state == QtCore.Qt.Checked:
            print "ANO"
            self.Local = True
        else:
            print "NE"
            self.Local = False

    def onConnect(self, state):
        self.PropertiesGroup = QtGui.QGroupBox("RA driver properties")
        PropertiesMainHFrame = QtGui.QVBoxLayout()
        if self.Local:
            VbxIP = QtGui.QHBoxLayout()
            VbxIP.addWidget(QtGui.QLabel("Remote adress:",self.win))
            TbxIP = QtGui.QLineEdit()
            VbxIP.addWidget(TbxIP)
            VbxPORT = QtGui.QHBoxLayout()
            VbxPORT.addWidget(QtGui.QLabel("Remote port:",self.win))
            NbxPORT = QtGui.QSpinBox()
            NbxPORT.setRange(0, 99999)
            VbxPORT.addWidget(NbxPORT)
            BtnRemConnect = QtGui.QPushButton("Conetct to RAmotor driver")
            BtnRemConnect.clicked.connect(self.RemConnect)
            PropertiesMainHFrame.addLayout(VbxIP)
            PropertiesMainHFrame.addLayout(VbxPORT)
            PropertiesMainHFrame.addWidget(BtnRemConnect)
            PropertiesMainHFrame.addStretch()
        else:
            PropertiesMainHFrame.addWidget(QtGui.QLabel("This operation isnt supported yet.",self.win))
            PropertiesMainHFrame.addWidget(QtGui.QLabel("Use remote driving",self.win))
            PropertiesMainHFrame.addWidget(QtGui.QLabel("Local driving will be supported as soos as possible :)",self.win))
            PropertiesMainHFrame.addStretch()

        self.PropertiesGroup.setLayout(PropertiesMainHFrame)
        self.content.addWidget(self.PropertiesGroup)

    def RemConnect(self, state):
        self.DriverGroup = QtGui.QGroupBox("Remote driver manager")
        PropertiesMainHFrame = QtGui.QVBoxLayout()
        if self.Local:
            VbxIP = QtGui.QHBoxLayout()
            VbxIP.addWidget(QtGui.QLabel("Remote adress:",self.win))
            TbxIP = QtGui.QLineEdit()
            VbxIP.addWidget(TbxIP)
            VbxPORT = QtGui.QHBoxLayout()
            VbxPORT.addWidget(QtGui.QLabel("Remote port:",self.win))
            NbxPORT = QtGui.QSpinBox()
            NbxPORT.setRange(0, 99999)
            VbxPORT.addWidget(NbxPORT)
            BtnRemConnect = QtGui.QPushButton("Conetct to RAmotor driver")
            BtnRemConnect.clicked.connect(self.RemConnect)
            PropertiesMainHFrame.addLayout(VbxIP)
            PropertiesMainHFrame.addLayout(VbxPORT)
            PropertiesMainHFrame.addWidget(BtnRemConnect)
            PropertiesMainHFrame.addStretch()
        else:
            PropertiesMainHFrame.addWidget(QtGui.QLabel("This operation isnt supported yet.",self.win))
            PropertiesMainHFrame.addWidget(QtGui.QLabel("Use remote driving",self.win))
            PropertiesMainHFrame.addWidget(QtGui.QLabel("Local driving will be supported as soos as possible :)",self.win))
            PropertiesMainHFrame.addStretch()

        self.DriverGroup.setLayout(PropertiesMainHFrame)
        self.content.addWidget(self.DriverGroup)
        

    
    
