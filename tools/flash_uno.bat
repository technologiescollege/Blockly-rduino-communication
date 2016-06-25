@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%tools
cls
.\avrdude -Cavrdude.conf -v -patmega328p -carduino -P\\.\COM13 -b115200 -D -V -Uflash:w:s2aio-FirmataPlus.Uno.hex:i
pause