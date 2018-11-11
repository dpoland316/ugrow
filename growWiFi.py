''' This is the module which handles the Wifi Connection '''
import network
import credentialManager3 as cm
from utime import sleep

# Turn off access point interface
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# Turn on station interface
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

def connectWiFi():

    if not sta_if.isconnected():
        sta_if.active(True)
        networksFound = [x[0] for x in sta_if.scan()] # grab first element from a list of tuples
        print("Networks Found: " + str(networksFound))
        
        for loc in cm.wifiConfig.listWiFiLocations():
            SSID = bytes(cm.wifiConfig.getSSID(loc), 'UTF-8') # get WiFi network SSID
            
            found = SSID in networksFound
            print('Checking if ' + cm.wifiConfig.getSSID(loc) + ' network found... ' + str(found))
            if found: # check if we can detect the network
                print('Connecting to ' + str(SSID) + '...')

                sta_if.connect(cm.wifiConfig.getSSID(loc),
                               cm.wifiConfig.getSSIDPwd(loc))
                break
        
        for x in range(5):
            if sta_if.isconnected():
                print('Network config:', sta_if.ifconfig())
                break
            else:
                sleep(0.5)

def checkNetworkFound(ssids):
    networksFound = [x[0] for x in sta_if.scan()] # grab first element from a list of tuples
    print('WiFi Check -- Networks Found: {}'.format(networksFound))
    
    found = False
    ssid = None
    
    for loc in ssids:
        ssid = bytes(loc, 'UTF-8') # convert ssid to bytes
        
        found = ssid in networksFound
        print('WiFi Check -- checking {}... found: {}'.format(ssid, found))
        
        if found:
            break
        
    return found
