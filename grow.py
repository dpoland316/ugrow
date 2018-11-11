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

print('Device ID is {}'.format(growConfig.growDevice.getDeviceInfo()['DeviceID']))
print ('ESP8266 Diagnostics -- allocated memory BEFORE GC: {} memory free: {}'.format(gc.mem_alloc(), gc.mem_free()))
gc.collect()
print ('ESP8266 Diagnostics -- allocated memory AFTER GC: {} memory free: {}'.format(gc.mem_alloc(), gc.mem_free()))
utime.sleep(2)


def c8yCallback(topic, msg): # define callback for actions coming from cumulocity
    msg=msg.decode("UTF-8")
    print("Callback executed. Message received on topic '{}', message: '{}'".format(topic, msg))
    
    '''
    Messages received from cumulocity typically have the following format:
    <template>,<c8Y_Fragment>,<payload>
    
    For example:
    510,DeviceSerial                   --  Restarts Device
    511,DeviceSerial,SET LED BLUE      -- Executes command
    513,DeviceSerial,"val1=1\nval2=2" -- Updates device configuration
    
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
            template, fragment, payload = [i for i in parsedMsg]
        elif len(parsedMsg) == 2:
            template, fragment = [i for i in parsedMsg]
            payload = None
        else:
            template = parsedMsg[0]
            fragment = None
            payload = None
        
        gc.collect()
            
        print("Template: '{}' Fragment: '{}' Payload: '{}'".format(template, fragment, payload))
        if growConfig.debug.getC8yDebug():
            print ('Sending task executing operation')
        
        c8y.sendOperationExecuting('executing', fragment)
        
        if growConfig.debug.getC8yDebug():
            print ('Sent task executing operation')
            
        # Perform function based on template received
        if template == str(c8yMqtt.TEMPLATE_EXEC_RESTART):
            print('Restart command received...restarting...')
            growWiFi.disconnectWiFi() # search thru WiFi config on restart, 
                                      # instead of only connecting to last network
            growWiFi.connectWiFi()    # refresh network connection from configured networks
            machine.reset();
            
        elif template == str(c8yMqtt.TEMPLATE_EXEC_COMMAND):
            print('Executing requested operation: ')
            runCommand(fragment, payload)
            
        elif template == str(c8yMqtt.TEMPLATE_EXEC_CONFIG):
            print("Update configuration action requested...")
            gc.collect()
            
            gcm = growConfig.growConfigManager.getInstance()
            success, message = gcm.saveConfig(payload)
            
            if growConfig.debug.getC8yDebug():
                print('Update Config results -- updated: {} -- message: {}'.format(success, message))          
            
            if success:{
                # send successful message
                c8y.sendOperationExecuting('success', fragment)
                }
            else:
                c8y.sendOperationExecuting('error', fragment, message)
        else:
            print("Unknown operation requested... ignoring")
            if growConfig.debug.getC8yDebug():
                print ('Sending task error operation')
            c8y.sendOperationExecuting('error', fragment, 'Unknown operation requested.')
            if growConfig.debug.getC8yDebug():
                print ('Sent task executing operation')
    
    except Exception as e:
        import sys
        c8y.sendOperationExecuting('error', 'c8y_GrowOperation', 'Invalid message format or unknown operation requested.')
        print ('Exception occured in callback: {}'.format(sys.print_exception(e)))

        
def runCommand(fragment, cmd):
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

    if action.lower() == "set":
        if target.lower() == "led":
            if args.lower() in (growPinConfig.COLORS):
                growLED.pulse(args)
                c8y.sendOperationExecuting('success', fragment)
    elif action.lower() == "get":
        if target.lower() == "config":
            gcm = growConfig.growConfigManager.getInstance()
            c8y.sendOperationExecuting('success', fragment, gcm.getConfig())
    else:
        c8y.sendOperationExecuting('error', fragment, 'Command not supported')
        
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
        lux = growSensors.getLight()
        if growConfig.debug.getTaskDebug(): print('{} -- Light: {}'.format(utime.localtime(), lux))
        c8y.sendLight(lux)
    
    
async def checkMsgs():
    while True:
        await asyncio.sleep(1) # pause and release resources
        c8yHack.check_msg()

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
            await asyncio.sleep(5 * 60) # pause and release resources

async def test(msg, n):
    while True:
        print(str(utime.localtime()) + msg)
        await asyncio.sleep(n)

async def checkWiFi():  
    while growWiFi.isConnected():
        growLED.ledControl(growPinConfig.WIFIPIN, 'on')
        await asyncio.sleep_ms(100)
        
async def checkMqtt():  
    while True:
        await asyncio.sleep_ms(250)
        if not c8y.isconnected():       # MQTT not connected
            if growWiFi.isConnected():  # WiFi is connected
                connectMqtt()           # reconnect 

def runAsyncTasks():
    print('Starting async tasks...')
    loop = asyncio.get_event_loop()
    loop.create_task(measureTempAndHumidity()) 
    loop.create_task(measureLight()) 
    loop.create_task(setTime())
    #loop.create_task(test("Testing...", 1))
    loop.create_task(checkMsgs())
    #loop.run_forever()
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
    connectMqtt()
    
    gc.collect()
    
    while True:
        runAsyncTasks()
        reconnectWifi()