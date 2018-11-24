'''
    Gather Sensor Data

'''
import growPinConfig
import growConfig
import dht
import time
import ads1x15
from machine import Pin, ADC, I2C

debug = growConfig.debug

'''
ADS1115 Config
Rate:
0 :  128/8      samples per second
1 :  250/16     samples per second
2 :  490/32     samples per second
3 :  920/64     samples per second
4 :  1600/128   samples per second (default)
5 :  2400/250   samples per second
6 :  3300/475   samples per second
7 :  - /860     samples per Second

Gain:
Choose a gain of 1 for reading voltages from 0 to 4.09V.
 - 2/3 = +/-6.144V
 -   1 = +/-4.096V
 -   2 = +/-2.048V
 -   4 = +/-1.024V
 -   8 = +/-0.512V
 -  16 = +/-0.256V
'''
rate = 0
gain = 1
addr = 72 # default HW addr of ADC
i2c = I2C(scl=Pin(growPinConfig.SCL), sda=Pin(growPinConfig.SDA), freq=400000)
ads = ads1x15.ADS1115(i2c, addr, gain)
soilSensorPwr = Pin(growPinConfig.SOILPWR)

thSensor = dht.DHT22(Pin(growPinConfig.DHTPIN))

#*****************
#lightSensor = ADC(0) # analog to digital conversion

# init the ADC sensors
ads.set_conv(rate, 1)
ads.set_conv(rate, 3)


def getTempAndHumidity():
    # get the measurements
    thSensor.measure()
    time.sleep(2) # let the sensor collect data
    temp = thSensor.temperature() # eg. 23.6 (°C)
    hum = thSensor.humidity()    # eg. 41.3 (% RH)

    if (debug.getSensorDebug()):
        print("Temp and Humidity Sensor -- temp: {} humidity: {} ".format(temp, hum))

    return {'temp':temp, 'humidity':hum}

def getLight():
    '''
    
    float vIn;          # input voltage to sensor
    float vOut;         # sensor reading converted to voltage
    int sensorValue;    # sensor readin (0-1023)
    float percentage;   # percentage of light
    int lux;            # lux representation of reading
    float RLDR;         # Resistance calculation of potential divider with LDR

    '''
    vIn=3.3     # ESP8266 max voltage is 3.3v
    vOut = ads.raw_to_v(ads.read(rate, 1)) # read the input on analog pin
    
    # percentage of light as a function of the range of the sensor
    percentage = (vOut / vIn) * 100.0
    
    RLDR = (((( vIn + .1) * 500) / vOut) - 500) / 5000 # Equation to calculate Resistance of LDR
    # R1 = 5,000 Ohms

    lux = (500 / RLDR);

    if (debug.getSensorDebug()):
        print("Light Sensor -- reading: {} percent: {} RLDR: {} Lux: {}".format(vOut, percentage, RLDR, lux))

    return lux

def getSoilMoisture():
    soilSensorPwr.on()
    moistureReading=ads.read(rate, 3)
    soilVoltage = ads.raw_to_v(moistureReading)
    soilSensorPwr.off()
    
    # Sensor reads High Voltage when it's dry and low when it's wet
    # Sensor was calibrated to get below values
    
    sensor_max = 26000
    sensor_correction = 7000
    corrected_max = sensor_max - sensor_correction
    corrected_reading = moistureReading - sensor_correction
    
    moisturePercentage = (((corrected_max - corrected_reading)/corrected_max) * 100.0)
   
    if (debug.getSensorDebug()):
        print("Soil Moisture Sensor -- reading: {} percent: {} voltage: {}".format(moistureReading, moisturePercentage, soilVoltage))

    return moisturePercentage 

if __name__ == '__main__':
    getTempAndHumidity()
    getLight()