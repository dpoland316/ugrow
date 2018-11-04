import time, math
import machine

MC_RED   =   4
MC_GREEN =   15
MC_BLUE  =   0

freq = 500
mcr = machine.PWM(machine.Pin(MC_RED), freq)
mcg = machine.PWM(machine.Pin(MC_GREEN), freq)
mcb = machine.PWM(machine.Pin(MC_BLUE), freq)



def pulse(color, t):
    for a in range(20):
        for i in range(20):
            if color == 'red':
                mcr.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
                mcb.duty(0)
                mcg.duty(0)

            elif color == 'green':
                mcr.duty(0)
                mcb.duty(0)
                mcg.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))

            elif color == 'blue':
                mcr.duty(0)
                mcb.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
                mcg.duty(0)

            elif color == 'yellow':
                mcr.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
                mcb.duty(0)
                mcg.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))

            elif color == 'purple':
                mcr.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
                mcb.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
                mcg.duty(0)

            elif color == 'aqua':
                mcr.duty(0)
                mcb.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))
                mcg.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))

            time.sleep_ms(t)
    mcr.duty(0)
    mcg.duty(0)
    mcb.duty(0)

#pulse('aqua', 50)