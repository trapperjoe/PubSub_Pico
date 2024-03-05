#==========================================================================
#
# 20240304 Test105 V07.py
#
# 1 Taster: button 	(GPIO17 - aktiv LOW)
# 1 LED: LEDext		(GPIO16 mit Vorwiderstand)
#
# onboard LED:
# Z102 * = WLAN Verbindung erfolgreich hergestellt
# Z118 ** = Hauptprogramm startet
# 
#
# 
#
#
#==========================================================================
#
# Bibliotheken laden
import machine
from time import sleep
import network
from simple import MQTTClient

from Zugang_JM import wlanSSID, wlanPW, IP_MQTT_broker

# WLAN-Zugangsdaten und MQTT-Broker-Details
WIFI_SSID = wlanSSID()
WIFI_PASSWORD = wlanPW()
MQTT_BROKER = IP_MQTT_broker()
MQTT_TOPIC_LED = "LED_Control"
MQTT_TOPIC_BUTTON = "Button_State"

# Initialisieren des LED- und Taster-Pins
LEDext = machine.Pin(16, machine.Pin.OUT)
LED = machine.Pin("LED", machine.Pin.OUT)

# Funktion für Blinki (OnboardLED)
def LED_blinkt(Zahl):
 print("LED_blinkt ", Zahl," x")
 for Nummer in range(Zahl):
     LED.value(1);sleep(0.3);LED.value(0);sleep(0.2)
 return 

# Funktion zum Umschalten der LED
def toggle_LEDext(msg):
 if msg == b"1":
     print("Z47 LED einschalten")
     LEDext.value(1)
 elif msg == b"0":
     print("Z50 LED ausschalten")
     LEDext.value(0)

# Definition des Schalters (GPIO17), aktiv=LOW
button = machine.Pin(17,machine.Pin.IN,machine.Pin.PULL_UP)

# Interrupthandler für eine Statusänderung am Schalter
def Button_ISR(pin):          	# Schalter Interrupt handler
    global button_state       	# Bezug zur globalen Variablen
    button.irq(handler=None)  	# Abschalten während der Ausführung
    
    if (button.value() == 1) and (button_state == 0):  # Schalter ist offen (1) und button_state ist 0
        button_state = 1      	# Setze button_state auf 1
        LED.value(0)    		# Schalte onboard LED aus
        #print("***** Schalter offen ***** \r", end='')          
        #publish_message(MQTT_TOPIC_BUTTON, "1")
        
    elif (button.value() == 0) and (button_state == 1): # Schalter ist geschlossen (0) und button_state ist 1
        button_state = 0     	# Setze Status auf 0
        LED.value(1)    		# Schalte onboard LED ein 
        #print("***** Schalter geschlossen ***** \r", end='')
        #publish_message(MQTT_TOPIC_BUTTON, "0")
        
    # Setze den Interrupthandler wieder aktiv
    button.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=Button_ISR)
    return

# Bezug des Schalters zum Interrupthandler
button.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=Button_ISR)

# Funktion zum Veröffentlichen einer Nachricht über MQTT
def publish_message(topic, message):
    try:
        client_pub.publish(topic, message)
        print()
        print("Z85 Message published:", "\n   Topic = ", topic, "\n Message = ", message)
    except Exception as e:
         print("Z87 Error publishing message:", e)

# Funktion, die aufgerufen wird, wenn eine Nachricht empfangen wird
def on_message(topic, msg):
    print("Z91 Message received:", "\n   Topic = ", topic, "\n Message = ", msg)
    toggle_LEDext(msg)
# Hier könnten weitere Aktionen basierend auf der empfangenen Nachricht durchgeführt werden

# Start Hauptprogramm. Verbindung zum WLAN herstellen
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)
while not wifi.isconnected():
    sleep(1)
    Blinki = 1 ;LED_blinkt(Blinki)
print("Z102 * = WLAN Verbindung erfolgreich hergestellt")

# MQTT-Client erstellen (Provider)
client_pub = MQTTClient("pico_pub", MQTT_BROKER)

# Verbindung zum MQTT-Broker herstellen
client_pub.connect()

# MQTT-Client erstellen (Subscriber)
client_sub = MQTTClient("pico_sub", MQTT_BROKER)
client_sub.set_callback(on_message)
client_sub.connect()
client_sub.subscribe(MQTT_TOPIC_LED)

# Hauptprogramm für den Raspberry Pi Pico
Blinki = 2 ;LED_blinkt(Blinki)
print("Z118 ** = Hauptprogramm startet ... \n")

# Setze die Status Variable für den Schalter
button_state = button.value()
print("Button_State = ", button_state, '\n')

counter = 0
try:
    while True:
# Überprüfen von eingehenden MQTT-Nachrichten
        print()
        print("**************", counter, "**********************")
        print("Empfangen...")
        print()

        client_sub.check_msg()
        # Hier können weitere spezifische Aktionen erfolgen
        print("=======================================")
        print("Senden...")
        publish_message(MQTT_TOPIC_BUTTON, str(button_state))
        
        counter += 1
        sleep(1)


except KeyboardInterrupt:
# Saubere Beendigung des Programms, wenn es durch den Benutzer
# unterbrochen wurde (Ctrl-C).
     print("Programm beendet.")
     client_sub.disconnect()
     client_pub.disconnect()
     button.irq(handler=None)
     wifi.disconnect()


