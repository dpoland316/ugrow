'''
    Currently this is a glorified config file.
    
    The plan is to make the config come from memory or the
    disk, or Flash or...
    
'''
LOCATIONS={'home', 'traveling', 'other'}
LOCATION="home"
OTHER_WIFI="foo"
OTHER_WIFI_PWD="foo"

# Define Wifi/Server credentials
class wifiConfig:
    def getSSID(location=LOCATION):
        if location == "home":
            return "Sapphire"
        elif location == "traveling":
            return "Pretty Fly for a Wi-Fi"
        else:
            return OTHER_WIFI
    def getSSIDPwd(location=LOCATION):
        if location == "home":
            return "0102030405"
        elif location == "traveling":
            return "Cr4cker!"
        else:
            return OTHER_WIFI_PWD
# MQTT credentials
# mqttServer        = "m20.cloudmqtt.com";
# mqttPort      = 14273;
# mqttUser      = "qzznwlks";
# mqttPassword  = "E5-zs3McrjBQ";

class mqttConfig:
    def getMqttServer():
        return "mqtt.cumulocity.com"

    def getMqttPort(ssl=False):
        if ssl:
            return 8883
        else:
            return 1883

    def getMqttUser():
        return "gcsplarc/david.poland@softwareag.com"

    def getMqttPwd():
        return "asdfg12345YXCVB(!)"

# mqttUser      = "gcsplarc/techUser";
# mqttPassword  = "manage123!";