#!/usr/bin/env python
# coding: Latin-1

# Simple example of a motor sequence script

# Import library functions we need
import ZeroBorg
import time
import math
import sys
from gpiozero import LineSensor

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print 'No ZeroBorg found, check you are attached :)'
    else:
        print 'No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'ZB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
#ZB.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.SetCommsFailsafe(False)             # Disable the communications failsafe
ZB.ResetEpo()

# Movement settings (worked out from our YetiBorg v2 on a smooth surface)
timeForward1m = 7.0                     # Number of seconds needed to move about 1 meter
timeSpin360   = 7.0                     # Number of seconds needed to make a full left / right spin
testMode = False                        # True to run the motion tests, False to run the normal sequence

# Power settings
voltageIn = 9.6                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Function to perform a general movement
def PerformMove(driveLeft, driveRight):
    # Set the motors running
    ZB.SetMotor1(-driveRight * maxPower) # Rear right
    ZB.SetMotor2(-driveRight * maxPower) # Front right
    ZB.SetMotor3(-driveLeft  * maxPower) # Front left
    ZB.SetMotor4(-driveLeft  * maxPower) # Rear left
    # Turn the motors off
    ZB.MotorsOff()

rightSensor = LineSensor(17,active_state=False)
middleSensor = LineSensor(27,active_state=False)
leftSensor = LineSensor(22,active_state=False)


direction = ""

while True:
    right_detect = int(rightSensor.value)
    middle_detect = int(middleSensor.value)
    left_detect = int(leftSensor.value)

    if right_detect == 1:
        PerformMove(1, 0.5)
        direction = "right"
    elif left_detect == 1:
        PerformMove(0.5, 1)
        direction = "left"
    elif right_detect == 1 AND left_detect ==1:
        panic() 
    elif middle_detect == 1:
        PerformMove(1, 1)
    elif right_detect == 0 AND left_detect == 0 AND middle_detect == 1:
        rabbit(direction) 


def rabbit(lastDirection):
    while middle_detect == 0:
        if lastDirection == "left":
            PerformMove(-1,1)
	elif lastDirection == "right":
            PerformMove(1,-1)

def panic():
    for i in range(5):
        PerformMove(1,-1)
        PerformMove(1,1)
        PerformMove(1,-1)
        PerformMove(1,1)
        PerformMove(1,-1)
    
