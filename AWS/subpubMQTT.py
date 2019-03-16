#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time, binascii

mqttClients = {}

def c8yConnect(credentials_b64, reconnect=False):
    global mqttClients
    credentials = binascii.a2b_base64(credentials_b64).decode('UTF-8')
    parsedCredentials = credentials.split(",",4)          
    c8y_url, c8y_port, clientID, user, passwd = [c for c in parsedCredentials]

    
    c8yClient = mqtt.Client(client_id=clientID)
    c8yClient.username_pw_set(user, passwd)
    c8yClient.user_data_set(clientID)
    c8yClient.on_message = on_c8y_message
    c8yClient.on_connect = on_c8y_connect
    c8yClient.on_disconnect = on_c8y_disconnect
    c8yClient.on_log = on_log
    
    if (clientID not in mqttClients.keys()) or (reconnect == True):
        print("Connecting to C8Y... with the following values: {}:{}, {}, {}".format(c8y_url, c8y_port, clientID, user))   
        c8yClient.connect(c8y_url, int(c8y_port))
        c8yClient.loop_start()
        c8yClient.subscribe("s/ds", 1) # subscribe to c8y operations
        c8yClient.subscribe("s/e", 1)  # subscribe to c8y error messages
    
    # add connection object to mqttClients list
    mqttClients[clientID] = credentials_b64

def on_grow_message(client, userdata, message):
    print("Received grow request " + str(message.payload))
    if (message.payload.startswith("C8Y_CONN")):
        parsedMsg = message.payload.split(",",1)
   
        if len(parsedMsg) == 2:
            operation, credentials_b64 = [i for i in parsedMsg]
            
            c8yConnect(credentials_b64)
            
            # Below code disabled because C8Y has issues with disconnection errors
            
            #===================================================================
            # if clientID in mqttClients.keys():
            #     print("Resetting stale connection")
            #     mqttConn = mqttClients.pop(clientID)
            #     mqttConn.disconnect()
            #     time.sleep(1)
            #===================================================================
                

            
        else:
            # send back connection error
            print("invalid message format: " + str(message.payload))
            
    elif (message.payload.startswith("C8Y_DISCON")):
        parsedMsg = message.payload.split(",",1)
                
        if len(parsedMsg) == 2:
            operation, client_b64 = [i for i in parsedMsg]
            clientID = binascii.a2b_base64(client_b64).decode('UTF-8')
            
            # Below code disabled because C8Y has issues with disconnection errors
             
            #===================================================================
            # try:
            #     mqttConn = mqttClients.pop(clientID)
            #     print("Disconnect - {} found in MQTT Client list".format(clientID))
            #     
            #     mqttConn.disconnect()
            # except:
            #     print("Disconnect - {} not found in MQTT Client list, ignoring".format(clientID))
            #===================================================================
    
def on_c8y_message(client, userdata, message):
    print("Received C8Y operation {}, publishing locally...".format(message.payload))
    msg_info = localClient.publish(topic=message.topic, payload=message.payload, qos=1)
    if msg_info.is_published() == False:
        msg_info.wait_for_publish()
    print('...sent');

def on_log(client, userdata, level, buf):
    print("paho log: ",buf)

def on_c8y_connect(client, userdata, flags, rc):
    print("Connection returned result: {}".format(rc))
    print("""
            key: 
            0: Connection successful 
            1: Connection refused - incorrect protocol version 
            2: Connection refused - invalid client identifier 
            3: Connection refused - server unavailable 
            4: Connection refused - bad username or password
            5: Connection refused - not authorised
            """)

def on_c8y_disconnect(client, userdata, rc):    
    if rc != 0:
        print("Disconnect requested for ClientID: {0}. RC: {1} -- Unexpected disconnection error.".format(userdata, rc))
        if userdata in mqttClients.keys():
            mqttClientCreds = mqttClients[userdata]
            print("Attempting to reconnect...")
            # mqttClient.reconnect()
            c8yConnect(mqttClientCreds, reconnect=True) 
    else:
        print("Disconnect requested for ClientID: {0}. RC: {1} -- Client {0} disconnected successfully".format(userdata, rc))
        
localClient = mqtt.Client(client_id="growAgent")
localClient.username_pw_set("growiot", "c8yPassthru")
localClient.on_message = on_grow_message
localClient.connect("localhost", 1883)
localClient.loop_start()
localClient.subscribe("c8y/connect")
localClient.loop_forever()
#while True: time.sleep(100)
