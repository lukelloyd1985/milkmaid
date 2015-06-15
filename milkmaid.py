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
import urllib2
import subprocess
import datetime
import fileinput
import sys

# Global variables
version = "v0.6"
now = datetime.datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M")


def write_file(level,message):
  # write data to local files
  # open current level for write - only most recent value will be in here
  current = open('./web/milklevel.txt', 'w')

  # write values
  current.write(message)
  #log.write(message)

  # close files
  current.close()


def update_html(level_percent_string,date):
  html_file_template = "./web/milklevel_template.html"
  html_file = "./web/index.html"

  f = open(html_file_template,'r')
  filedata = f.read()
  f.close()

  newdata = filedata.replace("@level@", level_percent_string + "%")
  newdata = newdata.replace("@date@", date)
  newdata = newdate.replace("@version@", version)

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


# Setup a value that indicates the resistor value we get back when there is nothing on the pad
nothing_on_pad_resistor_level = 1000


# Read the resistor data
resistor_level = ReadChannel(resistor_channel)
resistor_volts = ConvertVolts(resistor_level,2)


if resistor_level > 900:
  level_message = "Milk has all gone (or been left out of the fridge!)"

  # write to the local file
  write_file(resistor_level,current_time+","+str(resistor_level)+","+str(resistor_volts)+","+level_message)

  # update the HTML file
  resistor_level_percent = round(((float(resistor_level) / float(nothing_on_pad_resistor_level)) * 100),0)
  resistor_level_percent_string = str(100 - resistor_level_percent)
  resistor_level_percent_string = resistor_level_percent_string.rstrip("0").rstrip(".") if "." in resistor_level_percent_string else resistor_level_percent_string

  update_html(resistor_level_percent_string,current_time)

  # print the output and exit
  print level_message
  sys.exit(2)

elif 650 <= resistor_level <= 900:
  level_message = "Milk running low - please buy more"

  # write to the local file
  write_file(resistor_level,current_time+","+str(resistor_level)+","+str(resistor_volts)+","+level_message)

  # update the HTML file
  resistor_level_percent = round(((float(resistor_level) / float(nothing_on_pad_resistor_level)) * 100),0)
  resistor_level_percent_string = str(100 - resistor_level_percent)
  resistor_level_percent_string = resistor_level_percent_string.rstrip("0").rstrip(".") if "." in resistor_level_percent_string else resistor_level_percent_string

  update_html(resistor_level_percent_string,current_time)

  # print the output and exit
  print level_message
  sys.exit(1)

elif 400 <= resistor_level < 650:
  level_message = "Milk level currently okay"

  # write to the local file
  write_file(resistor_level,current_time+","+str(resistor_level)+","+str(resistor_volts)+","+level_message)

  # update the HTML file
  resistor_level_percent = round(((float(resistor_level) / float(nothing_on_pad_resistor_level)) * 100),0)
  resistor_level_percent_string = str(100 - resistor_level_percent)
  resistor_level_percent_string = resistor_level_percent_string.rstrip("0").rstrip(".") if "." in resistor_level_percent_string else resistor_level_percent_string

  update_html(resistor_level_percent_string,current_time)

  # print the output and exit
  print level_message
  sys.exit(0)

else:
  level_message = "Milk is plentiful!"

  # write to the local file
  write_file(resistor_level,current_time+","+str(resistor_level)+","+str(resistor_volts)+","+level_message)

  # update the HTML file
  resistor_level_percent = round(((float(resistor_level) / float(nothing_on_pad_resistor_level)) * 100),0)
  resistor_level_percent_string = str(100 - resistor_level_percent)
  resistor_level_percent_string = resistor_level_percent_string.rstrip("0").rstrip(".") if "." in resistor_level_percent_string else resistor_level_percent_string

  update_html(resistor_level_percent_string,current_time)

  # print the output and exit
  print level_message
  sys.exit(0)
