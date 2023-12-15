'''!@file                       encoder.py
    @brief                      A driver for reading from Quadrature Encoders
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       October 10, 2023
'''

from pyb import Pin, Timer
'''!@package              Import Pin and Timer from pyb
'''

class Encoder:


    def __init__(self, pinA, pinB, tim_N):
        '''!@brief              Constructs an encoder object
            @details            Defines pins, channels, initizalizes the Auto Reload limit and counts
            @param              pinA Pin for channel 1 of the Timer
            @param              pinB Pin for channel 2 of the Timer
            @param              tim_N Timer for the encoder
        '''
        self.PinA = Pin(pinA)
        self.PinB = Pin(pinB)
        self.tim_N = tim_N
        # Setting up the Timer Channel
        self.tim_CH_A = tim_N.channel(1, pin=pinA, mode=Timer.ENC_AB) #B8 for timer 4
        self.tim_CH_B = tim_N.channel(2, pin=pinB, mode=Timer.ENC_AB) #B9 for timer 4 
        
        self.position = 0
        self.prevcount = 0
        self.currcount = 0
        self.delta = 0
        
        # Auto Reload Limit
        self.arlim = 65535
        self.half_arlim = self.arlim//2
    
    def update(self):
        '''!@brief              Updates encoder position and delta
            @details            Uses the timer's counter to update, accounts for over and underflow
        '''
        
        self.prevcount = self.currcount #copy
        self.currcount = self.tim_N.counter() #get current count
        self.delta = self.currcount - self.prevcount #final - inital counts
        
        if(self.delta < -(self.half_arlim)):
            self.delta = self.delta + (self.arlim + 1) #overflow
        elif(self.delta > (self.half_arlim)):
            self.delta = self.delta - (self.arlim + 1) #underflow
                
        self.position = self.position + self.delta #update running position
        
        
    def get_position(self):
        '''!@brief              Gets the most recent encoder position
            @returns             Encoder position
        '''
        return self.position

    def get_delta(self):
        '''!@brief              Gets the most recent encoder delta
            @returns             Encoder delta
        '''
        return self.delta

    def zero(self):
        '''!@brief              Resets the encoder position to zero            
        '''
        self.position = 0