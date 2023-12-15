'''!@file                       QTR_Task.py
    @brief                      A class for following a line
    @details
    @author
    @author                     Andrew Whitacre
                                Drake Small
    @date                       November 28, 2023
'''

import time
import LineFollowerPID as PID
import machine
from pyb import Pin
import HCSR04
'''!@package                    Import time, LineFollowerPID, machine, Pin, HCSR04
'''

class QTR_Task:
    
    def __init__(self, qtr_front, qtr_left, qtr_right, motor_A, motor_B, hcr):
        '''!@brief              Constructs a QTR Task object
            @details            Sets flags, objects, motors, initializes data, mode, and state
            @param              qtr_front front line sensor
            @param              qtr_left left line sensor
            @param              qtr_right right line sensor
            @param              motor_A Motor A
            @param              motor_B Motor B
            @param              hcr Ultrasonic sensor
        '''
        self.qtr_front = qtr_front#instantiates object
        
        self.qtr_left = qtr_left
        self.qtr_right = qtr_right
        
        self.state = 0
        self.motor_A = motor_A
        self.motor_B = motor_B
        
        # Reflectance Sensor Line States
        self.line_state1 = 0
        self.line_state2 = 0
        self.line_state3 = 0
        
        # PID Params
        self.r_w = .035 # m
        self.V = .1
        self.target_w = 2 #rad/s
        self.L = 0.14
        self.previous_error = 0
        
        # Ultrasonic Sensor
        self.hcr = hcr
        self.wall = 0
        self.prev = 0
        
        
    def run(self):
        '''!@brief              FSM for the QTR Task
            @details            line following FSM, transitions between states based on sensor readings and elapsed time
        '''
        while True:
                if self.state == 0:
                    cms = self.hcr.distance_cm()
                    cm2 = self.hcr.distance_cm()
                    cm3 = self.hcr.distance_cm()
                    cms = (cms+ cm2 + cm3) /3
                    print("PREV: " + str(self.prev))
                    print("Wall: " + str(self.wall))
                    if cms <= 3 and not self.wall:
                        # if self.wall == 1:
                        #     self.state = 9
                        # else:
                            self.state = 2
                    # You hit the wall again after already hitting it
                    elif cms <= 3 and self.wall == 2:
                        self.state = 9
                        start = time.ticks_ms()
                    # You have crossed finish line and hit wall
                        
                    elif self.prev == 1 and self.wall == 1:
                            start = time.ticks_ms()
                            self.state = 7
                    # Didn't cross finish line, keep going
                    else:
                        self.state = 1
                        
                # Line Follower
                elif self.state == 1:
                    print(self.state)
                    # Update Each Sensor Reading
                    self.line_state1 = self.qtr_left.readLine()
                    self.line_state2 = self.qtr_front.readLine()
                    self.line_state3 = self.qtr_right.readLine()
                    
                    # print("L: " + str(self.line_state1))
                    # print("F: " + str(self.line_state2))
                    # print("R: " + str(self.line_state3))
                    # Create LineFollower instance
                    LF = PID.LineFollowerPID(self.V, self.target_w, Kp=1.25, Ki=0.2, Kd=0.01)
                    
                    
                    
                    if self.line_state1 == 0 and self.line_state2 == 0 and self.line_state3 == 0:
                        # All sensors see black, go straight
                        error = 0
                        self.prev = 1
                    elif self.line_state1 == 3 and self.line_state2 == 3 and self.line_state3 == 3:
                        # All sensors see white, go straight
                        error = 0
                        if self.prev == 1:
                            self.state = 7
                        else:
                            self.prev = 2
                    elif self.line_state2 == 2 and (self.line_state3 == 1 or self.line_state3 == 3):
                        error = 5
                        self.prev = 3
                    elif self.line_state2 == 1 and (self.line_state1 == 2 or self.line_state1 == 3):
                        error = -5
                        self.prev = 3
                    elif self.line_state1 == 1 or self.line_state1 == 3:
                        error = -8
                        self.prev = 4
                    elif self.line_state3 == 2 or self.line_state3 == 3:
                        error = 8
                        self.prev = 4
                    elif self.line_state2 == 1:
                        error = -2
                    elif self.line_state2 == 2:
                        error = 2
                        
                    else:
                        # Middle sensor sees white, go straight
                        error = 0.8 * self.previous_error
                        self.previous_error = error
                        
                    LF.error = error
                    
                    # Calculate motor speeds
                    omega_r, omega_l = LF.get_wheel_speed()
                    
                    self.motor_A.set_duty(15+omega_l)
                    self.motor_B.set_duty(8+omega_r)
                    self.state = 0
                    
                # Detected wall state    
                if self.state == 2:
                    print(self.state)
                    self.line_state2 = self.qtr_front.readLine()
                    # print(self.line_state2)
                    # Align yourself if not aligned
                    if not self.line_state2 == 0:
                        if self.line_state2 == 2 or self.line_state3 == 1:
                            self.motor_A.set_duty(-10)
                            self.motor_B.set_duty(10)
                        else:
                            self.motor_A.set_duty(-10)
                            self.motor_B.set_duty(10)
                        self.state = 2
                    # Once aligned, go around box
                    else:
                        self.state = 3
                        start = time.ticks_ms()
                # Pivot
                elif self.state == 3:
                    
                    if time.ticks_diff(time.ticks_ms(),start) < 2000:
                        self.motor_A.set_duty(10)
                        self.motor_B.set_duty(-10)
                    else:
                        start = time.ticks_ms()
                        self.state = 4
                # Go straight 
                elif self.state == 4:
                        print(self.state)
                        if time.ticks_diff(time.ticks_ms(),start) < 3000:
                            self.motor_A.set_duty(15)
                            self.motor_B.set_duty(15)
                        else:
                            start = time.ticks_ms()
                            self.state = 5
                # Pivot         
                elif self.state == 5:
                        print(self.state)
                        if time.ticks_diff(time.ticks_ms(),start) < 1500:
                            self.motor_A.set_duty(-10)
                            self.motor_B.set_duty(10)
                        else:
                            start = time.ticks_ms()
                            self.state = 6
                # Turn back onto path            
                elif self.state == 6:
                        print(self.state)
                        self.wall = 1
                        if time.ticks_diff(time.ticks_ms(),start) < 1750:
                            self.motor_A.set_duty(25)
                            self.motor_B.set_duty(35)
                        else:
                            start = time.ticks_ms()
                            self.state = 0
                            
                # Hit the finish line, drive into the box and           
                elif self.state == 7:
                    print(self.state)
                        
                    if time.ticks_diff(time.ticks_ms(),start) < 2000:
                        self.motor_A.set_duty(12)
                        self.motor_B.set_duty(12)
                    else:
                        self.motor_A.set_duty(0)
                        self.motor_B.set_duty(0)
                        start = time.ticks_ms()
                        self.state = 8
                 
                # Stop to show robot is in the box       
                elif self.state == 8:
                    self.wall = 2
                    print(self.state)
                    if time.ticks_diff(time.ticks_ms(),start) < 4250:
                        self.motor_A.set_duty(-20)
                        self.motor_B.set_duty(20)
                    else:
                        self.state = 0
                        
                        
                # Pivot to start        
                elif self.state == 9:
                    print(self.state)
                    if time.ticks_diff(time.ticks_ms(),start) < 1750:
                        self.motor_A.set_duty(-20)
                        self.motor_B.set_duty(20)
                    else:
                        start = time.ticks_ms()
                        self.state = 10
                        
                # Stop at Start        
                elif self.state == 10:
                        print(self.state)
                        if time.ticks_diff(time.ticks_ms(),start) < 3500:
                            self.motor_A.set_duty(20)
                            self.motor_B.set_duty(20)
                        else:
                            self.motor_A.disable()
                            self.motor_B.disable()
                            self.state = 10

                yield self.state
                    