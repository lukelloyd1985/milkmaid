MilkMaid
=======

Checks milk level in the fridge using a Raspberry Pi SPI and force sensitive resistor.

The Python code outputs the response in the Nagios format of Critical, Warning or OK.

It also writes the last status of the milk to a file `milklevel.txt`.

Example contents of the file is as follows:

    2014-06-05 08:01,650,2.1,Milk running low - please buy more

This is CSV data containing:

- Last read date/time
- Resistor value - higher values mean LESS pressure (as in less milk)
- Voltage - will vary depending on the resistence in the pad (will be higher with less pressure)
- Message - this is a text string message (potentially for posting to HipChat)

Possible messages:

- **Milk has all gone (or been left out of the fridge!)** - _This is shown if the milk has literally all gone or is too low to measure or has been left out of the fridge_
- **Milk running low - please buy more** - _This is shown if the milk level is getting low_
- **Milk level currently okay** - _This is shown if there is currently sufficient milk_
- **Milk is plentiful!** - _This is shown if there is a lot of milk left_

The HTML page is also updated so the milk status can be viewed via the web broswer.


Notes on setting up MilkMaid
==========================

You must have Raspian already installed on your Pi. You can get the latest Raspbian image at `http://downloads.raspberrypi.org/raspbian_latest/` but you will also need a program to write the image to an SD card, if you are running Windows you can use Win32DiskImager available here `http://sourceforge.net/projects/win32diskimager/`

**Run the below commands to setup MilkMaid**
```
cd ~
raspi-config (in advanced options enable SPI)
apt-get update
apt-get install python-dev nagios-nrpe-server
git clone https://github.com/doceme/py-spidev.git
cd py-spidev
python setup.py install
cd ~
rm -rf py-spidev/
cd /opt
git clone git@bitbucket.org:lukelloyd1985/milkmaid.git
```

If you want you can setup Apache (outside the scope of this document) to use `/opt/milkmaid/web/` as the directory root and this will allow displaying of the latest milk level from the browser.
