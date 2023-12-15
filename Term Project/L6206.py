'''!@file                       L6206.py
    @brief                      A class for controlling the motors
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       October 10, 2023
'''

from pyb import Pin, Timer
'''!@package              Import Pin and Timer from pyb
'''

class L6206:
    
    def __init__ (self, PWM_tim, INPin, Dir_pin, EN_pin, channel):
        '''!@brief              Constructs a L6206 object
            @details            Defines pins, timer, and initializes duty cycle
            @param              PWM_tim Timer for PWM
            @param              INPin Pin for Timer
            @param              Dir_pin Pin for direction
            @param              EN_pin Pin for enabling motor
            @param              channel For the timer channel
        '''
        # Constructor
        self.PWM_tim = PWM_tim
        self.Dir_pin = Pin(Dir_pin, mode= Pin.OUT_PP)     
        self.EN_pin = Pin(EN_pin, mode= Pin.OUT)
        self.EN_pin = EN_pin
        self.duty = 0
        
        # Set high as default (Forward)
        self.Dir_pin.low()
        
        # Setting up the PWM
        self.PWM = self.PWM_tim.channel(channel, pin=INPin, mode=Timer.PWM)
        
    
    def set_duty (self, duty):
        '''!@brief              Sets the duty cycle of the motor
            @details            If duty paramter is negative, it converted back to a positive value and the direction pin is sent high, else it is sent low
            @param              duty The duty cycle entered as a percentage of a pulse
        '''
        self.duty = duty
        if duty < 0:
            self.PWM.pulse_width_percent(-1*duty)
            self.Dir_pin.high()

        else:
            self.PWM.pulse_width_percent(duty)
            self.Dir_pin.low()
            
    
    def enable(self):
        '''!@brief              Sets the enable pin high
        '''
        self.EN_pin.high()
        
    def disable(self):
        '''!@brief              Sets the enable pin low
        '''
        self.EN_pin.low()