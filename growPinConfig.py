# Define LED pins
YELLOW   =   12
BLUE     =   0
GREEN    =   14
#MC_RED   =   
#MC_GREEN =   
#MC_BLUE  =   

LEDPINS=[YELLOW,BLUE,GREEN]

#Define I2C Pins
SCL=5
SDA=4

# Define Sensor Pins
LDR     = 1       # ADC Channel 1 Light Sensor (Light Dependent Resistor)
SOILPWR = 15      # Sensor only receives power to take a reading (to prevent degradation)
SOIL    = 3       # ADC Channel 3
DHTPIN  = 13      # Temp and Humidity
DHTTYPE = 'DHT22'
SOIL    = 'N/A'

# Define indicator pins
MONITORPIN  = YELLOW;
WIFIPIN     = BLUE;
MQTTPIN     = GREEN;

# Define colors for multi color LED
COLORS = {'purple', 'blue', 'aqua', 'green', 'yellow', 'red'} # rainbow order
