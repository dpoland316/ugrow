import c8yMqtt
import gc
import machine
import utime
import ntptime
import network
import uasyncio as asyncio
import growPinConfig
import credentialManager3
import growWiFi
import growSensors
import growLED
gc.collect()

#machine.freq(160000000) # turn the clock speed up to 11
growLED.init() # set pin output and turn off

print('Device ID is {}'.format(credentialManager3.growDevice.getDeviceInfo[DeviceID]))
print ('ESP8266 Diagnostics -- allocated memory BEFORE GC: {} memory free: {}'.format(gc.mem_alloc(), gc.mem_free()))
gc.collect()
print ('ESP8266 Diagnostics -- allocated memory AFTER GC: {} memory free: {}'.format(gc.mem_alloc(), gc.mem_free()))
utime.sleep(2)


def c8yCallback(topic, msg): # define callback for actions coming from cumulocity
    msg=msg.decode("UTF-8")
    print("Callback executed. Message received on topic '{}', message: '{}'".format(topic, msg))
    
    '''
    Messages received from cumulocity typically have the following format:
    <template>,<c8Y_Fragment>,<arguments>
    
    For example:
    510,DeviceSerial                  --  Restarts Device
    511,DeviceSerial,SET LED BLUE     -- Executes command
    
    Processing consists of parsing the initial header (template) values, then 
    parsing the command arguments if applicable.
    '''
    
    #Parse header/template values
    parsedMsg = msg.split(",",3)
    if len(parsedMsg) == 3:
        template, fragment, cmd = [i for i in parsedMsg]
    elif len(parsedMsg) == 2:
        template, fragment = [i for i in parsedMsg]
        cmd = None
    else:
        template = parsedMsg[0]
        fragment = None
        cmd = None
        
    print("Template: '{}' Fragment: '{}' Command: '{}'".format(template, fragment, cmd))
    
    
    # Perform function based on template received
    if template == str(c8yMqtt.TEMPLATE_EXEC_RESTART):
        print('Restart command received...restarting...')
 
        
        # TODO STOP AND RESTART WIFI ON A RESTART
        
                
        machine.reset();
        
    elif template == str(c8yMqtt.TEMPLATE_EXEC_COMMAND):
        print('Executing requested operation: ')
        runCommand(cmd)
        
    elif template == str(c8yMqtt.TEMPLATE_EXEC_CONFIG):
        print("Configuration action requested... doing something vaguely configish")
    else:
        print("Unknown operation requested... ignoring")

def runCommand(cmd):
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

async def measureTempAndHumidity():
    while True:
        await asyncio.sleep(2) # pause and release resources for 2 secs
        tah = growSensors.getTempAndHumidity()
        if credentialManager3.debug.getTaskDebug(): print('{} -- Temp and Humidity: {}'.format(utime.localtime(), tah))
        c8y.publishTemp(tah.get("temp"))
        c8y.sendHumidity(tah.get("humidity"))
    

async def measureLight():
    while True:
        await asyncio.sleep(1) # pause and release resources
        lux = growSensors.getLight()
        if credentialManager3.debug.getTaskDebug(): print('{} -- Light: {}'.format(utime.localtime(), lux))
        c8y.sendLight(lux)
    
    
async def checkMsgs():
    while True:
        await asyncio.sleep(1) # pause and release resources
        c8yHack.check_msg()

async def setTime():
    # RTC clock is notorously bad on ESP8266, so time needs to be resync'ed often
    # Additionally there is a known buffer overflow issue every 7:45 min, unless
    # time() is called. So this method fixes those.
    while True:
        before = gc.mem_free()
        gc.collect()
        after = gc.mem_free()
        print ('{} -- ESP8266 Diagnostics -- Runnning gc. Free memory before GC: {}, free memory after GC: {}'
               .format(utime.localtime(), before, after))
        
        try:
            ntptime.settime()
            if credentialManager3.debug.getTaskDebug(): print('Time synchronized to GMT: {}'.format(utime.localtime()))
            utime.localtime() # needed to prevent overflow
        except OSError as ose:
            print("Caught OS Error from setTime: {}".format(ose))
        finally:
            await asyncio.sleep(5 * 60) # pause and release resources

async def test(msg, n):
    while True:
        print(str(utime.localtime()) + msg)
        #print("MQTT Ping: " + str(c8y.ping()))
        await asyncio.sleep(n)

async def checkWiFi():  
    while sta_if.isconnected():
        growLED.ledControl(growPinConfig.WIFIPIN, 'on')
        await asyncio.sleep_ms(100)
        
async def checkMqtt():  
    while True:
        await asyncio.sleep_ms(250)
        if not c8y.isconnected():      # MQTT not connected
            if sta_if.isconnected():   # WiFi is connected
                connectMqtt()          # reconnect 

def runAsyncTasks():
    print('Starting async tasks...')
    loop = asyncio.get_event_loop()
    loop.create_task(measureTempAndHumidity()) 
    loop.create_task(measureLight()) 
    loop.create_task(setTime())
    #loop.create_task(test("Testing...", 1))
    loop.create_task(checkMsgs())
    #loop.create_task(checkWiFi())
    #loop.run_forever()
    loop.run_until_complete(checkWiFi())

def reconnectWifi():
    print('Wifi disconnected. Attempting to reconnect...')
    sta_if.disconnect()
    growLED.ledControl(growPinConfig.WIFIPIN, 'off')
    while not sta_if.isconnected():
        growWiFi.connectWiFi()
        utime.sleep(1)

def connectMqtt():
    global c8y
    global c8yHack
    c8y = c8yMqtt.C8yClient(c8yCallback)
    c8yHack = c8yMqtt.C8ySubscriptionHack(c8yCallback)
    
'''
Main Program Loop(s)
'''

# Establish WiFi
sta_if = network.WLAN(network.STA_IF)
growWiFi.connectWiFi()
connectMqtt()

gc.collect()

while True:
    runAsyncTasks()
    reconnectWifi()
