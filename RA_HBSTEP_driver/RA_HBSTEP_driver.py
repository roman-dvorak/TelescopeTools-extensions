#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from threading import Thread, RLock
import websocket
import csv


#l = RLock(False)

class Communicator(QtCore.QThread):

    def __init__(self, parent = None, win = None):
        self.parent= parent
        print "Communicator nastaven"

        adress = "ws://"+str(self.parent.TbxIP.text())+":"+str(self.parent.NbxPORT.value())+"/ws"

        print "Adresa:", adress
        self.ws = websocket.create_connection(adress)
        self.ws.send("Hello, World")
        result = self.ws.recv()
        print("Received {}".format(result))

        self.vTimeSpd = 0
        self.vDir = True

        self.vSHTtemp = 88.88
        self.vSHThumi = 88.88
        self.vLTStemp = 88.88

        self.ws.send("$raspd;%d;%d;" %(self.vDir, self.vTimeSpd))
        result = self.ws.recv()
        print("Received {}".format(result))



    def __del__(self):
        print "Communicator ukoncovani ..."
        self.exiting = True
        self.wait()


    def sync(self):
        self.getWeather()
        self.updateUI()


    def getWeather(self):
        self.ws.send("$sht25;")
        result = self.ws.recv()
        if result.split(';')[0] == "&sht25":
            self.vSHTtemp = float(result.split(';')[1])
            self.vSHThumi = float(result.split(';')[2])

        self.ws.send("$lts;")
        result = self.ws.recv()
        if result.split(';')[0] == "&lts":
            self.vLTStemp = float(result.split(';')[1])


    def updateUI(self):
        self.parent.LcnSHTtemp.display(self.vSHTtemp)
        self.parent.LcnSHTHumi.display(self.vSHThumi)
        self.parent.LcnLTStemp.display(self.vLTStemp)

        self.parent.LcnRAspeed1.display((self.vTimeSpd >> 16)&0xff)
        self.parent.LcnRAspeed2.display((self.vTimeSpd >> 8)&0xff)
        self.parent.LcnRAspeed3.display((self.vTimeSpd >> 0)&0xff)


    def change(self, widget):
        print "change,", self, widget
        self.vTimeSpd = self.parent.NbxSpdTime.value()

        self.updateUI()


    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        while not self.exiting:
            pass
        print "Communicator ukoncen"

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
            self.TbxIP = QtGui.QLineEdit("192.168.1.184")
            VbxIP.addWidget(self.TbxIP)
            VbxPORT = QtGui.QHBoxLayout()
            VbxPORT.addWidget(QtGui.QLabel("Remote port:",self.win))
            self.NbxPORT = QtGui.QSpinBox()
            self.NbxPORT.setRange(0, 99999)
            self.NbxPORT.setValue(10345)
            VbxPORT.addWidget(self.NbxPORT)
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
        self.thread = Communicator(self, self.win)

        self.DriverGroup = QtGui.QGroupBox("Remote driver manager")
        PropertiesMainHFrame = QtGui.QVBoxLayout()

        self.LcnSHTtemp = QtGui.QLCDNumber(0)
        self.LcnSHTtemp.display(99.99)
        self.LcnSHTtemp.setDigitCount(6)
        self.LcnSHTHumi = QtGui.QLCDNumber(0)
        self.LcnSHTHumi.setDigitCount(6)
        self.LcnSHTHumi.display(999.99)
        self.LcnLTStemp = QtGui.QLCDNumber(0)
        self.LcnLTStemp.display(99.99)
        self.LcnLTStemp.setDigitCount(6)
        HbxWeather = QtGui.QHBoxLayout()
        HbxWeather.addStretch(1)
        HbxWeather.addWidget(self.LcnSHTtemp)
        HbxWeather.addWidget(self.LcnSHTHumi)
        HbxWeather.addWidget(self.LcnLTStemp)
        HbxWeather.addStretch(1)

        VbxMovementSpd = QtGui.QVBoxLayout()
        VbxMovementSpd.addStretch()
        VbxMovementSpd.addWidget(QtGui.QLabel("Speed of translation:"))
        self.SldTrans = QtGui.QSlider(1)
        self.SldTrans.setMaximum(10)
        self.SldTrans.setMinimum(1)
        VbxMovementSpd.addWidget(self.SldTrans)
        VbxMovementSpd.addWidget(QtGui.QLabel("Speed of time:"))
        #VbxMovementSpd.addStretch()

        self.NbxSpdTime = QtGui.QSpinBox()
        self.NbxSpdTime.setMaximum(0xFFFFFF)
        self.LcnRAspeed1 = QtGui.QLCDNumber(0)
        self.LcnRAspeed1.display(0x00)
        self.LcnRAspeed1.setHexMode()
        self.LcnRAspeed1.setDigitCount(2)
        self.LcnRAspeed2 = QtGui.QLCDNumber(0)
        self.LcnRAspeed2.setHexMode()
        self.LcnRAspeed2.setDigitCount(2)
        self.LcnRAspeed2.display(0x00)
        self.LcnRAspeed3 = QtGui.QLCDNumber(0)
        self.LcnRAspeed3.setHexMode()
        self.LcnRAspeed3.display(0x00)
        self.LcnRAspeed3.setDigitCount(2)
        self.LcnRAspeedDec = QtGui.QLCDNumber(0)
        self.LcnRAspeedDec.display(0)
        self.LcnRAspeedDec.setDigitCount(9)
        HbxActualSpeed = QtGui.QHBoxLayout()
        HbxActualSpeed.addWidget(self.NbxSpdTime)
        HbxActualSpeed.addStretch(1)
        HbxActualSpeed.addWidget(self.LcnRAspeed1)
        HbxActualSpeed.addWidget(self.LcnRAspeed2)
        HbxActualSpeed.addWidget(self.LcnRAspeed3)
        '''
        #websocket.enableTrace(True)
        adress = "ws://"+str(self.TbxIP.text())+":"+str(self.NbxPORT.value())+"/ws"

        print "Adresa:", adress
        ws = websocket.create_connection(adress)
        ws.send("Hello, World")
        result = ws.recv()
        print("Received {}".format(result))
        #ws.close()
        '''

        PropertiesMainHFrame.addLayout(HbxWeather)
        PropertiesMainHFrame.addLayout(VbxMovementSpd)
        PropertiesMainHFrame.addLayout(HbxActualSpeed)
        self.BtnSync = QtGui.QPushButton("Sync")
        self.ChbAutoUpdate =  QtGui.QCheckBox("AutoUpdate")
        PropertiesMainHFrame.addWidget(self.BtnSync)
        PropertiesMainHFrame.addWidget(self.ChbAutoUpdate)

        HbxTime = QtGui.QHBoxLayout()
        self.BtnTrans0 = QtGui.QPushButton("<<")
        self.BtnTime = QtGui.QPushButton("==")
        self.BtnTrans1 = QtGui.QPushButton(">>")
        HbxTime.addStretch(3)
        HbxTime.addWidget(self.BtnTrans0,2)
        HbxTime.addWidget(self.BtnTime,1)
        HbxTime.addWidget(self.BtnTrans1,2)
        HbxTime.addStretch(3)

        PropertiesMainHFrame.addLayout(HbxTime)
        PropertiesMainHFrame.addStretch(1)
        self.DriverGroup.setLayout(PropertiesMainHFrame)
        self.content.addWidget(self.DriverGroup)

        self.thread.updateUI()

        self.NbxSpdTime.valueChanged.connect(self.thread.change)
        self.BtnSync.clicked.connect(self.thread.sync)
        self.ChbAutoUpdate.stateChanged.connect(self.thread.change)
        

    
    
