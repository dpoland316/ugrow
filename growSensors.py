'''
    Gather Sensor Data

'''
import growPinConfig
import credentialManager3
import dht
import time
from machine import Pin, ADC

debug = credentialManager3.debug

thSensor = dht.DHT22(Pin(growPinConfig.DHTPIN))
lightSensor = ADC(0) # analog to digital conversion


def getTempAndHumidity():
    # get the measurements
    thSensor.measure()
    time.sleep(2) # let the sensor collect data
    temp = thSensor.temperature() # eg. 23.6 (°C)
    hum = thSensor.humidity()    # eg. 41.3 (% RH)

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
    sensorValue = lightSensor.read()  # read the input on analog pin

    vIn=3.3
    vOut = sensorValue * (vIn / 1023.0) # Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 3.3V)

    # percentage of light as a function of the range of the sensor
    percentage = (sensorValue / 1023.0) * 100.0
    
    RLDR = (((( vIn + .1) * 500) / vOut) - 500) / 5000 # Equation to calculate Resistance of LDR
    # R1 = 5,000 Ohms

    lux = (500 / RLDR);

    if (debug.getSensorDebug()):
        print("Light Sensor -- reading: " + str(sensorValue) + " percent: " + str(percentage)
                    + " RLDR: " + str(RLDR) + " Lux: " + str(lux))

    return lux


if __name__ == '__main__':
    getTempAndHumidity()
    getLight()