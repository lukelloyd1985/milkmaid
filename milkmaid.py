#!/usr/bin/python
#--------------------------------------   
# This script reads data from a MCP3008 ADC device using the Raspberry Pi SPI bus.
#
# Author : Luke Lloyd (based on code by Russ Hill/Matt Hawkins - https://github.com/talis/gotmilk-hack)
#
# Ref :
#
# http://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/
# http://engineering.talis.com/articles/hardware-hack-got-milk/
#
#--------------------------------------

import spidev
import time
import os, os.path
import requests
import ConfigParser
import urllib2
import subprocess
import datetime
import fileinput

version = "v0.1"

config = ConfigParser.ConfigParser()
config.read([os.path.expanduser("~/gotmilk/.gotmilk"), '/etc/gotmilk'])

def write_file(level,message):
	# write data to local files

	# open log for append
	#log = open('milklog.txt', 'a')

	# open current level for write - only most recent value will be in here
	current = open('milklevel.txt', 'w')

	# write values
	current.write(message)
	#log.write(message)

	# close files
	current.close()
	#log.close()

def update_html(level_percent_string,date):
	html_file_template = "/home/pi/gotmilk/milklevel_template.html"
	html_file = "milklevel.html"

	f = open(html_file_template,'r')
	filedata = f.read()
	f.close()

	newdata = filedata.replace("@level@", level_percent_string + "%")
	newdata = newdata.replace("@date@", date)

	f = open(html_file,'w')
	f.write(newdata)
	f.close()	

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places. 
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)  
  return volts
  
# Define sensor channels
resistor_channel = 0

# Define previous resistor level
previous_resistor_level = 0
nothing_on_pad_count = 0
milk_gone_warning_shown = False
milk_low_warning_shown = False
milk_ok_warning_shown = False

# Setup a value that indicates the resistor value we get back when there is nothing on the pad
nothing_on_pad_resistor_level = 1000

while True:
	# get current datetime
	now = datetime.datetime.now()

	level_message = "Monitoring..."

	# Read the resistor data
	resistor_level = ReadChannel(resistor_channel)
	resistor_volts = ConvertVolts(resistor_level,2)

	if resistor_level != previous_resistor_level: 
		if resistor_level > 900:
			# Nothing on the pad
			level_message = "Nothing on the pad"
			nothing_on_pad_count += 1
			if nothing_on_pad_count == 5:
				nothing_on_pad_count = 0
				level_message = "Milk has all gone (or been left out of the fridge!)"
				if milk_gone_warning_shown == False:
					send_message(level_message,'red')
					milk_gone_warning_shown = True
					milk_ok_warning_shown = False
		elif 650 <= resistor_level <= 900:
 			# Milk running low
			level_message = "Milk running low - please buy more"
			nothing_on_pad_count = 0
			if milk_low_warning_shown == False:
				send_message(level_message,'yellow')
				milk_low_warning_shown = True
				milk_ok_warning_shown = False
		elif 400 <= resistor_level < 650:
			# Milk is healthy
			level_message = "Milk level currently okay"

			# See if we previous mentioned that the milk was low, if so, message that the milk is now okay (if we didn't do that already)
			if (milk_gone_warning_shown == True or milk_low_warning_shown == True):
				if milk_ok_warning_shown == False:
					send_message(level_message,'green')
					milk_ok_warning_shown = True

			# Reset flags
			milk_low_warning_shown = False
			milk_gone_warning_shown = False
			nothing_on_pad_count = 0
		else:
			# Loads of milk
			level_message = "Milk is plentiful!"

			# See if we previous mentioned that the milk was low, if so, message that the milk is now okay (if we didn't do that already)
			if (milk_gone_warning_shown == True or milk_low_warning_shown == True):
				if milk_ok_warning_shown == False:
					send_message(level_message,'green')
					milk_ok_warning_shown = True

			# Reset flags
			milk_low_warning_shown = False
			milk_gone_warning_shown = False
			nothing_on_pad_count = 0

	current_time = now.strftime("%Y-%m-%d %H:%M")

	# Print out results
	#print "--------------------------------------------"  
	#print("{} pressure : {} ({}V)".format(current_time,resistor_level,resistor_volts))
	#print level_message  

	# write the level to the local logs etc
	write_file(resistor_level,current_time+","+str(resistor_level)+","+str(resistor_volts)+","+level_message)

	# update the HTML file
	resistor_level_percent = round(((float(resistor_level) / float(nothing_on_pad_resistor_level)) * 100),0)
	resistor_level_percent_string = str(100 - resistor_level_percent)
	resistor_level_percent_string = resistor_level_percent_string.rstrip("0").rstrip(".") if "." in resistor_level_percent_string else resistor_level_percent_string

	update_html(resistor_level_percent_string,current_time)

	# set the previous level to the current level for comparison next time
	previous_resistor_level = resistor_level

	# Wait before repeating loop
	time.sleep(DELAY)
 
