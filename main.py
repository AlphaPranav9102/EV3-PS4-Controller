#!/usr/bin/env python3

#import modules
import evdev
import ev3dev.auto as ev3
import threading
import time

#Create functions to figure out how much to move
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(0,255),(-1000,1000))

def dc_clamp(value):
    return clamp(value,-1000,1000)

#Find PS4 controller from the list of devices.
print("Finding PS4 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
ps4dev = devices[0].fn

gamepad = evdev.InputDevice(ps4dev)

#Create variables for the motors to use

forward_speed = 0
side_speed = 0
running = True

#Create a class to and initialize the Large motors and run the motors.

class MotorThread(threading.Thread):
    def __init__(self):
        self.right_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        self.left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        threading.Thread.__init__(self)

    def run(self):
        print("Engine running!")
        while running:
            self.right_motor.run_forever(speed_sp=dc_clamp(forward_speed+side_speed))
            self.left_motor.run_forever(speed_sp=dc_clamp(-forward_speed+side_speed))
        self.right_motor.stop()
        self.left_motor.stop()

#Create a process for them to run on

motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()


# steer set up
steer_speed = 0

#Create a class to and initialize the Medium motors and run the motors

class DirectionThread(threading.Thread):
    def __init__(self):
        self.motor = ev3.MediumMotor(ev3.OUTPUT_D)
        threading.Thread.__init__(self)

    def run(self):
        print("Steer Ready...")
        while running:
            self.motor.run_forever(speed_sp=steer_speed)

#Create a process for them to run on.

steer_thread = DirectionThread()
steer_thread.setDaemon(True)
steer_thread.start()


# event listner
for event in gamepad.read_loop():   #this loops infinitely
    if event.type == 3:             #A stick is moved
        if event.code == 0:         #X axis on left stick
            forward_speed = -scale_stick(event.value)
        if event.code == 1:         #Y axis on left stick
            side_speed = -scale_stick(event.value)
        if side_speed < 100 and side_speed > -100:
            side_speed = 0
        if forward_speed < 100 and forward_speed > -100:
            forward_speed = 0

    if event.type == 1 and event.code == 305 and event.value == 1:
        steer_speed = 750

    if event.type == 1 and event.code == 306 and event.value == 1:
        steer_speed = -750

    if event.type == 1 and event.code == 307 and event.value == 1:
        steer_speed = 0

    if event.type == 1 and event.code == 304 and event.value == 1:
        pass



