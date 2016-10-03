## rDuino-Compiler-Uploader-Server##

Description
-----------
This small web server (a webapp), intented to run locally, receives pieces of Arduino code on port 5005, compile it and upload the binary to the target.
This server has been developped to close the gap between Blockly@rduino and the real Arduino target, when CodeBender.cc is not available, or can not be used.

Usage
-----
Run the server on the local machine, using python, as root.

    ./rDuino_uploader_server.py

Build your code in Blockly@reduino
When ready, click on the button:
"`Paste to arduino IDE`"

At this time, an HTTP request with the code is sent to 
http://127.0.0.1:5005/

The server get the code, prepare a shell command, and run it in order to have the code compiled, linked and uploaded to the target.

Here is a screen dump of an example of this process, with the "blink LED" example of Blockly@rDuino:

    $ sudo ./run_server.py 
    * Running on http://127.0.0.1:888/ (Press CTRL+C to quit)
    
    The code: 
    
    void setup() {
      pinMode(13, OUTPUT);
    }
    
    void loop() {
      digitalWrite(13, HIGH);
      delay(100);
      digitalWrite(13, LOW);
      delay(300);    }
    
    The shell command:
    
    arduino --board arduino:avr:uno --port /dev/ttyUSB0  --upload /tmp/uploaded_file/uploaded_file.ino
    
    The output of the compiler-linker-uploader:
    
    Picked up JAVA_TOOL_OPTIONS: 
    Loading configuration...
    Initialisation des paquets...
    Préparation des cartes
    Vérification et envoi...
    
    Le croquis utilise 1 066 octets (3%) de l'espace de stockage de programmes. Le maximum est de 32 256 octets.
    Les variables globales utilisent 9 octets (0%) de mémoire dynamique, ce qui laisse 2 039 octets pour les variables locales. Le maximum est de 2 048 octets.
    0
    
    Done.
    
    127.0.0.1 - - [10/May/2016 23:03:59] "POST / HTTP/1.1" 200 -

The services provided by this server are the following:

    - 127.0.0.1/set_target : Set the USB port

    - 127.0.0.1/set_board : set the type of Arduino board

    - 127.0.0.1/set_option : Set the Verbose options

    - 127.0.0.1/upload : To compile and upload te code into the Arduino board

    - 127.0.0.1/get_result : To get the result of the compile and upload phases

    - 127.0.0.1/get_error : To get the errors

    - 127.0.01/openIDE : To open the code in the Arduino IDE

    - 127.0.0.1/ : To display the main page


Options
-------
rDuino_uploader_server can be run with the following options:

    $ ./rDuino_uploader_server.py  --help
    Usage: rDuino_uploader_server.py [options]

    Options:
    -h, --help            show this help message and exit
    -H HOST, --host=HOST  Hostname of the rDuino_Uploader_Server app [default
                            127.0.0.1]
    -P PORT, --port=PORT  Ethernet port for the rDuino_Uploader_Server app
                            [default 5005]
    -D DEVICE, --device=DEVICE
                            Address of the target to be programmed :
                            '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2',
                            '/dev/ttyUSB3', '/dev/ttyACM0', '/dev/ttyACM1',
                            '/dev/ttyACM2', '/dev/ttyACM3'[default /dev/ttyUSB0]
    -B BOARD, --board=BOARD
                            The type of board to be programmed :
                            'arduino:avr:uno', 'arduino:avr:mega'[default
                            arduino:avr:uno]
    -O OPTION, --option=OPTION
                            Options to be used for programming and uploading the
                            code : '', '--verbose-upload', '--verbose-build', '--
                            verbose', '--preserve-temp-files'[default ]
    -E EXEC, --exec=EXEC  path and exec to be launched to compile and program
                        the target : [default : export DISPLAY=:0.0 && arduino]

example:

    ./rDuino_uploader_server.py -D /dev/ttyUSB3 -P 5555 -B arduino:avr:mega -O --verbose-upload

