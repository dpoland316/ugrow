import c8yMqtt
import gc
import machine
import utime
import ntptime
import uasyncio as asyncio
import growPinConfig
import growConfig
import growWiFi
import growSensors
import growLED
gc.collect()

#machine.freq(160000000) # turn the clock speed up to 11
growLED.init() # set pin output and turn off

deviceID = growConfig.growDevice.getDeviceInfo()['ModuleSerialNumber']
print('Device ID is {}'.format(deviceID))
print ('ESP8266 Diagnostics -- allocated memory BEFORE GC: {} memory free: {}'.format(gc.mem_alloc(), gc.mem_free()))
gc.collect()
print ('ESP8266 Diagnostics -- allocated memory AFTER GC: {} memory free: {}'.format(gc.mem_alloc(), gc.mem_free()))
utime.sleep(2)
alert=False
triggerRestart=False

def c8yCallback(topic, msg): # define callback for actions coming from cumulocity
    msg=msg.decode("UTF-8")
    print("Callback executed. Message received on topic '{}', message: '{}'".format(topic, msg))
    
    '''
    Messages received from cumulocity typically have the following format:
    <template>,<c8Y_Fragment>,<payload>
    
    For example:
    510,DeviceSerial                   --  Restarts Device
    511,DeviceSerial,SET ALERT ON      -- Executes command
    513,DeviceSerial,"val1=1\nval2=2" -- Updates tgtDevice configuration
    
    Processing consists of parsing the initial header (template) values, then 
    parsing the command arguments if applicable.
    '''
    gc.collect()
    
    try:
        #Parse header/template values
        parsedMsg = msg.split(",",2)
        
        #=======================================================================
        # if growConfig.debug.getC8yDebug():
        #     print('Parsed Msg Length: {}'.format(len(parsedMsg)))
        #     for i, v in enumerate(parsedMsg):
        #         print('Element[{}]: {}'.format(i, v))
        #=======================================================================
        
        if len(parsedMsg) == 3:
            template, tgtDevice, payload = [i for i in parsedMsg]
        elif len(parsedMsg) == 2:
            template, tgtDevice = [i for i in parsedMsg]
            payload = None
        else:
            template = parsedMsg[0]
            tgtDevice = None
            payload = None
        
        template = int(template)
        
        gc.collect()
            
        print("Template: '{}' Device: '{}' Payload: '{}'".format(template, tgtDevice, payload))
        
        if tgtDevice == deviceID:           # filter for operations relating to this device
            if growConfig.debug.getC8yDebug():
                print ('Sending task executing operation')
            
            c8y.sendOperationExecuting('executing', c8yMqtt.TEMPLATE_FRAGMENTS[template])
            
            if growConfig.debug.getC8yDebug():
                print ('Sent task executing operation')
                
            # Perform function based on template received
            
            #===================================================================
            # RESTART DEVICE
            #===================================================================
            global triggerRestart
            if template == c8yMqtt.TEMPLATE_EXEC_RESTART:
                print('Restart command received...restarting...')
                triggerRestart=True # Async trigger of restart, so MQTT event 
                                    # won't be redelivered.
                
            #===================================================================
            # EXECUTE SHELL COMMAND    
            #===================================================================
            elif template == c8yMqtt.TEMPLATE_EXEC_COMMAND:
                print('Executing requested operation: ')
                runCommand(tgtDevice, payload)
            
            
            #===================================================================
            # UPDATE DEVICE CONFIGURATION    
            #===================================================================
            elif template == c8yMqtt.TEMPLATE_EXEC_CONFIG:
                print("Update configuration action requested...")
                gc.collect()
                
                gcm = growConfig.growConfigManager.getInstance()
                
                if growConfig.debug.getC8yDebug():
                    print("Raw config payload: {}".format(payload))
                
                
                # C8Y sends a string with embedded escape sequences. This will remove 
                # extra slashes (i.e. so \"port\" becomes "port")
                formatted_payload = payload.replace(r'\"','"')
                                
                # C8Y also sends everything wrapped in quotations (which is is invalid 
                # for JSON)
                if (formatted_payload[0] == '"'):
                    # Return the string without the enclosing quotations
                    formatted_payload = formatted_payload[1:-1]     
                
                
                if growConfig.debug.getC8yDebug():
                    print("Formatted payload: " + formatted_payload)
                  
                
                success, message = gcm.saveConfig(formatted_payload)
                
                if growConfig.debug.getC8yDebug():
                    print('Update Config results -- updated: {} -- message: {}'.format(success, message))          
                
                if success:{
                    # send successful message
                    c8y.sendOperationExecuting('success', c8yMqtt.TEMPLATE_FRAGMENTS[template])
                    }
                else:
                    c8y.sendOperationExecuting('error', c8yMqtt.TEMPLATE_FRAGMENTS[template], message)
                    
                    
            else:
                print("Unknown operation requested... ignoring")
                if growConfig.debug.getC8yDebug():
                    print ('Sending task error operation')
                c8y.sendOperationExecuting('error', c8yMqtt.TEMPLATE_FRAGMENTS[template], 'Unknown operation requested.')
                if growConfig.debug.getC8yDebug():
                    print ('Sent task executing operation')
        else:
            print("Received operation request for different device (ignoring). Requested serial: {} ... my serial: {})".format(tgtDevice, deviceID))
    except Exception as e:
        import sys
        c8y.sendOperationExecuting('error', c8yMqtt.TEMPLATE_FRAGMENTS[template], 'Invalid message format or unknown operation requested.')
        print ('Exception occured in callback: {}'.format(sys.print_exception(e)))

        
def runCommand(fragment, cmd):
    global alert
    if cmd != None:
        parsedCmd = cmd.split(" ",2)
        if len(parsedCmd) >= 3:
            action, target, args = [d for d in parsedCmd]
        elif len(parsedCmd) == 2:
            action, target = [d for d in parsedCmd]
            args = ''
        else:
            action = parsedCmd[0]
            target, args = ''
        print("Action: '{}' Target: '{}' Args: '{}'".format(action, target, args))
    else:
        print('Invalid command received -- empty content')
        c8y.sendOperationExecuting('error', c8yMqtt.TEMPLATE_FRAGMENTS[c8yMqtt.TEMPLATE_EXEC_COMMAND], 'Invalid command received -- empty content')

    if action.lower() == "set":
        if target.lower() == "alert":
            if args.lower() != 'on':
                alert=False
            else:
                alert=True
                    
            c8y.sendOperationExecuting('success', c8yMqtt.TEMPLATE_FRAGMENTS[c8yMqtt.TEMPLATE_EXEC_COMMAND])
            
    elif action.lower() == "get":
        if target.lower() == "config":
            gcm = growConfig.growConfigManager.getInstance()
            c8y.sendOperationExecuting('success', c8yMqtt.TEMPLATE_FRAGMENTS[c8yMqtt.TEMPLATE_EXEC_COMMAND], '"' + gcm.getConfig() + '"')
    else:
        c8y.sendOperationExecuting('error', c8yMqtt.TEMPLATE_FRAGMENTS[c8yMqtt.TEMPLATE_EXEC_COMMAND], 'Command not supported')
        
async def measureTempAndHumidity():
    while True:
        await asyncio.sleep(2) # pause and release resources for 2 secs
        tah = growSensors.getTempAndHumidity()
        if growConfig.debug.getTaskDebug(): print('{} -- Temp and Humidity: {}'.format(utime.localtime(), tah))
        c8y.publishTemp(tah.get("temp"))
        c8y.sendHumidity(tah.get("humidity"))
    

async def measureLight():
    while True:
        await asyncio.sleep(1) # pause and release resources
        try:
            lux = growSensors.getLight()
            if growConfig.debug.getTaskDebug(): print('{} -- Light: {}'.format(utime.localtime(), lux))
            c8y.sendLight(lux)
        except Exception as e:
            print("Caught error from measureLight: {}".format(e))
            
async def measureSoilMoisture():
    while True:
        await asyncio.sleep(60) # pause and release resources
        try:
            moisture = growSensors.getSoilMoisture()
            if growConfig.debug.getTaskDebug(): print('{} -- Soil: {}%'.format(utime.localtime(), moisture))
            c8y.sendSoilMoisture(moisture)    
        except Exception as e:
            print("Caught error from measureSoilMoisture: {}".format(e))    
    
async def setTime():
    # RTC clock is notorously bad on ESP8266, so time needs to be resync'ed often
    # Additionally there is a known buffer overflow issue every 07:45:00, unless
    # time() is called. So this method fixes those.
    while True:
        before = gc.mem_free()
        gc.collect()
        after = gc.mem_free()
        print ('{} -- ESP8266 Diagnostics -- Runnning gc. Free memory before GC: {}, free memory after GC: {}'
               .format(utime.localtime(), before, after))
        
        try:
            ntptime.settime()
            if growConfig.debug.getTaskDebug(): print('Time synchronized to GMT: {}'.format(utime.localtime()))
            utime.localtime() # needed to prevent overflow
        except OSError as ose:
            print("Caught OS Error from setTime: {}".format(ose))
        finally:
            await asyncio.sleep(5 * 60) # pause and release resou
async def checkWiFi():  
    while growWiFi.isConnected():
        growLED.ledControl(growPinConfig.WIFIPIN, 'on')
        await asyncio.sleep_ms(10)
        
async def checkAlert():  
    while True:
        if growConfig.debug.getTaskDebug(): print('Current alert setting: {}'.format(alert))
        growLED.alert(alert)        
        await asyncio.sleep_ms(2000)
        
async def checkMsgs():
    while True:
        await asyncio.sleep(1)      # pause and release resources
        if growWiFi.isConnected():  # WiFi is connected
            c8yHack.check_msg()

async def checkRestart():
    while True:
        await asyncio.sleep(5)            # pause and release resources
        if triggerRestart == True:        # WiFi is connected
                utime.sleep(2)            # wait for MQTT restart trigger message to be ack'ed
                growWiFi.disconnectWiFi() # search thru WiFi config on restart, 
                                          # instead of only connecting to last network
                growWiFi.connectWiFi()    # refresh network connection from configured networks
                machine.reset();


def runAsyncTasks():
    print('Starting async tasks...')
    loop = asyncio.get_event_loop()
    loop.create_task(measureTempAndHumidity()) 
    loop.create_task(measureLight()) 
    loop.create_task(measureSoilMoisture()) 
    loop.create_task(setTime())
    loop.create_task(checkMsgs())
    loop.create_task(checkAlert())
    loop.create_task(checkRestart())
    loop.run_until_complete(checkWiFi())

def reconnectWifi():
    print('Wifi disconnected. Attempting to reconnect...')
    growWiFi.disconnectWiFi()       # Disabling the interface allows us to manage the
                                    # reconnecting logic, as opposed to losing control to 
                                    # the micropython auto-reconnect process 
    growLED.ledControl(growPinConfig.WIFIPIN, 'off')
    while not growWiFi.isConnected():
        growWiFi.connectWiFi()
        utime.sleep(1)

def connectMqtt():
    global c8y
    global c8yHack
    c8y = c8yMqtt.C8yClient(c8yCallback)
    c8yHack = c8yMqtt.C8ySubscriptionHack(c8yCallback)
    
def runGrow():
    '''
    Main Program Loop(s)
    '''

    # Establish WiFi
    growWiFi.connectWiFi()
    
    while not growWiFi.isConnected():
        utime.sleep(.5)
        
    connectMqtt()
    
    # send "Restart complete" signal. Will be ignored if not applicable.
    c8y.sendOperationExecuting('success', c8yMqtt.TEMPLATE_FRAGMENTS[c8yMqtt.TEMPLATE_EXEC_RESTART])
    
    gc.collect()
    
    while True:
        runAsyncTasks() 
        reconnectWifi() # This only ever gets run if the Wifi signal is lost
