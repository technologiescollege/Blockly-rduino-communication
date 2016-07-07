## rDuino-Compiler-Uploader-Server##

Description
-----------
This small web server (a webapp), intented to run locally, receives pieces of Arduino code on port 5005, compile it and upload the binary to the target.
This server has been developped to close the gap between Blockly@rduino and the real Arduino target, when CodeBender.cc is not available, or can not be used.

Usage
-----
Run the server on the local machine, using python, as root.

    ./uploader.py

Build your code in Blockly@reduino
When ready, click on the button:
"`Paste to arduino IDE`"

At this time, an HTTP request with the code is sent to 
http://127.0.0.1:5005/

The server get the code, prepare a shell command, and run it in order to have the code compiled, linked and uploaded to the target.

Here is a screen dump of an example of this process, with the "blink LED" example of Blockly@rDuino:

    $ sudo ./uploader.py 
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




