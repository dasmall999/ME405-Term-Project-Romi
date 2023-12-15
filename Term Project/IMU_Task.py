'''!@file                       IMU_Task.py
    @brief                      A class for driving the IMU in main
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       November 28, 2023
'''
import struct
import os
from task_share import Queue
from task_share import Share
from pyb import USB_VCP
import math
'''!@package              Import struct, os, queue, share, vcp and math
'''

class IMU_Task:
    
    def __init__(self, imu, modeID:Share, EA:Share, AV:Share, cc:Share, command_flag, motor_A, motor_B):
        '''!@brief              Constructs an IMU Task object
            @details            Sets flags, objects, motors, initializes data, mode, and state
            @param              imu For IMU object
            @param              modeID Share for IMU mode name
            @param              EA Share for Euler angle data
            @param              AV Share for angular velocity data
            @param              cc Share for calibration coefficients
            @param              command_flag Command from UI
            @param              motor_A Motor A
            @param              motor_B Motor B
        '''
        self.imu = imu
        self.command_flag = command_flag
        self.modeID = modeID # start in config mode
        self.EA = EA
        self.AV = AV
        self.cc = cc
        self.motor_A = motor_A
        self.motor_B = motor_B
        self.ser = USB_VCP()
        self.state = 0
        self.mode_dict = {0: "CONFIG",
                          8: "IMU",
                          9: "COMPASS",
                          10: "M4G",
                          11: "NDOF_FMC_OFF",
                          12: "NDOF", }
        
        self.imu.change_mode("NDOF")
        
    
    def run(self):
        '''!@brief              FSM for the IMU Task
            @details            Reads in coefficients if a file exists, else, calibrate to get data, then takes data based on UI command
        '''
        while True:
            # print(self.imu.mode)
            # print("State: " + str(self.state))
            
            if self.state == 0:
                print(self.imu.get_status())
                if "IMU_cal_coeffs.txt" in os.listdir():
                    print("FILE EXISTS")
                    self.state = 1
                else:
                    self.state = 2
        
            # State 1: File exists, read the coefficients
            elif self.state == 1:
                with open("IMU_cal_coeffs.txt", 'r') as file:
                    values = file.readline().strip().split(',')
                    cc_list = bytearray([int(value, 16) for value in values])
                    cc_struct = struct.pack('22b', *cc_list)
                    self.imu.set_coeffs(cc_struct)
                self.state = 4 # Skip to command state since we have coeffs already
                
            # State 2: Calibration
            elif self.state == 2:
                self.imu.change_mode("NDOF")
                self.ser.write(str((struct.unpack('b', self.imu.i2c.mem_read(1, 0x28, 0x35))[0])) + "\n\r")
                if self.imu.get_status():
                    self.state = 3 # Once calibrated, go to next step
                else:
                    self.state = 2 #not calibrated, stay in calibration state
            
            
            # State 3: Write new coefficients to file
            elif self.state == 3:
                with open("IMU_cal_coeffs.txt", 'w') as file:
                    print("FILE DOES NOT EXIST")
                    # print(self.imu.get_status())
                    if self.imu.get_status():
                        cc_tuple = struct.unpack('22b', self.imu.get_coeffs())
                        print(str(cc_tuple))
                        file.write(','.join(map(str, cc_tuple)))
                            
                self.state = 4 # Now we have new coeffs, go to command state
            
            
            # Command Flag State
            elif self.state == 4:
                # euler angles
                if chr(self.command_flag.get()) == 'a':
                    self.imu.change_mode("NDOF")
                    x,y,z = struct.unpack('hhh', self.imu.read_euler())
                    
                    # Convert to degrees
                    x = x // 16
                    y = y // 16
                    z = z // 16
                    self.ser.write(f"OLEA - X: {x}, Y: {y}, Z: {z}\n\r")
                    
                
                # angular velocity
                elif chr(self.command_flag.get()) == 'b':
                    x,y,z = struct.unpack('hhh', self.imu.read_ang_vel())
                    
                    # Convert to degrees/sec
                    x = x // 16
                    y = y // 16
                    z = z // 16
                    self.ser.write(f"OLAV - X: {x}, Y: {y}, Z: {z}\n\r")
                    
                # magnetometer
                elif chr(self.command_flag.get()) == 'n':
                    self.imu.change_mode("COMPASS")
                    x,y,z = struct.unpack('hhh', self.imu.read_mag())
                    
                    # Convert to uT
                    x = x // 16
                    y = y // 16
                    z = z // 16
                    if  (-3 < y and y < 3):
                        print("FACING NORTH (kinda)")
                        self.motor_A.set_duty(0)
                        self.motor_B.set_duty(0)
                        # self.command_flag.put(0)
                    else:
                        self.motor_A.set_duty(20)
                        self.motor_B.set_duty(-20)
                    self.ser.write(f"OLMG - X: {x}, Y: {y}, Z: {z}\n\r")
                    self.imu.change_mode("NDOF")
                    
                # euler angles
                elif chr(self.command_flag.get()) == 'e':
                    x,y,z = struct.unpack('hhh', self.imu.read_euler())
        
                    # Convert to degrees
                    x = x // 16
                    y = y // 16
                    z = z // 16
                    self.ser.write(f"CLEA - X: {x}, Y: {y}, Z: {z}\n\r")
                    
        
                # angular velocity
                elif chr(self.command_flag.get()) == 'f':    
                    x,y,z = struct.unpack('hhh', self.imu.read_ang_vel())
        
                    # Convert to m/s^2
                    x = x // 900
                    y = y // 900
                    z = z // 900
                    self.ser.write(f"CLAV - X: {x}, Y: {y}, Z: {z}\n\r")
                
            yield self.state
