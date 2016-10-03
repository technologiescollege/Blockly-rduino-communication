@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%scripts
cls
python.exe .\rDuino\rDuino_uploader_server.py -D COM12 -U arduino_debug.exe -C arduino.exe -T F:\Logiciels\Arduino_graphique\Blockly-at-rduino_AIO\ArduinoTechnoEduc\