import os
import time
import paho.mqtt.client as mqtt

class SPLmqtt():
    def on_connect(client, userdata, flags, rc):
        if rc ==0:
            print("Connected successfully")
        else:
            print("Connect return result code: " + str(rc))
    
    # Create the client
    client =mqtt.Client()
    client.on_connect = on_connect

    # Enable TLS
    # client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

    # Set username and password
    # client.username_pw_set("USERNAME", "PASSWORD")

    # Connect to MQTT Broker
    client.connect("MQTT_BROKER", 1884)