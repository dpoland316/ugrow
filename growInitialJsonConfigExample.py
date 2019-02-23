'''
    Currently this is the config file which holds the initial
    json config. All passwords are base 64 UTF-8 encoded.
    
'''
initialConfig = """
{
  "WiFiDefault": "home",
  "WiFiLocations": [
    {
      "home": {
        "ssid": "Home_Network",
        "password": "U2FtcGxlUGFzc3dvcmQ="
      }
    },
    {
      "traveling": {
        "ssid": "WiFi Hotspot",
        "password": "RGlmZmVyZW50U2FtcGxlUGFzc3dvcmQ="
      }
    }
  ],
  "MQTTLocations": [
    {
      "pubServer": {
        "server": "mqtt.cumulocity.com",
        "port": 1883,
        "user": "mytenant/myuser@cumulocity.com",
        "password": "Q3VtdWxvY2l0eVRlbmFudFBhc3N3b3Jk"
      }
    },
    {
      "subServer": {
        "server": "myMosquittoServer.amazonaws.com",
        "port": 1883,
        "user": "mosquittoSubcriberUser",
        "password": "bW9zcXVpdHRvUGFzc3dvcmQ="
      }
    }
  ],
  "MQTTDefault": "pubServer",
  "Device": {
    "ModuleName": "Grow Module v0.5.1.0.0",
    "ModuleSerialNumber": "1A2S3DFCX5434",
    "ModuleRevision": "0.0.3",
    "ConfigurationVersion": "0.6" 
  },
  "Debug": {
    "sensorDebug": false,
    "c8yDebug": false,
    "taskDebug": false
  }
}
"""