#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# --------------------------------------------------------------------
# rDuino_Uploader_Server : Mini server to compile and upload
# a code to the target board.
#
# This program serves HTTP requests on port 888
# Compile and upload the code using the arduino IDE (linux)
#
# Compile and upload example: arduino --board arduino:avr:nano:cpu=atmega168 --port /dev/ttyACM0 --upload /path/to/sketch/sketch.ino
# See here: https://github.com/arduino/Arduino/blob/ide-1.5.x/build/shared/manpage.adoc
#
# --------------------------------------------------------------------

# VERSION NUMBER
version = "1.0"


import os
from os import walk
import sys
import glob
import serial
import subprocess
import tempfile
import time
import datetime
import optparse
#from easyprocess import EasyProcess # https://pypi.python.org/pypi/EasyProcess
import sys
from threading import Thread


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) # Only the errors will be displayed, not the HTTP requests in the flask server
# See http://stackoverflow.com/questions/14888799/disable-console-messages-in-flask-server


# from http://flask.pocoo.org/ 
from flask import Flask, abort, redirect, url_for, request, render_template,  Markup,  make_response,  session,  escape,  jsonify

# Configuration data
#debugMode = 0

myPort = 5005


myCompileAndUploadOption = "--upload"
myCompileOption = "--verify"
myVerify = "--verify"
myInstallLibrary = "--install-library"
myInstallBoard = "--install-boards"

# avrdude -U flash:w:[put-hex-file-path-here]:i -C avrdude.conf -v -p atmega328 -b 115200 -c stk500v2 -P [put-device-path-here]
#
# C:\dev\Arduino\hardware/tools/avr/bin/avrdude 
#-CC:\dev\Arduino\hardware/tools/avr/etc/avrdude.conf 
#-v -patmega2560 -carduino -b115200 -cstk500v2
#-P\\.\COM1 
#-D -Uflash:w:C:\Users\sandy_000\Documents\Arduino\polargraph_firmware\polargraph_server_a1\polargraph_server_a1_adafruit_v1.cpp.hex:i

myAvrdudeOptions_file = " -c stk500v2 -D -Uflash:w:"
myAvrdudeOptions_file_end = ":i"
myAvrdudeOptions_target = " -b 115200 -P "
myAvrdudeOptions_target_end = ""
myAvrdudeOptions_configfile = " -C "
myAvrdudeConfigFile = "hardware\\tools\\avr\\etc\\avrdude.conf"
myAvrdudeOptions_configfile_end = ""
myAvrdudeOptions_board = " -v -p "
myAvrdudeOptions_board_end = ""
#myAvrdudeBoard = "atmega328"
myAvrdudeBoard = "atmega2560"

#myHEXfilePath = "D:\\Users\\s551544\\Personnel\\Blockly\\rDuino-Compiler-Uploader-Server-master\\arduinoBinaries"
myHEXfilePath = "arduinoBinaries"
#myHEXfileList = [ "my_StandardFirmataPlus.ino.standard.hex", "my_StandardFirmataPlus.ino.mega.hex",  "my_StandardFirmataPlus.ino.with_bootloader.standard.hex", "my_StandardFirmataPlus.ino.with_bootloader.mega.hex"]
myHEXfileList = [ ] # Will be populated at run time by exploring the myHEXfilePath folder

myBoardOptions = "--board"
boardList = [ "arduino:avr:uno",  "arduino:avr:mega:cpu=atmega2560"]
myBoard = "arduino:avr:uno"

myTargetOption = "--port"

myOptionList = ["", "--verbose-upload",  "--verbose-build",  "--verbose",  "--preserve-temp-files"]
myOption = ""

if sys.platform.startswith('win'):
    separator = "\\"  # Windows
    myTempDirectory = "rDuinoUploader\\blockly_upload_temp"
    myFileName = "blockly_upload_temp.ino"
    myHEXfile = "my_StandardFirmataPlus.ino.standard.hex"
    myArduinoPrecommand = ""
    myArduinoToolPath = "C:\\Programmation\\Arduino\\"
    myArduinoUploadExe = "arduino_debug.exe" # Windows
#    myArduinoUploadExe = "arduino.exe" # Windows
    myArduinoCompileExe = "arduino.exe" # Windows
    myAvrDudeExe = "hardware\\tools\\avr\\bin\\avrdude.exe"
    myTarget = "COM1"    
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    separator = "/"  # Linux
    myTempDirectory = "/home/nbremond/Arduino/blockly_upload_temp"
#    myTempDirectory = "/tmp/Arduino/blockly_upload_temp"
    myFileName = "blockly_upload_temp.ino"    
    myHEXfile = "my_StandardFirmataPlus.ino.standard.hex"
    myArduinoPrecommand = "export DISPLAY=:0.0 && "
    myArduinoToolPath = "/home/nbremond/Tools/Arduino/arduino-nightly/"
    myArduinoUploadExe = "arduino " # Linux
    myArduinoCompileExe = "arduino " # Linux
    myAvrDudeExe = "export DISPLAY=:0.0 && avrdude" # Linux
    myTarget = "/dev/ttyUSB0"    
elif sys.platform.startswith('darwin'):
    separator = "/"  # Mac - Not tested
    myTempDirectory = "Arduino/blockly_upload_temp"
    myFileName = "blockly_upload_temp.ino"    
    myHEXfile = "my_StandardFirmataPlus.ino.standard.hex"
    myArduinoPrecommand = ""
    myArduinoToolPath = "Arduino.app/Contents/MacOS"
    myArduinoUploadExe = "Arduino" # MAC - not tested
    myArduinoCompileExe = "Arduino" # MAC - not tested
    myAvrDudeExe = "avrdude" # MAC - not tested
    myTarget = "/dev/ttyUSB0"    
else:
    raise EnvironmentError('Unsupported platform')
    

myCmd = ""
theResult = ""
theError = ""
theReturnCode = "Waiting for command..." # In waiting mode"
compileTime = datetime.datetime.now()

myProc = None

    
# Define the main application
app = Flask(__name__)





# This function return a list of the available serial ports. Works on any system
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(25)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

#    print("  Serial port list :%s" % ports)
    result = []
    for port in ports:
#        print("     trying port :%s" % port)
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
#            print("Serial port %s detected." % port)
        except (OSError, serial.SerialException):
            pass
    print("List of detected USB devices:%s" % result)
    return result
    

#targetList = ["COM1","COM2","COM3","COM4","COM5","COM6"]
#targetList = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"]
targetList = [""] + serial_ports()
 


class RunProcess(Thread):
    def __init__(self, cmd, result="", error=""):
        """Initialisation of the Thread"""
        global theReturnCode
        global theResult
        global theError

        Thread.__init__(self)
        
        print("Opening thread...")
        self.computingInProgress = False
        self.done = False
        
        self.myCmd = cmd
        theResult = result
        theError  = error         
        theReturnCode = "In progress..." # In progress mode"  

    def run(self):
        global myProc
        global theReturnCode
        global theError
        global theResult
        
        """Code to be run during the thread."""
        print("--> ", end="")
        if not self.computingInProgress:
            print("Running : %s ..." % self.myCmd)
#            print("Running : %s ..." % ' '.join(self.myCmd))
            if sys.platform.startswith('win'):
                myProc = subprocess.Popen(self.myCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, shell=True)
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                myProc = subprocess.Popen(self.myCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, shell=True)
            elif sys.platform.startswith('darwin'):
                myProc = subprocess.Popen(self.myCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, shell=True) # NOT TESTED
            else:
                raise EnvironmentError('Unsupported platform')
            self.computingInProgress  = True  
            
        while not self.done:
            print(".", end="")

            if myProc is not None:

                for line in myProc.stdout:
                    result = line.decode('utf-8', errors='ignore')
                    theResult = theResult + result.replace("\n","<br/>")
                    print("%s" % result)
                 
                #theTime = datetime.datetime.now()
                for line in myProc.stderr:
                    error = line.decode('utf-8', errors='ignore')
                    theError = theError + error.replace("\n","<br/>")
                    print("%s" % error)
            
            status = myProc.poll()
            if status is not None: # End of subprocess
                if (theError.find("can't open") >= 0):
                    theReturnCode = -2 # Error
                elif (theError.find("stk500_getsync") >= 0):
                    theReturnCode = -3 # Error
                elif (theError.find("exit status 1") >= 0):
                    theReturnCode = -4 # Error
                else:
                    theReturnCode = myProc.returncode # Good or error returned code
                print("Return code:[%s]\n" % theReturnCode)
             
                myProc = None
                self.done = True
                print("Done")

        
#global app
# Define the routes
    
# Main page, and process code compile and upload requests
@app.route('/', methods=['GET', 'POST'])
def main_page():
    global theResult
    global theError
    global theReturnCode
    global myCmd
    global myFileName
    global compileTime
    global targetList
    global myProc

    #print(" Call main page.\n")
    targetList = [""] + serial_ports() # Update the list of serial ports, in case a board has been connected
    #print("Updated list of serial ports : %s \n   --> myTarget : %s" % (targetList, myTarget))     
    
    return render_template('main.html', result=theResult, error=theError)

    
# Program an HEX file using Avrdude
@app.route('/upload_hex', methods=['GET', 'POST'])
def upload_hex():
    global myCmd
    global myHEXfile
    global myHEXfileList
    global myTarget
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     

    if request.method == 'POST':
    
        myHEXfile = request.form['filename']
        myTarget = request.form['target']

        # avrdude -U flash:w:[put-hex-file-path-here]:i -C avrdude.conf -v -p atmega328 -b 115200 -c stk500v2 -P [put-device-path-here]
#        myCmd = [myArduinoToolPath+myAvrDudeExe]
#        myCmd.append(myAvrdudeOptions_file+myHEXfilePath+separator+myHEXfile+myAvrdudeOptions_file_end)
#        myCmd.append(myAvrdudeOptions_configfile+myArduinoToolPath+myAvrdudeConfigFile+myAvrdudeOptions_configfile_end)
#        myCmd.append(myAvrdudeOptions_board+myAvrdudeBoard+myAvrdudeOptions_board_end)
#        myCmd.append( myAvrdudeOptions_target+myTarget+myAvrdudeOptions_target_end)

        myCmd = [myArduinoToolPath+myAvrDudeExe+" "+myAvrdudeOptions_file+myHEXfilePath+separator+myHEXfile+myAvrdudeOptions_file_end+" "+myAvrdudeOptions_configfile+myArduinoToolPath+myAvrdudeConfigFile+myAvrdudeOptions_configfile_end+" "+myAvrdudeOptions_board+myAvrdudeBoard+myAvrdudeOptions_board_end+" "+myAvrdudeOptions_target+myTarget+myAvrdudeOptions_target_end]
        
        # Creation of the thread
        thread_1 = RunProcess(myCmd)
        # Launch of the thread
        thread_1.start()
        print("\nProcess called in a separate thread..." )
        
    targetList = [""] + serial_ports() # Update the list of serial ports, in case a board has been connected
    
    # Get list of files in the "upload" folder
    #from os import walk
    myHEXfileList = []
    for (dirpath, dirnames, filenames) in walk(myHEXfilePath):
        myHEXfileList.extend(filenames)
        break
    print("myHEXfileList: %s" % myHEXfileList)
    return render_template('program_hex_file.html', cmd=myCmd, result=theResult, error=theError,  theTargetList=targetList, theTarget=myTarget, theFileList=myHEXfileList, theFile=myHEXfile)
    

# Install a new library in the Arduino IDE
@app.route('/run_websocket', methods=['GET', 'POST'])
def run_websocket():
    global myCmd
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     
    
#    if request.method == 'POST':
    
#        theLibrary = request.form['library']
        
        # arduino --install-library "Bridge:1.0.0"
        #myCmd = myArduinoToolPath + myArduinoUploadExe +" "+myInstallLibrary+" "+theLibrary
#        myCmd = [myArduinoToolPath+myArduinoUploadExe, myInstallLibrary, theLibrary]
        
        # Creation of the thread
#        thread_1 = RunProcess(myCmd)
        # Launch of the thread
#        thread_1.start()
#        print("\nProcess called in a separate thread..." )
        
    return render_template('run_websocket.html', cmd=myCmd, result=theResult, error=theError)    
    
    
# Install a new library in the Arduino IDE
@app.route('/install_library', methods=['GET', 'POST'])
def install_library():
    global myCmd
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     
    
    if request.method == 'POST':
    
        theLibrary = request.form['library']
        
        # arduino --install-library "Bridge:1.0.0"
        myCmd = myArduinoPrecommand+myArduinoToolPath + myArduinoUploadExe +" "+myInstallLibrary+" "+theLibrary
#        myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe, myInstallLibrary, theLibrary]
        
        # Creation of the thread
        thread_1 = RunProcess(myCmd)
        # Launch of the thread
        thread_1.start()
        print("\nProcess called in a separate thread..." )
        
    return render_template('install_library.html', cmd=myCmd, result=theResult, error=theError)


# Install a new baord in the Arduino IDE
@app.route('/install_board', methods=['GET', 'POST'])
def install_board():
    global myCmd
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     
    
    if request.method == 'POST':
    
        theBoard = request.form['board']
        # arduino --install-boards "arduino:sam"
        myCmd = myArduinoPrecommand+myArduinoToolPath + myArduinoUploadExe + " "+myInstallBoard+" "+theBoard
#        myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe, myInstallBoard, theBoard]

        # Creation of the thread
        thread_1 = RunProcess(myCmd)
        # Launch of the thread
        thread_1.start()
        print("\nProcess called in a separate thread..." )
        
    return render_template('install_board.html',  theBoardList=boardList, theBoard=myBoard, cmd=myCmd, result=theResult, error=theError)

# Define the target address
@app.route('/set_target', methods=['GET', 'POST'])
def set_target():
    global myTarget
    global theResult
    global theError
    global theReturnCode

    if request.method == 'POST':
        myTarget = request.form['target']
        print("Taget set to:[%s]\n" % (myTarget))
        theResult = ""
        theError = ""
        theReturnCode = "Waiting for command..." # In waiting mode"        
    return redirect('/')
    
# Define the board
@app.route('/set_board', methods=['GET', 'POST'])
def set_board():
    global myBoard
    global theResult
    global theError
    global theReturnCode

    if request.method == 'POST':
        myBoard = request.form['board']
        print("Board set to:[%s]\n" % myBoard)
        theResult = ""
        theError = ""
        theReturnCode = "Waiting for command..." # In waiting mode"        
    return redirect('/')
    
# Define the board
@app.route('/set_option', methods=['GET', 'POST'])
def set_option():
    global myOption
    global theResult
    global theError
    global theReturnCode

    if request.method == 'POST':
        myOption = request.form['option']
        print("Option set to:[%s]\n" % myOption)
        theResult = ""
        theError = ""
        theReturnCode = "Waiting for command..." # In waiting mode"        
    return redirect('/')

# Define temp directory
@app.route('/set_temp_directory', methods=['GET', 'POST'])
def set_set_temp_directory():
    global myTempDirectory
    global theResult
    global theError
    global theReturnCode

    if request.method == 'POST':
        myTempDirectory = request.form['temp_directory']
        print("Temp. directory set to:[%s]\n" % myTempDirectory)
        theResult = ""
        theError = ""
        theReturnCode = "Waiting for command..." # In waiting mode"        
    return redirect('/')

# Define arduino EXE to launch
@app.route('/set_arduino_exe', methods=['GET', 'POST'])
def set_set_arduino_exe():
    global myArduinoExe
    global theResult
    global theError
    global theReturnCode

    if request.method == 'POST':
        myArduinoToolPath = request.form['arduino_tool_path']
        print("Arduino tool path set to:[%s]\n" % myArduinoToolPath)
        myArduinoUploadExe = request.form['arduino_upload_exe']
        print("Arduino Upload EXE set to:[%s]\n" % myArduinoUploadExe)
        myArduinoCompileExe = request.form['arduino_compile_exe']
        print("Arduino Compile EXE set to:[%s]\n" % myArduinoCompileExe)
        theResult = ""
        theError = ""
        theReturnCode = "Waiting for command..." # In waiting mode"        
    return redirect('/')


# Open the code in the Arduino IDE
@app.route('/openIDE', methods=['GET', 'POST'])
def openIDE():
    global myCmd
    global myFileName
    global compileTime
    global myProc
    global targetList
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     
    
    if request.method == 'POST':
        
        tmp = request.data
#        theCode = tmp.decode(encoding='UTF-8', errors='ignore')
        theCode = tmp.decode(encoding='UTF-8', errors='ignore') + "\n"
        
        theFileName = myTempDirectory + separator + myFileName
        print("The code:\n%s\n" % theCode)
        print("Try to save the code to a local file %s\n" % theFileName)

        # Write the code to a temp file
        try:
            f = open(theFileName, "w", encoding='utf-8', errors='ignore')
            print("Trying...\n")
#        except (OSError, IOError) as err:
        except:
            print("Unable to open file for writing: IOError: %s\n" % sys.exc_info()[0])
        else:
            try:
                print("Writing...\n")
                f.write(theCode)
                print("Code written to %s\n" % theFileName)
#            except  (OSError, IOError) as err:
            except:
                print("Unable to write in the file : %s\n" % sys.exc_info()[0])
            finally:
                f.close()
                print("File closed.\n")


        # arduino --board arduino:avr:nano:cpu=atmega168 --port /dev/ttyACM0 --upload /path/to/sketch/sketch.ino
        compileTime = datetime.datetime.now()
        myCmd = myArduinoPrecommand+myArduinoToolPath + myArduinoCompileExe +" "+myTempDirectory+separator+myFileName
#        myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoCompileExe, myTempDirectory+separator+myFileName]
            
        # Creation of the thread
        thread_1 = RunProcess(myCmd)
        # Launch of the thread
        thread_1.start()
        print("\nProcess called in a separate thread..." )

        
    return render_template('main.html', thePort=myPort, theBoardList=boardList, theBoard=myBoard, theTargetList=targetList, theTarget=myTarget, theOptionList=myOptionList, theOption=myOption, theTempFile=myTempDirectory+separator+myFileName, result=theResult, error=theError)


    
# Main page, and process code compile and upload requests
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global myCmd
    global myFileName
    global compileTime
    global myProc
    global targetList
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     
    
    if request.method == 'POST':
        
#        print("Type de request.data : %s" % type(request.data))
        tmp = request.data
        
#        theCode = tmp.decode(encoding='UTF-8', errors='ignore')
        theCode = tmp.decode(encoding='UTF-8', errors='ignore') + "\n"
#        print("Type detheCode : %s" % type(theCode))
#        theCode = tmp
        theFileName = myTempDirectory + separator + myFileName
        print("The code:\n%s\n" % theCode)


        # Write the code to a temp file
        try:
            f = open(theFileName, "w", encoding='utf-8', errors='ignore')
#            print("Trying...\n")
#        except (OSError, IOError) as err:
        except:
            print("Unable to open file for writing: Error: %s" % sys.exc_info()[0])
        else:
            try:
                print("Writing...")
#                f.write(bytes(theCode, "UTF-8"))
#                f.write((theCode).decode(encoding='UTF-8', errors='ignore'))
                f.write((theCode))
                print("Code written to %s\n" % theFileName)
#            except  (OSError, IOError) as err:
            except:
                print("Unable to write in the file %s. Error : %s" % {theFileName,  sys.exc_info()[0]})
            finally:
                f.close()
                print("File closed.")


        # arduino --board arduino:avr:nano:cpu=atmega168 --port /dev/ttyACM0 --upload /path/to/sketch/sketch.ino
        compileTime = datetime.datetime.now()
#        myCmd = myArduinoToolPath + myArduinoUploadExe +" "+myBoardOptions+" "+myBoard+" "+myTargetOption+" "+myTarget+" "+myOption+" "+myCompileAndUploadOption+" "+myTempDirectory+separator+myFileName
        if myOption == "":
            #myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe, myBoardOptions, myBoard, myTargetOption, myTarget, myCompileAndUploadOption, myTempDirectory+separator+myFileName]

            myCmd = myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe + " " + myBoardOptions + " " +  myBoard + " " +  myTargetOption + " " +  myTarget + " " +  myCompileAndUploadOption + " " +  myTempDirectory+separator+myFileName

        else:
            #myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe, myBoardOptions, myBoard, myTargetOption, myTarget, myOption, myCompileAndUploadOption, myTempDirectory+separator+myFileName]

            myCmd = myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe + " " + myBoardOptions + " " +  myBoard + " " +  myTargetOption + " " +  myTarget + " " +  myOption + " " +  myCompileAndUploadOption + " " +  myTempDirectory+separator+myFileName

        # Clean the result:
#        theResult = "\nCommand: \n" + ' '.join(myCmd) + "\n\nResult:\n"
        theResult = "\nCommand: \n" + ' ' + myCmd + "\n\nResult:\n"

        # Creation of the thread
        thread_1 = RunProcess(myCmd, theResult)
        # Launch of the thread
        thread_1.start()
        print("\nProcess called in a separate thread..." )

    targetList = [""] + serial_ports()
#    print("targetList : %s \n   --> myTarget : %s" % (targetList, myTarget))    
    return render_template('main.html', thePort=myPort, theBoardList=boardList, theBoard=myBoard, theTargetList=targetList, theTarget=myTarget, theOptionList=myOptionList, theOption=myOption, theTempFile=myTempDirectory+separator+myFileName, result=theResult, error=theError)



# Main page, and process code compile and upload requests
@app.route('/compile', methods=['GET', 'POST'])
def compile():
    global myCmd
    global myFileName
    global compileTime
    global myProc
    global targetList
    global theResult
    global theError
    global theReturnCode

    theResult = ""
    theError = ""
    theReturnCode = "Waiting for command..." # In waiting mode"     
    
    if request.method == 'POST':

        tmp = request.data
        
#        theCode = tmp.decode(encoding='UTF-8', errors='ignore')
        theCode = tmp.decode(encoding='UTF-8', errors='ignore') + "\n"
        
        theFileName = myTempDirectory + separator + myFileName
        print("The code:\n%s\n" % theCode)
        print("Try to save the code to a local file %s" % theFileName)

        # Write the code to a temp file
        try:
            f = open(theFileName, "w", encoding='utf-8', errors='ignore')
#            print("Trying...")
#        except (OSError, IOError) as err:
        except:
            print("Unable to open file for writing: Error: %s" % sys.exc_info()[0])
        else:
            try:
                print("Writing...")
                f.write(theCode)
                print("Code written to %s" % theFileName)
#            except  (OSError, IOError) as err:
            except:
                print("Unable to write in the file %s. Error : %s" % {theFileName,  sys.exc_info()[0]})
            finally:
                f.close()
                print("File closed.\n")


        # arduino --board arduino:avr:nano:cpu=atmega168 --port /dev/ttyACM0 --upload /path/to/sketch/sketch.ino
        compileTime = datetime.datetime.now()
#        myCmd = myArduinoToolPath + myArduinoCompileExe+" "+myBoardOptions+" "+myBoard+" "+myOption+" "+myCompileOption+" "+myTempDirectory+separator+myFileName
        if myOption == "":
            #myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe, myBoardOptions, myBoard, myCompileOption, myTempDirectory+separator+myFileName]

            myCmd = myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe + " " + myBoardOptions + " " + myBoard + " " + myCompileOption + " " + myTempDirectory+separator+myFileName
        else:
            #myCmd = [myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe, myBoardOptions, myBoard, myOption, myCompileOption, myTempDirectory+separator+myFileName]
            myCmd = myArduinoPrecommand+myArduinoToolPath+myArduinoUploadExe + " " + myBoardOptions + " " + myBoard + " " + myOption + " " + myCompileOption + " " + myTempDirectory+separator+myFileName
        
        # Creation of the thread
        thread_1 = RunProcess(myCmd)
        # Launch of the thread
        thread_1.start()
        print("\nProcess called in a separate thread..." )
   
    targetList = [""] + serial_ports()
#    print("targetList : %s \n   --> myTarget : %s" % (targetList, myTarget))    
    return render_template('main.html', thePort=myPort, theBoardList=boardList, theBoard=myBoard, theTargetList=targetList, theTarget=myTarget, theOptionList=myOptionList, theOption=myOption, theTempFile=myTempDirectory+separator+myFileName, result=theResult, error=theError)


    
@app.route('/get_result')
def get_result():
    global theResult
    global theError
    global compileTime
    global theReturnCode
    global myProc

    theTime = datetime.datetime.now()
    return jsonify(date=theTime.strftime("%A %d %B %Y %H:%M:%S"),  compileTime =  compileTime.strftime("%A %d %B %Y %H:%M:%S"), result=theResult,  error = theError, returnCode=theReturnCode)



    
def flaskrun(default_host="127.0.0.1", 
                  default_port=myPort):
    """
    Takes a flask.Flask instance and runs it. Parses 
    command-line flags to configure the app.
    """
    global myTarget
    global targetList
    global myBoard
    global boardList
    global myOption    
    global myOptionList
    global myArduinoToolPath
    global myArduinoUploadExe
    global myArduinoPrecommand
    global myArduinoCompileExe
    global debugMode
    global myTempDirectory
    global app
    global version

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help="Hostname of the rDuino_Uploader_Server app " + \
                           "[default : %s]" % default_host,
                      default=default_host)
    parser.add_option("-P", "--port",
                      help="Ethernet port for the rDuino_Uploader_Server app " + \
                           "[default : %s]" % default_port,
                      default=default_port)
    parser.add_option("-D", "--device",
                      help="Address of the target to be programmed : " + str(targetList).strip('[]')+ \
                           "[default : %s]" % myTarget,
                      default=myTarget)
    parser.add_option("-B", "--board",
                      help="The type of board to be programmed : " + str(boardList).strip('[]')+ \
                           "[default : %s]" % myBoard,
                      default=myBoard)
    parser.add_option("-O", "--option",
                      help="Options to be used for programming and uploading the code : " + str(myOptionList).strip('[]')+ \
                           "[default : %s]" % myOption,
                      default=myOption)
    parser.add_option("-T", "--tool-path",
                      help="path of the Arduino tools : " + \
                           "[default : %s]" % myArduinoToolPath,
                      default=myArduinoToolPath)
    parser.add_option("-U", "--upload-exec",
                      help="exec to be launched to compile and program the target : " + \
                           "[default : %s]" % myArduinoUploadExe,
                      default=myArduinoUploadExe)
    parser.add_option("-C", "--compile-exec",
                      help="exec to be launched to open the Arduino IDE : " + \
                           "[default : %s]" % myArduinoCompileExe,
                      default=myArduinoCompileExe)
                      #parser.add_option("-d", "--debug",
    #                  help="Debug mode of Falsk. Do not use in production... : " + \
    #                       "[default : %s]" % debugMode,
    #                  default=debugMode)

    # Two options useful for debugging purposes, but 
    # a bit dangerous so not exposed in the help message.
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()
    
    #print("%s" % options)
    myTarget = options.device
    myBoard = options.board
    myOption = options.option
    myArduinoToolPath = options.tool_path
    myArduinoUploadExe = options.upload_exec
    myArduinoCompileExe = options.compile_exec

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if options.profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                       restrictions=[30])
        options.debug = True

    print("\nThe Arduino Uploader server will run with the following options and parameters :\n")
    print("   Version             : %s" % version)
    print("   Host                : %s" % options.host)
    print("   Port                : %s" % options.port)
    print("   USB port            : %s" % myTarget)
    print("   Board               : %s" % myBoard)
    print("   Option              : %s" % myOption)
    print("   Pre-Exec            : %s" % myArduinoPrecommand)
    print("   Exec path           : %s" % myArduinoToolPath)
    print("   Compile Exec        : %s" % myArduinoCompileExe)
    print("   Upload Exec         : %s" % myArduinoUploadExe)
    print("   INO temp Directory  : %s" % myTempDirectory)
    print("   Filename            : %s" % myFileName)
    print("   separator           : %s" % separator)
    print("\n")

    #app.config['DEBUG'] = True
    
    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
    # Start the main server
    #app.run(port=myPort)    

if __name__ == '__main__':
    #global app
    
    # Create the temp file directory if needed
    if not(os.path.isdir(myTempDirectory)):
        os.system("mkdir "+myTempDirectory)
    
    # Start the main server
    flaskrun()



