#!/usr/bin/python
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from PyQt4 import QtCore, QtGui
from threading import Thread, RLock
import websocket
import csv
import time


#l = RLock(False)

class ListenWebsocket(QtCore.QThread):
    def __init__(self, parent=None, adress = None):
        super(ListenWebsocket, self).__init__(parent)
        self.parent = parent

        #websocket.enableTrace(True)

        self.WS = websocket.WebSocketApp(adress,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close) 

    def run(self):
        self.WS.on_open = self.on_open;
        self.WS.run_forever()

    def on_message(self, ws, message):
        self.str = message
        print "ON_MESSAGE:", ws, message

    def on_error(self, ws, error):
        print "ON_ERROR:", error

    def on_close(self, ws):
        print "### closed ###"

    def on_open(self, client):
        print "##ON_OPEN##", client
        self.WS.send("client data")

    def send(self, data):
        print "##posilam data", data
        self.WS.send(data)

    def recv(self):
        self.str = ""
        while self.str == "":
            pass
        return self.str


class Communicator(QtCore.QThread):

    def __init__(self, parent = None, win = None):
        super(Communicator, self).__init__()
        self.parent= parent
        self.adress = "ws://"+str(self.parent.TbxIP.text())+":"+str(self.parent.NbxPORT.value())+"/ws"
        print "Adresa:", self.adress

        self.exiting = False

        self.vTimeSpd = 0
        self.vActSpd = 0
        self.vTrans = 1
        self.vFollow = False
        self.vDir = True
        self.vActDir = True
        self.vSHTtemp = 88.88
        self.vSHThumi = 88.88
        self.vSHTdew = 88.88
        self.vLTStemp = 88.88
        self.vChange = False
        self.vAutoUpdate = True
        self.vLastOutPut = False
        self.vRecLoc = False

        print "##created"

        self.ws = ListenWebsocket(None, self.adress)
        self.ws.start()

       # self.ws.send("$raspd;%d;%d;" %(self.vDir, self.vTimeSpd))
        result = self.ws.recv()
        print "Received:", result


    def __del__(self):
        print "Communicator ukoncovani ..."
        self.exiting = True
        self.wait()

    def sendSpd(self):
        self.ws.send("$raspd;%d;%d;" %(self.vActSpd, self.vActDir))
        result = self.ws.recv()
        #if result.split(';')[0] == "&lts":
        #    self.vLTStemp = float(result.split(';')[1])
        

    def sync(self):
        print "sync procedure"
        self.getWeather()
        self.updateUI()

        self.ws.send("$raspd;%d;%d;" %(self.vTimeSpd, self.vActDir))
        result = self.ws.recv()
        if result.split(';')[0] == "&lts":
            self.vLTStemp = float(result.split(';')[1])


    def getWeather(self):
        self.ws.send("$sht25;")
        print "getWeather"
        result = self.ws.recv()
        if result.split(';')[0] == "&sht25":
            self.vSHTtemp = float(result.split(';')[1])
            self.vSHThumi = float(result.split(';')[2])
            self.vSHTdew = ((self.vSHThumi / 100) ** 0.125) * (112 + 0.9 * self.vSHTtemp) + (0.1 * self.vSHTtemp) - 112

        self.ws.send("$lts;")
        result = self.ws.recv()
        if result.split(';')[0] == "&lts":
            self.vLTStemp = float(result.split(';')[1])




    def updateUI(self):
        self.parent.LcnSHTtemp.display(self.vSHTtemp)
        self.parent.LcnSHTHumi.display(self.vSHThumi)
        self.parent.LcnSHTDew.display(self.vSHTdew)
        self.parent.LcnLTStemp.display(self.vLTStemp)

        #self.parent.LcnRAspeed1.display((self.vTimeSpd >> 16)&0xff)
        #self.parent.LcnRAspeed2.display((self.vTimeSpd >> 8)&0xff)
        #self.parent.LcnRAspeed3.display((self.vTimeSpd >> 0)&0xff)

        self.parent.NbxSpdTime.setValue(self.vTimeSpd)
        self.parent.LcnRAspeed1.display(self.vTimeSpd)
        self.parent.LcnRAspeed2.display(self.vTimeSpd*(self.vTrans**2))
        self.parent.LcnRAspeed3.display(self.vActSpd)


    def change(self, type=None, widget=None):
        print "change,", self, type, widget
        if type == "NbxSpdTime":
            self.vTimeSpd = widget.value()
            #if self.vFollow:
            #    self.vActSpd = self.vTimeSpd
        elif type == "ChbTimeDir":
            self.vDir = bool(widget.checkState())
            self.vActDir = self.vDir
            #print type, ": ", widget.checkState()
            self.sendSpd()
        elif type == "ChbAutoUpdate":
            self.vAutoUpdate = bool(widget.checkState())
            #print type, ": ", widget.checkState()
        elif type == "SldTrans":
            self.vTrans = bool(widget.checkState())
        elif type == "ChbLastOutPut":
            self.vLastOutPut = widget.checkState()
        elif type == "ChbRecordLocaly":
            self.vRecLoc = widget.checkState()

        self.updateUI()

        '''
        self.ChbRecordLocaly.stateChanged.connect(lambda: self.thread.change("ChbRecordLocaly", self.ChbRecordLocaly))
        self.ChbRecordRemotly.stateChanged.connect(lambda: self.thread.change("ChbRecordRemotly", self.ChbRecordRemotly))
        self.ChbTimeDir.stateChanged.connect(lambda: self.thread.change("ChbTimeDir", self.ChbTimeDir)
        '''

    def save(self, type = None):
        print "SAVE:", type

        if type == 0:
            self.ws.send("$gettime;")
            result = self.ws.recv()
            if result.split(';')[0] == "&gettime":
                self.vTimeSpd = int(result.split(';')[1])
                self.vDir = int(result.split(';')[2])
            self.updateUI()

        if type == 2:
            self.ws.send("$savetime;%d;%d" %(self.vTimeSpd, int(self.vDir)))
                

    def trans(self, type = 0):
        print "TRANS:", type
        if type == -2:
            self.vActSpd = self.vTimeSpd - self.vTimeSpd*(self.vTrans**2)
            print  self.vActSpd, self.vTimeSpd, self.vTimeSpd*(self.vTrans**2), self.vTimeSpd - self.vTimeSpd*(self.vTrans**2)
            if self.vActSpd < 0:
                self.vActSpd = self.vActSpd*-1
                self.vActDir = not self.vDir
            #if self.vActSpd < self.vTimeSpd*(self.vTrans**2):
            #    self.vActDir != self.vDir
            else:
                self.vActDir = self.vDir
            print  self.vActSpd, self.vTimeSpd, self.vTimeSpd*(self.vTrans**2), self.vTimeSpd - self.vTimeSpd*(self.vTrans**2)
        if type == 1:
            self.vActSpd = self.vTimeSpd
            self.vFollow = True
            self.vActDir = self.vDir
        if type == 0:
            self.vActSpd = 0
            self.vFollow = False
            self.vActDir = self.vDir
        if type == +2:
            self.vActSpd = self.vTimeSpd + self.vTimeSpd*(self.vTrans**2)
            #if self.vActSpd < self.vTimeSpd*(self.vTrans**2):
            #    self.vActDir != self.vDir
            #    self.vActSpd = self.vActSpd*-1
            #else:
            self.vActDir = self.vDir
        if type == -1:
            self.vActSpd = self.vTimeSpd
            self.vActDir = self.vDir

        self.updateUI()
        self.sendSpd()
        
    def upgrade(self):
        pass

    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        timer1 = time.time()
        timer2 = time.time()
        fLog =open("Log_%s.txt" %time.strftime("%Y%m%d"),'a')
        while not self.exiting:
            if timer1+5 < time.time():
                if self.vAutoUpdate:
                    self.getWeather()
                if not self.vChange:
                    self.upgrade()
                if self.vLastOutPut:
                    try:
                        fLast=open("LastData.txt",'w')
                        fLast.write("%.2f\n%.2f" %(round(self.vSHTtemp,2), round(self.vSHThumi,2)))
                        fLast.close()
                    except Exception, e:
                        print e
                if self.vRecLoc:
                    try:
                        fLog =open("Log_%s.txt" %time.strftime("%Y%m%d"),'a')
                        fLog.write( str(time.time()) + ";" + str(self.vSHTtemp) + ";" + str(self.vSHThumi) + ";" + str(self.vLTStemp) + ";\n")
                        fLog.close()
                    except Exception, e:
                        print e
                timer1 = time.time()
                self.updateUI()
            #if timer2+2.5 < time.time():
                #print self.vActDir, self.vActSpd, self.vDir, self.vTimeSpd
            time.sleep(1)
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
        self.thread.start()

        self.DriverGroup = QtGui.QGroupBox("Remote driver manager")
        PropertiesMainHFrame = QtGui.QVBoxLayout()

        self.LcnSHTtemp = QtGui.QLCDNumber(0)
        self.LcnSHTtemp.setDigitCount(5)
        self.LcnSHTtemp.display(99.99)
        self.LcnSHTHumi = QtGui.QLCDNumber(0)
        self.LcnSHTHumi.setDigitCount(5)
        self.LcnSHTHumi.display(999.99)
        self.LcnSHTDew = QtGui.QLCDNumber(0)
        self.LcnSHTDew.setDigitCount(5)
        self.LcnSHTDew.display(99.99)
        self.LcnLTStemp = QtGui.QLCDNumber(0)
        self.LcnLTStemp.setDigitCount(5)
        self.LcnLTStemp.display(99.99)
        HbxWeather = QtGui.QHBoxLayout()
        HbxWeather.addStretch(1)
        HbxWeather.addWidget(self.LcnSHTtemp)
        HbxWeather.addWidget(self.LcnSHTHumi)
        HbxWeather.addWidget(self.LcnSHTDew)
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
        self.ChbTimeDir = QtGui.QCheckBox()
        self.ChbTimeDir.setObjectName("ChbLR")
        self.NbxSpdTime = QtGui.QSpinBox()
        self.NbxSpdTime.setMaximum(0xFFFFFF)
        self.LcnRAspeed1 = QtGui.QLCDNumber(0)
        self.LcnRAspeed1.display(0x00)
        self.LcnRAspeed1.setHexMode()
        self.LcnRAspeed1.setDigitCount(6)
        self.LcnRAspeed2 = QtGui.QLCDNumber(0)
        self.LcnRAspeed2.setHexMode()
        self.LcnRAspeed2.setDigitCount(6)
        self.LcnRAspeed2.display(0x00)
        self.LcnRAspeed3 = QtGui.QLCDNumber(0)
        self.LcnRAspeed3.setHexMode()
        self.LcnRAspeed3.display(0x00)
        self.LcnRAspeed3.setDigitCount(6)
        self.LcnRAspeedDec = QtGui.QLCDNumber(0)
        self.LcnRAspeedDec.display(0)
        self.LcnRAspeedDec.setDigitCount(9)
        HbxActualSpeed = QtGui.QHBoxLayout()
        HbxActualSpeed.addWidget(self.ChbTimeDir)
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

        self.BtnSync = QtGui.QPushButton("Sync")
        self.ChbAutoUpdate =  QtGui.QCheckBox("AutoUpdate")

        HbxTime = QtGui.QHBoxLayout()
        HbxTime2 = QtGui.QHBoxLayout()
        self.BtnTrans0 = QtGui.QPushButton("<<")
        self.BtnTrans0.setObjectName("BtTransFBW")
        self.BtnTime = QtGui.QPushButton("==")
        self.BtnTime.setObjectName("BtTransPlay")
        self.BtnTrans1 = QtGui.QPushButton(">>")
        self.BtnTrans1.setObjectName("BtTransFFW")
        HbxTime.addStretch(3)
        HbxTime.addWidget(self.BtnTrans0,2)
        HbxTime.addWidget(self.BtnTime,1)
        HbxTime.addWidget(self.BtnTrans1,2)
        HbxTime.addStretch(3)
        self.BtnTimeStop = QtGui.QPushButton("||")
        self.BtnTimeStop.setObjectName("BtTransPause")
        HbxTime2.addStretch(2)
        HbxTime2.addWidget(self.BtnTimeStop,7)
        HbxTime2.addStretch(2)

        VbxSet = QtGui.QVBoxLayout()
        self.BtnSetGetAllData = QtGui.QPushButton("Get all data")
        self.BtnSetSaveLocaly = QtGui.QPushButton("Save localy")
        self.BtnSetSaveRemotly = QtGui.QPushButton("Save remotly")
        self.ChbRecordRemotly = QtGui.QCheckBox("Record remotly")
        self.ChbRecordLocaly = QtGui.QCheckBox("Record localy")
        self.ChbLastOutPut = QtGui.QCheckBox("Record last file")
        VbxSet.addWidget(self.BtnSetGetAllData)
        VbxSet.addWidget(self.BtnSetSaveLocaly)
        VbxSet.addWidget(self.BtnSetSaveRemotly)
        VbxSet.addWidget(self.ChbRecordRemotly)
        VbxSet.addWidget(self.ChbRecordLocaly)
        VbxSet.addWidget(self.ChbLastOutPut)

        PropertiesMainHFrame.addLayout(HbxWeather)
        PropertiesMainHFrame.addLayout(VbxMovementSpd)
        PropertiesMainHFrame.addLayout(HbxActualSpeed)
        PropertiesMainHFrame.addWidget(self.BtnSync)
        PropertiesMainHFrame.addWidget(self.ChbAutoUpdate)
        PropertiesMainHFrame.addLayout(HbxTime)
        PropertiesMainHFrame.addLayout(HbxTime2)
        PropertiesMainHFrame.addLayout(VbxSet)
        PropertiesMainHFrame.addStretch(1)
        self.DriverGroup.setLayout(PropertiesMainHFrame)
        self.content.addWidget(self.DriverGroup)

        self.thread.updateUI()

        self.NbxSpdTime.valueChanged.connect(lambda: self.thread.change("NbxSpdTime", self.NbxSpdTime))
        #self.BtnSync.clicked.connect(self.OnSync)
        self.SldTrans.valueChanged.connect(lambda: self.thread.change("SldTrans", self.SldTrans))
        self.BtnSync.clicked.connect(lambda: self.thread.sync())
        self.BtnTrans0.pressed.connect(lambda: self.thread.trans(-2))
        self.BtnTrans0.released.connect(lambda: self.thread.trans(-1))
        self.BtnTime.clicked.connect(lambda: self.thread.trans(1))
        self.BtnTimeStop.clicked.connect(lambda: self.thread.trans(0))
        self.BtnTrans1.pressed.connect(lambda: self.thread.trans(+2))
        self.BtnTrans1.released.connect(lambda: self.thread.trans(-1))
        self.BtnSetGetAllData.clicked.connect(lambda: self.thread.save(0))
        self.BtnSetSaveLocaly.clicked.connect(lambda: self.thread.save(1))
        self.BtnSetSaveRemotly.clicked.connect(lambda: self.thread.save(2))
        self.ChbAutoUpdate.stateChanged.connect(lambda: self.thread.change("ChbAutoUpdate", self.ChbAutoUpdate))
        self.ChbRecordLocaly.stateChanged.connect(lambda: self.thread.change("ChbRecordLocaly", self.ChbRecordLocaly))
        self.ChbRecordRemotly.stateChanged.connect(lambda: self.thread.change("ChbRecordRemotly", self.ChbRecordRemotly))
        self.ChbLastOutPut.stateChanged.connect(lambda: self.thread.change("ChbLastOutPut", self.ChbLastOutPut))
        self.ChbTimeDir.stateChanged.connect(lambda: self.thread.change("ChbTimeDir", self.ChbTimeDir))




