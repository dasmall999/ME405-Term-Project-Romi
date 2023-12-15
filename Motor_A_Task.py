'''!@file                       Motor_A_Task.py
    @brief                      A class for driving Motor A in main
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       October 30, 2023
'''


import L6206
import Encoder
from pyb import Pin, Timer, UART
from task_share import Share
from task_share import Queue
from pyb import USB_VCP
import ClosedLoop as CL
import time
'''!@package              Import l6206, Encoder, Pin, Timer, UART, Share, queue, share, vcp, time, CL
'''

class Motor_A_Task:

    def __init__(self, motor, duty_cycle: Share, OC: Share, sp: Share, gain: Share, command_flag: Share, mot_A_pos: Queue, mot_A_spd: Queue):
        '''!@brief              Constructs a Motor A Task object
            @details            Sets flags, objects, motors, collects open/closed loop response data
            @param              motor for motor object
            @param              duty_cycle Share for duty cycle of motor
            @param              OC Share for open/closed loop
            @param              sp Share for closed loop setpoint
            @param              gain Share for closed loop gain
            @param              command_flag Command from UI
            @param              motor_A_pos Motor A position
            @param              motor_A_spd Motor A speed
        '''
        # Initialize everything for Motor A
        
        # Motor Timer
        self.ser = USB_VCP()
        # Encoder Timer
        tim_3 = Timer(3, period = 65535, prescaler = 0)
        
        
        # Constructors
        self.command_flag = command_flag
        self.encoder = Encoder.Encoder(Pin.cpu.B4, Pin.cpu.B5, tim_3)
        self.motor = motor
        self.motor.set_duty(0)
        self.motor.enable()
        self.state = 1 # set to Open Loop initially
        self.gain = gain
        self.duty_cycle = duty_cycle
        self.setpoint = sp
        self.echo = 0
        self.OC = OC
        self.mot_A_pos = mot_A_pos
        self.mot_A_spd = mot_A_spd
        self.closedloop = CL.ClosedLoop(int(self.gain.get()), int(self.setpoint.get()))
        
        self.uart = UART(2, 115200)
        self.uart.init(115200, bits=8, parity=None, stop=1)
    
    
    def run(self):
        '''!@brief              FSM for the Motor_A_Task
            @details            Reads in commands from UI, sets duty cycle, open/closed loop, and collects data to send to jupyter over UART
        '''
        while True:

            self.command_flag.get()
            self.duty_cycle.get()
            self.setpoint.get()
            self.gain.get()
            self.encoder.update()            
            if self.state == 1:
                
                # Set duty cycle for motor     
                if chr(self.command_flag.get()) == 'm': 
                        self.motor.change_dir(self.duty_cycle.get())
                        self.motor.set_duty(self.duty_cycle.get())
                        

                # Zero the position of encoder
                elif chr(self.command_flag.get()) == 'z':
                    self.encoder.zero()
                    self.command_flag.put(0)
                
                # Print out the position of encoder
                elif chr(self.command_flag.get()) == 'p':
                    self.ser.write("\n\r"+"Motor A Encoder Position:"+str(self.encoder.get_position())) #write position to PuTTY

                    
                # Print out the delta for encoder
                elif chr(self.command_flag.get()) == 'd':
                    self.ser.write("\n\r"+"Motor A Encoder Delta:"+str(self.encoder.get_delta()))
        
                # Print out the velocity for encoder
                elif chr(self.command_flag.get()) == 'v':
                    self.ser.write("\n\r"+"Motor A Encoder velocity:"+str(self.encoder.get_delta()*60000/16384/100))

                
                # Collect speed and pos and send to Jupyter
                elif chr(self.command_flag.get()) == 'g':
                    start = time.ticks_ms()
                    self.state = 2
                    
                    
                # set to closedloop    
                elif chr(self.command_flag.get()) == 'c':
                     self.state = 3
                     self.command_flag.put(0) 
                     

            # state for doing 30 seconds of data collection
            elif self.state == 2:
                if time.ticks_diff(time.ticks_ms(),start) < 30000:
                    pos1 = self.encoder.get_position()
                    spd1 = self.encoder.get_delta()#*60000/16384/100 
                    self.uart.write(f"{pos1},{spd1}")
                    
                else:
                    self.uart.write('!') # End condition for data transfer
                    
                    self.state = 1
                    self.command_flag.put(0)
                
                
            
            # Closed Loop
            elif self.state == 3:
                
                if chr(self.command_flag.get()) == 'k':
                    self.closedloop.set_gain(self.gain.get())
                    
                elif chr(self.command_flag.get()) == 's':
                    self.closedloop.set_sp(self.setpoint.get())
                
                # Trigger step response and send to plot
                elif chr(self.command_flag.get()) == 'r': #confused on how it works
                    start2 = time.ticks_ms()
                    self.state = 4
                    
                        
    
                # Set to Open Loop
                elif chr(self.command_flag.get()) == 'o':
                    self.state = 1
                    
            elif self.state == 4:
                    if time.ticks_diff(time.ticks_ms(), start2) < 5000:
                        pos2 = self.encoder.get_position()
                        spd2 = self.encoder.get_delta()*60000/16384/100 
                        self.uart.write(f"{pos2},{spd2}\n\r")

                        
                    else:
                        self.ser.write("\n\r Data Transfer Complete")                      
                        self.uart.write('$') # End condition for data transfer
                        self.command_flag.put(0)
                        self.state = 3

    
                # Set duty cycle based on speed of motor
                    motor_spd = self.encoder.get_delta()*60000/16384/100

                    if self.closedloop.update(motor_spd,self.gain.get(),self.setpoint.get())*100/250 > 100:
                        self.motor.set_duty(100) 
                    else:
                        self.motor.set_duty(self.closedloop.update(motor_spd, self.gain.get(), self.setpoint.get())*100/250)
    
            yield self.state


    
        