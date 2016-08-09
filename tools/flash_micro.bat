@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%tools
cls
mode COM5 1200
timeout 3
.\avrdude -Cavrdude.conf -v -patmega32u4 -cavr109 -P\\.\COM11 -b57600 -D -V -Uflash:w:PyMata-aio-FirmataPlus.Micro.ino.hex:i
pause