# PubSub_Pico
# Program name:  Test105.py
#
#
# This program is written in Python and has been tested on a Raspberry Pi Pico W. 
# It will connect to an internal Node-Red broker (running on a Raspberry Pi 4) via WiFi using the MQTT protocol. 
# Communication is done in both directions (Publish and Subscribe funtions).  
#
# Publish: A button (GPIO17) will initiate an interrupt, which sets a global variable.
# Subscribe: An external LED (GPIO16) will switch on/off depending on a message received from the Node-Red broker. 
# 
# Comments in the program are in German language.
#
#


