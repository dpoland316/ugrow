import os
import ujson
import network
import ubinascii
import growInitialJsonConfig

cfgFile = 'config.json'

class growConfigManager():
    __instance = None
    
    @staticmethod
    def getInstance():
        """ Static access method. """
        if growConfigManager.__instance == None:
            growConfigManager()
        return growConfigManager.__instance
  
    def __init__(self):
        """ Virtually private constructor. """
        if growConfigManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            growConfigManager.__instance = self

        self.dict = {}
        
        files = os.listdir('/')
        if not cfgFile in files:
            # config file doesn't exist, so create default initial entry
            
            '''
                Initial Json must have a format like this:
                  {
                  "WiFiDefault": "home",
                  "WiFiLocations": [ 
                        { "Location1": { "ssid": "home_ssid", "password": "foo" } },
                        { "location2": { "ssid": "away_ssid", "password": "bar" } }
                      ],
                  "MQTTDefault": "provider1"
                  "MQTTLocations": [
                        { "pubServer": {
                            "server": "server1", "port": 1883,
                            "user": "joe, "password": "horses" } 
                        },
                        { "subServer": {
                            "server": "server2", "port": 14273,
                            "user": "sally", "password": "rainbows" }
                        } ]
                  "Device": {
                        "DeviceID": "1A2S3DFCX5434",
                        "ModuleName": "Grow Module v0.5,0.0.3",
                        "ModuleSerialNumber": "1234554322",
                        "ModuleRevision": "0.0.1",
                        "ConfigurationVersion": "0.3"  }
                  "Debug": {
                        "sensorDebug": false,
                        "c8yDebug": false,
                        "taskDebug": false   }  
                  }
            '''
            print('No config file found... initializing...')
            self.dict = ujson.loads(growInitialJsonConfig.initialConfig) # get init json file
            
            # init SerialNumber
            mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
            mac = mac.replace(':', '').upper()
            
            self.dict['Device']['ModuleSerialNumber'] = mac
         
            with open(cfgFile, 'w') as f:
                # dump initial config to file
                f.write(ujson.dumps(self.dict))
                
        else:
            self.getConfig(True)
    
    def getConfig(self, reload=False):
        if reload:
            with open(cfgFile, 'r+') as f:
                # dump initial config to file
                print('Loading config file...')
                self.dict = ujson.loads(f.read())
            
        return ujson.dumps(self.dict)
    
    def saveConfig(self, dictJson):
        import growWiFi
        try:
            print("Saving new configuration: {}".format(dictJson))
            tempDict=ujson.loads(dictJson)
            
            ssids = list()
            for loc in tempDict['WiFiLocations']:
                for key in loc.keys():
                    ssids.append(loc[key]['ssid'])
            
            print("ssids: {}".format(ssids))
            
            # check if any configured WiFi's are found beofre saving (validate WiFi config)
            if growWiFi.checkNetworkFound(ssids):
                self.dict = tempDict
                with open(cfgFile, 'w') as f:
                    # dump new config to file
                    f.write(ujson.dumps(self.dict))   
                return (True, None)
            else:
                return (False, 'No networks matching configured WiFi SSIDs were found during scan.')
            
        except ValueError:
            return (False, 'Invalid JSON')
        except Exception as e:
            return (False, str(e))
    
            
class wifiConfig:
    def printDict(): 
        gcm = growConfigManager.getInstance()          
        print(gcm.dict)
        
    def listWiFiLocations():
        gcm = growConfigManager.getInstance()
        locs = list()
        for loc in gcm.dict['WiFiLocations']:
            for key in loc.keys():
                locs.append(key)
        return locs
        
    def getSSID(location = None): 
        gcm = growConfigManager.getInstance()
        
        if location == None: # get default
            location = gcm.dict['WiFiDefault']
        
        for loc in gcm.dict['WiFiLocations']:
            for key in loc.keys():
                if key == location:
                    return loc[key]['ssid']
                    
    def getSSIDPwd(location = None):
        gcm = growConfigManager.getInstance()
        
        if location == None: # get default
            location = gcm.dict['WiFiDefault']
            
        for loc in gcm.dict['WiFiLocations']:
            for key in loc.keys():
                if key == location:
                    rawPwd = loc[key]['password']
                    break
        
        return ubinascii.a2b_base64(rawPwd).decode('UTF-8')
        
class mqttConfig:
    def listMQTTLocations():
        gcm = growConfigManager.getInstance()
        
        locs = list()
        for loc in gcm.dict['MQTTLocations']:
            for key in loc.keys():
                locs.append(key)
        return locs
    
    def getConnectionDetails(location = None):
        gcm = growConfigManager.getInstance()
        
        if location == None: # get default
            location = gcm.dict['MQTTDefault']
        
        for loc in gcm.dict['MQTTLocations']:
            for key in loc.keys():
                if key == location:
                    return loc[key]
            
    def getMqttServer(location = None):
        return mqttConfig.getConnectionDetails(location).get('server')

    def getMqttPort(location = None):
        return mqttConfig.getConnectionDetails(location)['port']

    def getMqttUser(location = None):
        return mqttConfig.getConnectionDetails(location)['user']

    def getMqttPwd(location = None):
        rawPwd = mqttConfig.getConnectionDetails(location)['password']
        return ubinascii.a2b_base64(rawPwd).decode('UTF-8')

class growDevice:
    def getDeviceInfo():
        '''
        Returns dict with following keys:
        
        "ModuleName": "Grow Module v0.5,0.0.3",
        "ModuleSerialNumber": "1234554322",
        "ModuleRevision": "0.0.1",
        "ConfigurationVersion": "0.3"
        '''
        gcm = growConfigManager.getInstance()
        return gcm.dict['Device']

class debug:
    def getSensorDebug():
        gcm = growConfigManager.getInstance()
        return gcm.dict['Debug']['sensorDebug']
    def getC8yDebug():
        gcm = growConfigManager.getInstance()
        return gcm.dict['Debug']['c8yDebug']
    def getTaskDebug():
        gcm = growConfigManager.getInstance()
        return gcm.dict['Debug']['taskDebug']
    
    