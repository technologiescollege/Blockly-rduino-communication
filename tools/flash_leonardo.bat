@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%tools
cls
MODE COM11 BAUD=9600 RETRY=4
.\avrdude -Cavrdude.conf -v -patmega32u4 -cavr109 -P\\.\COM11 -b57600 -D -V -Uflash:w:s2aio-FirmataPlus.Leonardo.hex:i
pause