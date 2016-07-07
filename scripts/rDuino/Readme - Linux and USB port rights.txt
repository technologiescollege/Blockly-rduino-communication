The easy way:

sudoedit /etc/udev/rules.d/50-myusb.rules

Save this text:

KERNEL=="ttyUSB[0-9]*",MODE="0666"
KERNEL=="ttyACM[0-9]*",MODE="0666"

Unplug the device and replug it, and it should be read/write from any user!


