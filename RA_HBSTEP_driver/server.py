#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys
import time
from pymlab import config
from datetime import datetime
import ConfigParser
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import httpserver
from tornado import websocket
from tornado import ioloop
from tornado import web
import socket
import netifaces as ni

class axis:
    def __init__(self, spi, SPI_CS, Direction, StepsPerUnit):
        ' One axis of robot '
        self.spi = spi
        self.CS = SPI_CS
        self.Dir = Direction
        self.SPU = StepsPerUnit
        self.Reset()

    def Reset(self):
        ' Reset Axis and set default parameters for H-bridge '
        self.spi.SPI_write_byte(self.CS, 0xC0)      # reset
        self.spi.SPI_write_byte(self.CS, 0x14)      # Stall Treshold setup
        self.spi.SPI_write_byte(self.CS, 0x7F)  
        self.spi.SPI_write_byte(self.CS, 0x14)      # Over Current Treshold setup 
        self.spi.SPI_write_byte(self.CS, 0x0F)  
        #self.spi.SPI_write_byte(self.CS, 0x15)      # Full Step speed 
        #self.spi.SPI_write_byte(self.CS, 0x00)
        #self.spi.SPI_write_byte(self.CS, 0x30) 
        #self.spi.SPI_write_byte(self.CS, 0x0A)      # KVAL_RUN
        #self.spi.SPI_write_byte(self.CS, 0x50)
      
    def MaxSpeed(self, speed):
        ' Setup of maximum speed '
        self.spi.SPI_write_byte(self.CS, 0x07)       # Max Speed setup 
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)
      
    def ACC(self, speed):
        ' Setup of speed profile acceleration '
        self.spi.SPI_write_byte(self.CS, 0x05)       # Max Speed setup 
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)
    
    def DCC(self, speed):
        ' Setup of speed profile deceleration '
        self.spi.SPI_write_byte(self.CS, 0x06)       # Max Speed setup 
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)

    def ReleaseSW(self):
        ' Go away from Limit Switch '
        while self.ReadStatusBit(2) == 1:           # is Limit Switch ON ?
            self.spi.SPI_write_byte(self.CS, 0x92 | (~self.Dir & 1))     # release SW 
            while self.IsBusy():
                pass
            self.MoveWait(10)           # move 10 units away
 
    def GoZero(self, speed):
        ' Go to Zero position '
        self.ReleaseSW()

        self.spi.SPI_write_byte(self.CS, 0x82 | (self.Dir & 1))       # Go to Zero
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)  
        while self.IsBusy():
            pass
        time.sleep(0.3)
        self.ReleaseSW()

    def Move(self, units):
        ' Move some distance units from current position '
        steps = units * self.SPU  # translate units to steps 
        if steps > 0:                                          # look for direction
            self.spi.SPI_write_byte(self.CS, 0x40 | (~self.Dir & 1))       
        else:
            self.spi.SPI_write_byte(self.CS, 0x40 | (self.Dir & 1)) 
        steps = int(abs(steps))     
        self.spi.SPI_write_byte(self.CS, (steps >> 16) & 0xFF)
        self.spi.SPI_write_byte(self.CS, (steps >> 8) & 0xFF)
        self.spi.SPI_write_byte(self.CS, steps & 0xFF)

    def MoveWait(self, units):
        ' Move some distance units from current position and wait for execution '
        self.Move(units)
        while self.IsBusy():
            pass

    def Run(self, spd):
        ' The Run command produces a motion at SPD speed '
        if spd > 0:                                          # look for direction
            self.spi.SPI_write_byte(self.CS, 0x50 | (self.Dir & 1))
            print "A %x" %(0x50 | (self.Dir & 1)),
        else:
            self.spi.SPI_write_byte(self.CS, 0x51 | (self.Dir & 1))
            spd = spd *-1
            print "B %x" %(0x51 | (self.Dir & 1)),
        #//steps = int(abs(steps))   
        print spd  
        self.spi.SPI_write_byte(self.CS, (spd >> 16) & 0xFF)
        self.spi.SPI_write_byte(self.CS, (spd >>  8) & 0xFF)
        self.spi.SPI_write_byte(self.CS, (spd >>  0) & 0xFF)


    def Float(self):
        ' switch H-bridge to High impedance state '
        self.spi.SPI_write_byte(self.CS, 0xA0)

    def ReadStatusBit(self, bit):
        ' Report given status bit '
        self.spi.SPI_write_byte(self.CS, 0x39)   # Read from address 0x19 (STATUS)
        self.spi.SPI_write_byte(self.CS, 0x00)
        data0 = self.spi.SPI_read_byte()           # 1st byte
        self.spi.SPI_write_byte(self.CS, 0x00)
        data1 = self.spi.SPI_read_byte()           # 2nd byte
        #print hex(data0), hex(data1)
        if bit > 7:                                   # extract requested bit
            OutputBit = (data0 >> (bit - 8)) & 1
        else:
            OutputBit = (data1 >> bit) & 1        
        return OutputBit

    
    def IsBusy(self):
        """ Return True if tehre are motion """
        if self.ReadStatusBit(1) == 1:
            return False
        else:
            return True

# End Class axis --------------------------------------------------


class WSHandler(websocket.WebSocketHandler):
    def get(self):
        print "Aaaa"

    def open(self):
        print 'connection opened...'
        self.write_message("The server says: 'Hello'. Connection was accepted.")

    def on_message(self, message):
        self.write_message("The server says: " + message + " back at you")
        print 'received:', message

    def on_close(self):
        print 'connection closed...'


class RAserver():
    def __init__(self, port=10123 , lIP="127.0.0.1"):
        self.port = port
        self.lIP = lIP
        cfg = config.Config(
            i2c = {
                "port": 1,
            },
            bus = [
                { "name":"spi", "type":"i2cspi"},
                { "name":"lcd", "type":"i2clcd"},
                { "name":"sht", "type":"sht25"},
                { "name":"lts", "type":"lts01"},
            ],
        )

        n = 0
        cfg.initialize()
        self.lcd = cfg.get_device("lcd")
        self.spi = cfg.get_device("spi")
        self.sht = cfg.get_device("sht")
        self.lts = cfg.get_device("lts")
        self.lcd.light(1)

        self.vTimeSpd = 0
        self.vTimeDir = 0
        self.vActSpd = 0
        self.vActDir = 0

        self.lcd.reset()
        self.lcd.init()
        self.lcd.home()
        self.lcd.puts("Loading ...")
        self.spi.SPI_config(self.spi.I2CSPI_MSB_FIRST| self.spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| self.spi.I2CSPI_CLK_461kHz)
        time.sleep(0.5)
        self.ra_driver = axis(self.spi, self.spi.I2CSPI_SS0, 0, 1)
        self.ra_driver.Reset()
        self.ra_driver.ACC(15)
        self.ra_driver.DCC(15)
        self.lcd.home()
        self.lcd.puts("RAmotor-TT exten")
        self.ra_driver.MoveWait(10000)
        time.sleep(1)
        self.ra_driver.MoveWait(10000)

    def CreateServer(self):
        self.lcd.reset()
        self.lcd.init()
        time.sleep(0.1)
        self.lcd.clear()

        self.app = web.Application([
            (r'/', IndexHandler),
            (r'/ws', SocketHandler, {'parent': self}),
        ], debug=True)
        self.app.listen(self.port)

        self.lcd.home()
        #self.lcd.puts("WS port: %d" %self.port )
        self.lcd.set_row2()
        self.lcd.puts("IP:"+str(self.lIP))

        tornado.ioloop.IOLoop.current().start()

class IndexHandler(web.RequestHandler):
    def get(self):
        print "get WWW"
        self.render("index.html")

cl = []
class SocketHandler(websocket.WebSocketHandler): 
    def initialize(self, parent):
        self.ra = parent
        self.StationList = []
        #self.ra.lcd.puts("X")


    def check_origin(self, origin):
        return True

    def open(self):
        print "Opened new port: ", self
        if self not in cl:
            cl.append(self)
        #self.write_message("HI")

    def on_close(self):
        if self in cl:
            cl.remove(self)

    def on_message(self, message):
        print "Prijata zprava: ", message
        #self.write_message(u"ACK")
        if message[0] == "$":
            self.ra.lcd.light(1)
            m_type = message[1:message.find(";")].lower()
            print "data msg", m_type
            if m_type == "hi":
                self.StationList.append([self] + message[message.find(";")+1:].split(";") )
                print self.StationList
            elif m_type == "sht25":
                print "sht"
                temp = self.ra.sht.get_temp()
                humidity = self.ra.sht.get_hum()
                print "pozadavek o SHT t:", temp, " h:", humidity
                self.write_message(u"&sht25;%f;%f;" %(temp, humidity))
            elif m_type == "lts":
                print "lts"
                temp = self.ra.lts.get_temp()
                print "pozadavek o LTS t:", temp
                self.write_message(u"&lts;%f;" %(temp))
            elif m_type == "settime":
                print "set time speed"
                self.ra.vTimeSpd = int(message.split(';')[1])
                self.ra.vTimeDir =bool(message.split(';')[2])
                self.write_message(u"&settime;%i;%i" %(self.ra.vTimeSpd, self.ra.vTimeDir))
            elif m_type == "gettime":
                print "get time speed"
                #self.vTimeSpd = int(message.split(';')[1])
                #self.vTimeDir =bool(message.split(';')[2])
                self.write_message(u"&gettime;%i;%i" %(self.ra.vTimeSpd, self.ra.vTimeDir))
            elif m_type == "savetime":
                print "save time speed"
                #self.vTimeSpd = int(message.split(';')[1])
                #self.vTimeDir =bool(message.split(';')[2])
                self.write_message(u"&savetime;%i;%i" %(self.ra.vTimeSpd, self.ra.vTimeDir))
                self.ra.vTimeSpd = int(message.split(';')[1])
                self.ra.vTimeDir = bool(message.split(';')[2])
            elif m_type == "reloadtime":
                print "reload time speed"
                #self.vTimeSpd = int(message.split(';')[1])
                #self.vTimeDir =bool(message.split(';')[2])
                self.write_message(u"&reloadtime;%i;%i" %(self.ra.vTimeSpd, self.ra.vTimeDir))
            elif m_type == "setmultipler":
                print "set time speed multipler"
                self.ra.vActMultiplerSpd = int(message.split(';')[1])
                self.ra.vActMultiplerDir =bool(message.split(';')[2])
                self.write_message(u"&setmultipler;%i;" %(self.ra.vActMultiplerSpd, self.ra.vActMultiplerDir))
            elif m_type == "raspd":
                print "set actual speed "
                self.ra.vActSpd = int(message.split(';')[1])
                self.ra.vActDir = int(message.split(';')[2])
                self.write_message(u"&raspd;%d;%d" %(self.ra.vActSpd, self.ra.vActDir))
                if self.ra.vActDir != 0:
                    self.ra.vActSpd = self.ra.vActSpd * -1
                print self.ra.vActDir, self.ra.vActSpd
                #self.ra.spi.SPI_write(self.ra.spi.I2CSPI_SS0, [(self.ra.vActSpd >> 16)&0xff])
                #self.ra.spi.SPI_write(self.ra.spi.I2CSPI_SS0, [(self.ra.vActSpd >> 8)&0xff])
                #self.ra.spi.SPI_write(self.ra.spi.I2CSPI_SS0, [(self.ra.vActSpd >> 0)&0xff])
                self.ra.ra_driver.Run(self.ra.vActSpd)
            elif m_type == "onfollow":
                print "set actual speed "
                self.ra.vFollow = True
                self.write_message(u"&onfollow;%i;" %(self.ra.vFollow))
            elif m_type == "offfollow":
                print "set actual speed "
                self.ra.vFollow = False
                self.write_message(u"&offfollow;%i;" %(self.ra.vFollow))
            else:
                print "Neznama dolarova operace"
                self.write_message(u"&None")

        else:
            print "unsupported", message
            self.write_message(u"&unsupported")
        #    for client in cl:
        #        client.write_message(u"multicast: " + message)
        self.ra.lcd.light(0)



def main():
    ip="IPnotFound"
    try:
    	ip = ni.ifaddresses('eth0')[2][0]['addr']
    except:
	pass
    port = 10123
    print ip, port
    ra = RAserver(port, ip)
    ra.CreateServer()

if __name__ == "__main__":
    main()
