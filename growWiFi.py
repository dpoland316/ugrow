''' This is the module which handles the Wifi Connection '''
import network
import credentialManager
from utime import sleep

def connectWiFi():
    
    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        sta_if.active(True)
        networksFound = [x[0] for x in sta_if.scan()] # grab first element from a list of tuples
        print("Networks Found: " + str(networksFound))
        
        for loc in credentialManager.LOCATIONS:
            SSID = bytes(credentialManager.wifiConfig.getSSID(loc), 'UTF-8') # get WiFi network SSID
            
            found = SSID in networksFound
            print('Checking if ' + credentialManager.wifiConfig.getSSID(loc) + ' network found... ' + str(found))
            if found: # check if we can detect the network
                print('Connecting to ' + str(SSID) + '...')

                sta_if.connect(credentialManager.wifiConfig.getSSID(loc),
                               credentialManager.wifiConfig.getSSIDPwd(loc))
                break
        
        for x in range(5):
            if sta_if.isconnected():
                print('Network config:', sta_if.ifconfig())
                break
            else:
                sleep(0.5)
    