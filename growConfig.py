# Define LED pins
YELLOW   =   12
BLUE     =   5
GREEN    =   14
MC_RED   =   4
MC_GREEN =   15
MC_BLUE  =   0

LEDPINS=[YELLOW,BLUE,GREEN]

# Define Sensor Pins
LDR     = 0       # A0 Light Sensor (Light Dependent Resistor)
DHTPIN  = 13      # Temp and Humidity
DHTTYPE = 'DHT22'
SOIL    = 'N/A'

# Define indicator pins
MONITORPIN  = YELLOW;
WIFIPIN     = BLUE;
MQTTPIN     = GREEN;

sensorDebug = False
c8yDebug    = False
taskDebug   = False

# Define colors for multi color LED
COLORS = {'purple', 'blue', 'aqua', 'green', 'yellow', 'red'} # rainbow order
