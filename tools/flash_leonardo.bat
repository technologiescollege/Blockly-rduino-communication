@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%tools
cls
.\avrdude -Cavrdude.conf -v -patmega32u4 -cavr109 -P\\.\COM9 -b57600 -D -V -Uflash:w:PyMata-aio-FirmataPlus.Leonardo.ino.hex:i
pause