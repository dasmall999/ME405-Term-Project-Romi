'''!@file                       QTRSensorAnalog.py
    @brief                      A class for reading from the analog reflectance sensor
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       November 10, 2023
'''

import pyb
import array
'''!@package              Import pyb and array
'''

class QTRSensorAnalog:

    def init(self, adc0, adc1):
        '''!@brief              Constructs a reflectance sensor object
            @details            Defines the ADC's and timer
            @param              adc0 ADC for right side channel
            @param              adc1 ADC for left side channel
        '''

        self.threshold = 1500 # ADC value threshold

        self.adc0 = adc0
        self.adc1 = adc1

        self.tim = pyb.Timer(7, freq=20_000)        # Create timer

        self.rx0 = array.array('H', (0 for i in range(100))) # ADC buffers of
        self.rx1 = array.array('H', (0 for i in range(100))) # 1 16-bit word, fill every .1sec


    def HighLow(self, val, threshold):
        '''!@brief              Returns logic high when value is greater than threshold
            @returns            1 for black and 0 for white
        '''
        if (val >= threshold):
            return 1 #black
        else:
            return 0 #white

    def read(self): #capture adc reading into array
        '''!@brief              Uses a timer to read the ADC values into arrays
        '''
        pyb.ADC.read_timed_multi((self.adc0, self.adc1), (self.rx0, self.rx1), self.tim)

    def readLine(self): #calculate the next motor action, will become main task
        '''!@brief              Reads in values and determines which channels see black or white
            @returns            3 for all white, 2 for left white, 1 for right white, 0 for all black
        '''
        self.read() #take a reading

        if ((self.HighLow(self.rx1[0], self.threshold) == 0) and (self.HighLow(self.rx0[0], self.threshold) == 0)):
            return 3 #both see white
        elif(self.HighLow(self.rx0[0], self.threshold) == 0): # assuming a low value means white
            return 1 #right sees white
        elif (self.HighLow(self.rx1[0], self.threshold) == 0):
            return 2 #left sees white

        else:
            return 0 #both see black