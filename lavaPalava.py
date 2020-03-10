#!/usr/bin/env python
# coding: Latin-1

# Simple example of a motor sequence script

# Import library functions we need
import ZeroBorg
import time
import math
import sys
from gpiozero import LineSensor
import pygame
import os

sys.stdout = sys.stderr

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print('No ZeroBorg found, check you are attached :)')
    else:
        print('No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress))
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I²C address change the setup line so it is correct, e.g.')
        print('ZB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()
#ZB.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.SetCommsFailsafe(False)             # Disable the communications failsafe
ZB.ResetEpo()

# Movement settings (worked out from our YetiBorg v2 on a smooth surface)
timeForward1m = 7.0                     # Number of seconds needed to move about 1 meter
timeSpin360   = 7.0                     # Number of seconds needed to make a full left / right spin
#testMode = False                        # True to run the motion tests, False to run the normal sequence

triangle = 2	              		#Button to start the Test (triangle)
interval = 0.01

# Power settings
voltageIn = 9.6                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 9.6                        # Maximum motor voltage

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
    #ZB.MotorsOff()

def PerformStop():
    PerfomMove(0,0)

rightSensor = LineSensor(17,pull_up=None,active_state=False)
middleSensor = LineSensor(27,pull_up=None,active_state=False)
leftSensor = LineSensor(22,pull_up=None,active_state=False)

def rabbit(lastDirection):
    middle_detect = int(middleSensor.value)
    hadEvent = False
    events = pygame.event.get()
    while middle_detect == 0:
        if lastDirection == "left":
            PerformMove(-0.8,0.8)
        if lastDirection == "right":
            PerformMove(0.8,-.8)
        #if lastDirection == "straight":
        #    PerformMove(1,1)
        middle_detect = int(middleSensor.value)
        #for event in events:
        #    if event.type == pygame.JOYBUTTONDOWN:
        #        hadEvent = True
        #        if hadEvent:
        #            if joystick.get_button(triangle):
        #                print("Triangle Pressed!")
        #                ZB.MotorsOff()
        #                break

ZB.MotorsOff()
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1,1))
print 'waiting for joystick... (press CTRL+C to abort)'

def line_follow():
    driving = True
    direction = "straight"
    while driving:
        hadEvent = False
        right_detect = int(rightSensor.value)
        middle_detect = int(middleSensor.value)
        left_detect = int(leftSensor.value)
#        print right_detect
#        print middle_detect
#        print right_detect
        if right_detect == 1 and left_detect == 1 and middle_detect == 1:
            PerformMove(0,0)
#            print "Stop!"
        elif right_detect == 1 and middle_detect == 0 and left_detect == 0:
            PerformMove(1,0.2)
#            print "Turn Right!"
            direction = "right"
        elif left_detect == 1 and middle_detect == 0 and right_detect == 0:
            PerformMove(0.2,1)
#            print "Turn Left!"
            direction = "left"
        elif middle_detect == 1 and left_detect == 0 and right_detect == 0:
#            print "Forward!"
            PerformMove(1,1)
            #direction = "straight"
        elif middle_detect == 1 and left_detect == 1 and right_detect ==0:
            print "Slight left"
            PerformMove(0.8,1)
            direction = "left"
        elif middle_detect == 1 and right_detect == 1 and left_detect ==0:
            print "Slight right"
            PerformMove(1,0.8)
            direction = "right"
        elif (right_detect == 0 and left_detect == 0 and middle_detect == 0):
            print "find the line! Spin to the %s" % (direction)
            rabbit(direction)
        #events = pygame.event.get()
        #for event in events:
        #    if event.type == pygame.JOYBUTTONDOWN:
        #        hadEvent = True
        #        print("EVENT!")
        #    if hadEvent:
        #        if joystick.get_button(triangle):
        #            print("Triangle Pressed!")
        #            ZB.MotorsOff()
        #            driving = False

def panic():
    for i in range(5):
        PerformMove(1,-1)
        PerformMove(1,1)
        PerformMove(1,-1)
        PerformMove(1,1)
        PerformMove(1,-1)

while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                # No joystick attached, toggle the LED
                ZB.SetLed(not ZB.GetLed())
                pygame.joystick.quit()
                time.sleep(0.1)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            # Failed to connect to the joystick, toggle the LED
            ZB.SetLed(not ZB.GetLed())
            pygame.joystick.quit()
            time.sleep(0.1)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print 'User aborted'
        ZB.SetLed(True)
        sys.exit()
print 'Joystick found'
joystick.init()
ZB.SetLed(False)

#PerformMove(0.5,0.5)
#time.sleep(0.2)
#PerformMove(0,0)
#time.sleep(0.2)
#PerformMove(-0.5,-0.5)
#time.sleep(0.2)
#PerformMove(0,0)

try:
    print('Press CTRL+C to quit')
    running = True
    hadEvent = False
    while running:
        #get the latest events
        hadEvent = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
            # User exit
                ZB.MotorsOff()
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                hadEvent = True
            if hadEvent:
                if joystick.get_button(triangle):
                    print("Button pressed")
                    line_follow()
        ZB.SetLed(ZB.GetEpo())
        time.sleep(interval)
    ZB.MotorsOff()
except KeyboardInterrupt:
    # CTRL+C exit diable all drives
    ZB.MotorsOff()

