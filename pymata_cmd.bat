@echo off
break ON
rem fichiers BAT et fork cr��s par S�bastien CANET
SET currentpath=%~dp1
cd %currentpath%scripts
cls
python.exe .\Lib\site-packages\pymata_aio\pymata_iot.py -l 5 -c no_client -comport COM14