#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from pymlab import config
from datetime import datetime
import ConfigParser


class RAserver():
	def __init__(self, arg):
		super(RAserver, self).__init__()
		self.arg = arg

		cfg = config.Config(
			i2c = {
				"port": 8,
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
		self.spi = cfg.get_device("spi")
		self.lcd = cfg.get_device("lcd")
		self.sht = cfg.get_device("sht")
		self.lts = cfg.get_device("lts")

		spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)



		lcd.clear()
		lcd.home()
		lcd.puts("RAserver")
		lcd.set_row2()
		lcd.puts("loaded")



def  main():
	ra = RAserver()

if __name__ == '__main__':
	main()