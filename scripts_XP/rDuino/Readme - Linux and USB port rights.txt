# Linux requires the user to belong to the Dialout group to allow him to read/write from/to an USB port.
# If it's not feasible, the following solution will set the serial port R/W to everybody

sudoedit /etc/udev/rules.d/50-myusb.rules

# Copy this text and save:

KERNEL=="ttyUSB[0-9]*",MODE="0666"
KERNEL=="ttyACM[0-9]*",MODE="0666"

# Unplug the device and replug it, and it should be read/write from any user!


