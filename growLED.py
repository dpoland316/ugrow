import growPinConfig
from utime import sleep_ms
import machine
import math

FREQ = 1000 # Frequency for PWM machine.Pins

def init():
    for pin in growPinConfig.LEDPINS:
        myPin = machine.Pin(pin, machine.Pin.OUT)
        myPin.off()
    
    soilPwr = machine.Pin(growPinConfig.SOILPWR, machine.Pin.OUT)
    soilPwr.off()
    
    
    #===========================================================================
    # global mcr, mcg, mcb    
    # mcr = machine.PWM(machine.Pin(growPinConfig.MC_RED), FREQ)
    # mcg = machine.PWM(machine.Pin(growPinConfig.MC_GREEN), FREQ)
    # mcb = machine.PWM(machine.Pin(growPinConfig.MC_BLUE), FREQ)
    #===========================================================================

def ledControl (pin, onoff):
    myPin = machine.Pin(pin, machine.Pin.OUT)
    if onoff == 'on':
        myPin.on()
    else:
        myPin.off()

def blink (pin):
    myPin = machine.Pin(pin, machine.Pin.OUT)
    myPin.value(not bool(myPin.value())) # convert 0 and 1 to true and false and toggle it
    sleep_ms(100)
    myPin.value(not bool(myPin.value()))
#===============================================================================
# 
# def pulse(color, t=30):
#     print("Callback executed, color: " + color)
#     
#     if color in growPinConfig.COLORS:
#         for a in range(10):             # repeat the pulsing
#             for i in range(20):         # perform the pulse
#                 if color == 'red':
#                     mcr.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#                     mcb.duty(0)
#                     mcg.duty(0)
#     
#                 elif color == 'green':
#                     mcr.duty(0)
#                     mcb.duty(0)
#                     mcg.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#     
#                 elif color == 'blue':
#                     mcr.duty(0)
#                     mcb.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#                     mcg.duty(0)
#     
#                 elif color == 'yellow':
#                     mcr.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#                     mcb.duty(0)
#                     mcg.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#     
#                 elif color == 'purple':
#                     mcr.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#                     mcb.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#                     mcg.duty(0)
#     
#                 elif color == 'aqua':
#                     mcr.duty(0)
#                     mcb.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#                     mcg.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
#     
#                 sleep_ms(t)
#     mcr.duty(0)
#     mcg.duty(0)
#     mcb.duty(0)
#===============================================================================
