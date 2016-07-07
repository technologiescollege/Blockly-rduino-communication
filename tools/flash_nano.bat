@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%tools
cls
mode COM7 1200
timeout 1
.\avrdude -Cavrdude.conf -v -patmega328p -carduino -P\\.\COM8 -b57600 -D -V -Uflash:w:s2a-FirmataPlus.Nano.hex:i
pause