@echo off
break ON
rem fichiers BAT et fork créés par Sébastien CANET
SET currentpath=%~dp1
cd %currentpath%scripts
cls
python.exe .\rDuino\rDuino_uploader.py