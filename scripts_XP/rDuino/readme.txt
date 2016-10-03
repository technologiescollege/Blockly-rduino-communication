

Another possibility is to make a rules file in /etc/udev/rules.d/ directory. I had similar problem and I have created 50-myusb.rules file in the above directory with this content:

KERNEL=="ttyACM[0-9]*",MODE="0666"

Note that this will give any device connected to ttyACM socket read/write permissions. If you need only specific device to get read/write permissions you must also check idVendor and idProduct. You can find those by running lsusb command twice, once without your device connected and once when it is connected, then observe the additional line in the output. There you will see something like Bus 003 Device 005: ID ffff:0005. In this case idVendor = ffff and idProduct = 0005. Yours will be different. Than you modify the rules file to:

ACTION=="add", KERNEL=="ttyACM[0-9]*", ATTRS{idVendor}=="ffff", ATTRS{idProduct}=="0005", MODE="0666"

Now only this device gets the permissions. Read this to know more about writing udev rules.

# nano /etc/udev/rules.d/50-myusb.rules


KERNEL=="ttyACM[0-9]*",MODE="0666"
KERNEL=="ttyUSB[0-9]*",MODE="0666"




