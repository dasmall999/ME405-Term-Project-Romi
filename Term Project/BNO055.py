'''!@file                       BNO055.py
    @brief                      A class for reading from the IMU
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       November 27, 2023
'''


from pyb import I2C
import struct
from task_share import Share
from task_share import Queue
'''!@package              Import I2C from pyb, struct, share, and queue
'''

class BNO055:
    
    def __init__(self, i2c):
        '''!@brief              Constructs an IMU object
            @details            Initializes the I2C object, usable values, and defines register addresses
            @param              i2c I2C object
        '''
        
        # I2C BUS 3
        # PINOUT PC0 = SCL
        # PINOUT PC1 = SDA
        
        #we are assuming we dont need starts and ends
        #we are assuming that the mem statements are 
        #safe and dont modify stuff we dont need to
        
        #axis remap
        
        #assuming default config for all sensors
        
        #we need to init in a ndof mode for calib
        
        self.MAG = 0 #init to 0 when starting task, 3 when done
        self.ACC = 0
        self.GYR = 0
        self.SYS = 0
        self.calibrated = 0
        
        self.mode = 0
        self.cc = 0
        self.EA = 0
        self.i2c = i2c
        self.addr = 0x28
        self.OPR_MODE = 0x3D
        self.CALIB_STAT = 0x35
        
        
        self.i2c.init(I2C.CONTROLLER, baudrate = 400_000, gencall=False, dma=False)
        
        self.i2c.is_ready(self.addr)
        
        # self.i2c.mem_write(1, self.addr, 0x3F) #reset that jawn
        self.i2c.mem_write(0x21, self.addr, 0x41) #p0 axis remap config
        self.i2c.mem_write(0x04, self.addr, 0x42) #p0 axis sign config
        
    
    def change_mode(self, mode):
        '''!@brief              Updates and changes the mode
        '''
        if str(mode) == "IMU":
            self.mode = mode
            self.i2c.mem_write(8, self.addr, self.OPR_MODE)
        elif str(mode) == "COMPASS":
            self.mode = mode    
            self.i2c.mem_write(9, self.addr, self.OPR_MODE)
        elif str(mode) == "M4G":
            self.mode = mode    
            self.i2c.mem_write(10, self.addr, self.OPR_MODE)
        elif str(mode) == "NDOF_FMC_OFF":
            self.mode = mode    
            self.i2c.mem_write(11, self.addr, self.OPR_MODE)
        elif str(mode) == "NDOF":
            self.mode = mode
            self.i2c.mem_write(12, self.addr, self.OPR_MODE)
        elif str(mode) == "CONFIG":
            self.mode = mode
            self.i2c.mem_write(0, self.addr, self.OPR_MODE)
            
            
    
    def get_status(self):
        '''!@brief              Check the calibration status of the IMU
            @details            If a 3 is present in all 4 parts of the register, the system is calibrated
            @returns            1 upon sucessful calibration, 0 if otherwise
        '''
        self.change_mode("NDOF")
        status_byte = self.i2c.mem_read(1, self.addr, self.CALIB_STAT) #read 1 byte
        self.MAG = (status_byte[0] & 0b00000011) >> 0 #parse, chunk, 3 = calib
        self.ACC = (status_byte[0] & 0b00001100) >> 2 
        self.GYR = (status_byte[0] & 0b00110000) >> 4
        self.SYS = (status_byte[0] & 0b11000000) >> 6
        
        print("MAG: "+ str(self.MAG) + " ACC: " + str(self.ACC) + " GYR: " + str(self.GYR) + " SYS: " + str(self.SYS))
        
        if ((self.MAG == 3) and (self.ACC == 3) and (self.GYR == 3) and (self.SYS == 3)):
            self.calibrated = 1
        else:
            self.calibrated = 0
            
        return self.calibrated
    
    
    
    
    def get_coeffs(self):
        '''!@brief              Using structs, data is read from the ACC, MAG, GYR, and radius registers
            @details            Upon calibration, device is placed in config mode and registers are read
            @returns            All offsets from each axis for ACC, MAG, GYR, and radius
        '''
        if (self.calibrated == 1):
            self.i2c.mem_write(0, self.addr, self.OPR_MODE) # set to config
            self.mode = "CONFIG"
            
            ACC_OFFSET_X_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x55))[0]
            ACC_OFFSET_X_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x56))[0]
            ACC_OFFSET_Y_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x57))[0]
            ACC_OFFSET_Y_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x58))[0]
            ACC_OFFSET_Z_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x59))[0]
            ACC_OFFSET_Z_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x5A))[0]
            
            MAG_OFFSET_X_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x5B))[0]
            MAG_OFFSET_X_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x5C))[0]
            MAG_OFFSET_Y_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x5D))[0]
            MAG_OFFSET_Y_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x5E))[0]
            MAG_OFFSET_Z_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x5F))[0]
            MAG_OFFSET_Z_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x60))[0]
            
            GYR_OFFSET_X_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x61))[0]
            GYR_OFFSET_X_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x62))[0]
            GYR_OFFSET_Y_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x63))[0]
            GYR_OFFSET_Y_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x64))[0]
            GYR_OFFSET_Z_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x65))[0]
            GYR_OFFSET_Z_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x66))[0]
            
            ACC_RADIUS_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x67))[0]
            ACC_RADIUS_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x68))[0]
            MAG_RADIUS_LSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x69))[0]
            MAG_RADIUS_MSB = struct.unpack('b', self.i2c.mem_read(1, self.addr, 0x6A))[0]
            
            self.cc = struct.pack("22b", ACC_OFFSET_X_LSB, ACC_OFFSET_X_MSB, ACC_OFFSET_Y_LSB,
                                       ACC_OFFSET_Y_MSB, ACC_OFFSET_Z_LSB, ACC_OFFSET_Z_MSB,
                                       MAG_OFFSET_X_LSB, MAG_OFFSET_X_MSB, MAG_OFFSET_Y_LSB,
                                       MAG_OFFSET_Y_MSB, MAG_OFFSET_Z_LSB, MAG_OFFSET_Z_MSB,
                                       GYR_OFFSET_X_LSB, GYR_OFFSET_X_MSB, GYR_OFFSET_Y_LSB, 
                                       GYR_OFFSET_Y_MSB, GYR_OFFSET_Z_LSB, GYR_OFFSET_Z_MSB,
                                       ACC_RADIUS_LSB, ACC_RADIUS_MSB, MAG_RADIUS_LSB, 
                                       MAG_RADIUS_MSB)
            self.change_mode("NDOF")
            return self.cc
            
        else:
            print("Not  calibrated!")
    
    def set_coeffs(self, cc_struct): #cc is a struct
            '''!@brief              Writes given offsets to the IMU offset registers
                @details            In config mode, a struct contain ing all the numbers is unpacked
                @param              cc_struct A struct containing 22 bytes of given offsets
            '''
        
            
            self.i2c.mem_write(0, self.addr, self.OPR_MODE) # set to config
            self.change_mode("CONFIG")
            
            #unpack to tuple
            cc_tup = struct.unpack("22b", cc_struct)
            
            self.i2c.mem_write(cc_tup[0], self.addr, 0x55)
            self.i2c.mem_write(cc_tup[1], self.addr, 0x56)
            self.i2c.mem_write(cc_tup[2], self.addr, 0x57)
            self.i2c.mem_write(cc_tup[3], self.addr, 0x58)
            self.i2c.mem_write(cc_tup[4], self.addr, 0x59)
            self.i2c.mem_write(cc_tup[5], self.addr, 0x5A)
            
            self.i2c.mem_write(cc_tup[6], self.addr, 0x5B)
            self.i2c.mem_write(cc_tup[7], self.addr, 0x5C)
            self.i2c.mem_write(cc_tup[8], self.addr, 0x5D)
            self.i2c.mem_write(cc_tup[9], self.addr, 0x5E)
            self.i2c.mem_write(cc_tup[10], self.addr, 0x5F)
            self.i2c.mem_write(cc_tup[11], self.addr, 0x60)
            
            self.i2c.mem_write(cc_tup[12], self.addr, 0x61)
            self.i2c.mem_write(cc_tup[13], self.addr, 0x62)
            self.i2c.mem_write(cc_tup[14], self.addr, 0x63)
            self.i2c.mem_write(cc_tup[15], self.addr, 0x64)
            self.i2c.mem_write(cc_tup[16], self.addr, 0x65)
            self.i2c.mem_write(cc_tup[17], self.addr, 0x66)
            
            self.i2c.mem_write(cc_tup[18], self.addr, 0x67)
            self.i2c.mem_write(cc_tup[19], self.addr, 0x68)
            self.i2c.mem_write(cc_tup[20], self.addr, 0x69)
            self.i2c.mem_write(cc_tup[21], self.addr, 0x6A)
            
            self.i2c.mem_write(12, self.addr, self.OPR_MODE) #to fusion mode
            self.change_mode("NDOF")
            
    
    def read_euler(self): #may need a mode change, handled in task maybe
        '''!@brief              Reads and returns the Euler angle data
            @returns            A struct containing 6 btyes of euler angle data
        '''
        
        EUL_DATA_X_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x1A), "big")
        EUL_DATA_X_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x1B), "big")
        EUL_DATA_Y_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x1C), "big")
        EUL_DATA_Y_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x1D), "big")
        EUL_DATA_Z_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x1E), "big")
        EUL_DATA_Z_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x1F), "big")
        
        EA = struct.pack('6b', EUL_DATA_X_LSB, EUL_DATA_X_MSB, EUL_DATA_Y_LSB,
                               EUL_DATA_Y_MSB, EUL_DATA_Z_LSB, EUL_DATA_Z_MSB)
        return EA
        
        
        
    
    def read_ang_vel(self):
        '''!@brief              Reads and returns the anglular velocity data
            @returns            A struct containing 6 btyes of angular velocity data
        '''
        GYR_DATA_X_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x14), "big")
        GYR_DATA_X_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x15), "big")
        GYR_DATA_Y_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x16), "big")
        GYR_DATA_Y_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x17), "big")
        GYR_DATA_Z_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x18), "big")
        GYR_DATA_Z_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x19), "big")
        
        AV = struct.pack('6b', GYR_DATA_X_LSB, GYR_DATA_X_MSB, GYR_DATA_Y_LSB,
                               GYR_DATA_Y_MSB, GYR_DATA_Z_LSB, GYR_DATA_Z_MSB)
        return AV
    
    
    def read_mag(self):
        '''!@brief              Reads and returns the magnetometer data
            @returns            A struct containing 6 btyes of magnetometer data
        '''
        MAG_DATA_X_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x0E), "big")
        MAG_DATA_X_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x0F), "big")
        MAG_DATA_Y_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x10), "big")
        MAG_DATA_Y_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x11), "big")
        MAG_DATA_Z_LSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x12), "big")
        MAG_DATA_Z_MSB = int.from_bytes(self.i2c.mem_read(1, self.addr, 0x13), "big")
        
        MG = struct.pack('6b', MAG_DATA_X_LSB, MAG_DATA_X_MSB, MAG_DATA_Y_LSB,
                               MAG_DATA_Y_MSB, MAG_DATA_Z_LSB, MAG_DATA_Z_MSB)
        return MG

        