# Define LED pins
BLUE     =   12 #D6
GREEN    =   13 #D7
YELLOW   =   15 #D8
RED      =   14 #D5 

LEDPINS=[YELLOW,BLUE,GREEN]

#Define I2C Pins
SCL=4 #5
SDA=5 #4

# Define Sensor Pins
LDR     = 3       # ADC Channel 1 Light Sensor (Light Dependent Resistor)
SOILPWR = 16      # Sensor only receives power to take a reading (to prevent degradation)
SOIL    = 1       # ADC Channel 3
DHTPIN  = 0 #13      # Temp and Humidity
DHTTYPE = 'DHT22'

# Define indicator pins
MONITORPIN  = YELLOW;
WIFIPIN     = BLUE;
MQTTPIN     = GREEN;
ALERTPIN    = RED;

# Define colors for multi color LED
COLORS = {'purple', 'blue', 'aqua', 'green', 'yellow', 'red'} # rainbow order
