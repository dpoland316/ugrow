'''
    Handles the MQTT connection, and associated C8Y services
    
'''
from umqtt.robust import MQTTClient
import growPinConfig
import growConfig
import utime
import ubinascii
from growLED import ledControl, blink

# C8Y Static MQTT Templates
TEMPLATE_CREATE_DEVICE  = 100
TEMPLATE_SET_HW_SERIAL  = 110
TEMPLATE_REGISTER_CMD   = 114
TEMPLATE_SEND_EVENT     = 400
TEMPLATE_CMD_EXECUTING  = 501
TEMPLATE_CMD_FAILED     = 502
TEMPLATE_CMD_FINISHED   = 503
TEMPLATE_EXEC_RESTART   = 510
TEMPLATE_EXEC_COMMAND   = 511
TEMPLATE_EXEC_CONFIG    = 513
TEMPLATE_FRAGMENTS      = {510:"c8y_Restart", 511:"c8y_Command", 513:"c8y_Configuration"}

# C8Y MQTT topics
SENDING_TEMPLATE_TOPIC      = b"s/us"
RECEIVING_TEMPLATE_TOPIC    = b"s/ds"
RECEIVING_ERROR_TOPIC       = b"s/e"

# C8Y Supported Operations
C8Y_OPERATIONS = "c8y_Command,c8y_Configuration,c8y_Restart";

MQTT_QoS    = 1
MQTT_RETAIN = 0

SSL=False # not enough memory to enable

mqtt = growConfig.mqttConfig
growDevice = growConfig.growDevice.getDeviceInfo()
debug = growConfig.debug

# get values from default configured profile
PUB_mqttServer  = mqtt.getMqttServer('pubServer')
PUB_mqttPort    = mqtt.getMqttPort('pubServer')
PUB_mqttUser    = mqtt.getMqttUser('pubServer')
PUB_mqttPwd     = mqtt.getMqttPwd('pubServer')

SUB_mqttServer    = mqtt.getMqttServer('subServer')
SUB_mqttPort      = mqtt.getMqttPort('subServer')
SUB_mqttUser      = mqtt.getMqttUser('subServer')
SUB_mqttPwd       = mqtt.getMqttPwd('subServer')

class C8yClient(MQTTClient):
    
    def __init__(self, callback):
        self.__deviceID = growDevice['ModuleSerialNumber']
        
        super().__init__(self.__deviceID,
                   PUB_mqttServer,
                   PUB_mqttPort,
                   PUB_mqttUser,
                   PUB_mqttPwd,
                   ssl=SSL)
                   #ssl_params={"server_side":False, "cert_reqs":CERT_OPTIONAL})
                   #ssl_params={"cert_reqs":ussl.CERT_NONE, "ca_certs":"/flash/cert/ca.pem"})
        
        self.__connected=False # flag for Mqtt connection status
        self.mqttConnect()
        
        self.__sendDeviceRegistrationInfo()
        self.__sendDeviceSupportedOperations()
        #self.subscribeC8yEvents(callback)
        
    def isConnected(self):
        return self.__connected
        
    def mqttConnect(self):

        # Last will will send this message when connection is lost
        super().set_last_will(SENDING_TEMPLATE_TOPIC,
                             "400,c8y_ConnectionEvent,Device connection was lost.",
                             MQTT_RETAIN,
                             MQTT_QoS)
        print('Connecting to MQTT with: {}@{}:{}'.format(PUB_mqttUser, PUB_mqttServer, PUB_mqttPort))
        try:
            super().connect(clean_session=False)
            print('Connected!')
            ledControl(growPinConfig.MQTTPIN, 'on')
            self.__connected=True
            
        except Exception as e:
            print('Connecting to MQTT server failed: ' + str(e))
            ledControl(growPinConfig.MQTTPIN, 'off') # change to pulse?
            self.__connected=False
            raise e
        
    
    @staticmethod    
    def constructC8YMessage(template, *payload):
        msg = str(template) + ',' + ','.join(payload) # return CSV*payload
        return msg
        
    def publish(self, message, topic=SENDING_TEMPLATE_TOPIC):
        try:
            if self.isConnected():
                super().publish(topic, bytes(message, 'UTF-8'))
                blink(growPinConfig.MONITORPIN) # signal data sent
        except Exception as e:
            print('Publishing to MQTT server failed: {}'.format(e))
            ledControl(growPinConfig.MQTTPIN, 'off')
            self.__connected = False

    def __sendDeviceRegistrationInfo(self):
        print("Preparing device registration Info")
        deviceCreationMsg = self.constructC8YMessage(TEMPLATE_CREATE_DEVICE,
                                                     'Grow_' + self.__deviceID,
                                                     'c8y_MQTTdevice')
        deviceHardwareMsg = self.constructC8YMessage(TEMPLATE_SET_HW_SERIAL,
                                                     growDevice['ModuleSerialNumber'],
                                                     growDevice['ModuleName'],
                                                     growDevice['ModuleRevision'])
        deviceConnectedEvt = self.constructC8YMessage(TEMPLATE_SEND_EVENT,
                                                      'c8y_ConnectionEvent',
                                                      'Device connected.')
 
        if (growConfig.debug.getC8yDebug()):
            print("C8y Device creation sent: {}".format(deviceCreationMsg))
            print("C8y Device hardware sent: {}".format(deviceHardwareMsg))
            print("Connection Event sent: {}".format(deviceConnectedEvt))
            
        self.publish(deviceCreationMsg)
        self.publish(deviceHardwareMsg)
        self.publish(deviceConnectedEvt)
        
        print("Done sending!")

    def __sendDeviceSupportedOperations(self):
        deviceOperations = self.constructC8YMessage(TEMPLATE_REGISTER_CMD, C8Y_OPERATIONS)
        self.publish(deviceOperations)
        
    def subscribeC8yEvents(self, callback):
        print("Starting subscription with callback {}".format(callback))
        super().set_callback(callback)
        print('set cb')
        super().subscribe(RECEIVING_TEMPLATE_TOPIC, qos=MQTT_QoS)
        print('Subscribed to topic {}'.format(RECEIVING_TEMPLATE_TOPIC))
        super().subscribe(RECEIVING_ERROR_TOPIC, qos=MQTT_QoS)
        print('Subscribed to topic {}'.format(RECEIVING_ERROR_TOPIC))
        

    def publishTemp(self, temp):
        mesg = self.constructC8YMessage(200, 'c8y_TemperatureSensor', 'T', str(temp), 'C')
        
        if debug.getC8yDebug():
            print('{} -- {}{}'.format(utime.localtime(), SENDING_TEMPLATE_TOPIC, bytes(mesg, 'UTF-8')))
        
        self.publish(mesg)
        

    def sendHumidity(self, humidity):
        mesg = self.constructC8YMessage(200, 'c8y_HumiditySensor', 'h', str(humidity), '%RH')
        
        if debug.getC8yDebug():
            print('{} -- {}{}'.format(utime.localtime(), SENDING_TEMPLATE_TOPIC, bytes(mesg, 'UTF-8')))
        
        self.publish(mesg)


    def sendLight(self, lux):
        mesg = self.constructC8YMessage(200, 'c8y_LightSensor', 'e', str(lux), 'lux')
        
        if debug.getC8yDebug():
            print('{} -- {}{}'.format(utime.localtime(), SENDING_TEMPLATE_TOPIC, bytes(mesg, 'UTF-8')))
        
        self.publish(mesg)
        
    def sendSoilMoisture(self, moisture):
        mesg = self.constructC8YMessage(200, 'c8y_MoistureSensor', 'moisture', str(moisture), '%')
        
        if debug.getC8yDebug():
            print('{} -- {}{}'.format(utime.localtime(), SENDING_TEMPLATE_TOPIC, bytes(mesg, 'UTF-8')))
        
        self.publish(mesg)
    
    def sendOperationExecuting(self, status, fragment, message=None):
        msgTemplate = None
        if status in ('executing', 'error', 'success'):
            if status == 'executing':
                msgTemplate = TEMPLATE_CMD_EXECUTING
            elif status == 'error':
                msgTemplate = TEMPLATE_CMD_FAILED
            elif status == 'success':
                msgTemplate = TEMPLATE_CMD_FINISHED
        else: 
            raise NotImplementedError("Status must be either 'executing, ' error' or 'success'")
        
        if message == None:
            mesg = self.constructC8YMessage(msgTemplate, fragment)
        else:
            mesg = self.constructC8YMessage(msgTemplate, fragment, message)
        
        if debug.getC8yDebug():
            print('{} -- {}{}'.format(utime.localtime(), SENDING_TEMPLATE_TOPIC, bytes(mesg, 'UTF-8')))
        
        self.publish(mesg)    
        
        
class C8ySubscriptionHack(MQTTClient):
    # C8y subscriptions aren't working, so need to use a different provider.
    def __init__(self, callback):
        self.__deviceID = growDevice['ModuleSerialNumber']
        
        super().__init__(self.__deviceID,
                   SUB_mqttServer,
                   SUB_mqttPort,
                   SUB_mqttUser,
                   SUB_mqttPwd,
                   ssl=SSL)
                   #ssl_params={"server_side":False, "cert_reqs":CERT_OPTIONAL})
                   #ssl_params={"cert_reqs":ussl.CERT_NONE, "ca_certs":"/flash/cert/ca.pem"})
        
        self.mqttConnect()                  # Connect to intermediate MQTT server for subscribing
        self.subscribeC8YDevice()           # Send creds for growAgent to connect to C8Y   
        self.subscribeC8yEvents(callback)   # Subscribe to intermediate MQTT server topics
        
    def subscribeC8yEvents(self, callback):
        print("SUB -- Starting subscription with callback {}".format(callback))
        super().set_callback(callback)
        print('SUB -- Set callback')

        super().subscribe(RECEIVING_TEMPLATE_TOPIC, qos=MQTT_QoS)
        print('SUB -- Subscribed to topic {}'.format(RECEIVING_TEMPLATE_TOPIC))
        super().subscribe(RECEIVING_ERROR_TOPIC, qos=MQTT_QoS)
        print('SUB -- Subscribed to topic {}'.format(RECEIVING_ERROR_TOPIC))
        
    def mqttConnect(self):
        
        # Set last will to send notification when disconnect occurs
        b64_clientID = ubinascii.b2a_base64(self.__deviceID.encode('UTF-8')).decode('UTF-8')               
        message="C8Y_DISCON," + b64_clientID
        
        # Last will will send this message when connection is lost
        super().set_last_will("c8y/connect",
                             message,
                             MQTT_RETAIN,
                             MQTT_QoS)
        print('Connecting to MQTT with: {}@{}:{}'.format(SUB_mqttUser, SUB_mqttServer, SUB_mqttPort))
        super().connect(clean_session=False)
        print('Connected!')
    
    def subscribeC8YDevice(self):
        try:
            # encode the c8y credentials as base 64
            connPayload=(PUB_mqttServer +',' + str(PUB_mqttPort) +',' + self.__deviceID 
                         +',' + PUB_mqttUser +',' + PUB_mqttPwd).encode('UTF-8')
            b64_payload = ubinascii.b2a_base64(connPayload).decode('UTF-8')               
            message="C8Y_CONN," + b64_payload

            super().publish("c8y/connect", bytes(message, 'UTF-8'))
            blink(growPinConfig.MONITORPIN) # signal data sent
            
        except Exception as e:
            print('Publishing to SUB MQTT server failed: {}'.format(e))
            ledControl(growPinConfig.MQTTPIN, 'off')
            self.__connected = False
        
        
        