'''!@file                       IMU_Task.py
    @brief                      A class for driving the IMU in main
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       October 22, 2023
'''

from task_share import Queue
from task_share import Share
'''!@package                    import Queue, Share
'''
class ClosedLoop:
    
    def __init__(self, kP, setPoint):
        '''!@brief              Constructs an IMU Task object
            @details            Sets flags, objects, motors, initializes data, mode, and state
            @param              kP Share proportional gain
            @param              setPoint Share for setPoint
        '''
        self.kP = kP
        self.setPoint = setPoint
        self.integral = 0
        
    def set_gain(self, kP):
        self.kP = kP
        
    def set_sp(self, sp):
        self.sp = sp

        
    def update(self, speedMeasured, kp, sp):
        #amount of error between setPoint and measured speed
        error = sp - speedMeasured
        
        #set the prop
        proportional = kp * error
        
        # Adds the current error times the kI term to the integral
        self.integral += (.5 * error)
        
        # Derivate takes the change of error times the kD term
        #derivative = self.kD * (error-self.prev_error)
        
        # Update the prev_error for the next loop
        #self.prev_error = error
        
        # Output of the controller
        output = proportional + self.integral
        #output = proportional
        return output
    
   
        
    