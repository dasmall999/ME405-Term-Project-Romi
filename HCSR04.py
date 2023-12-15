'''!@file                       HCSR04.py
    @brief                      A class for reading from the ultrasonic sensor
    @details
    @author                     Roberto Sánchez
    @date                       December 14, 2023
'''

import machine
import time
'''!@package              Import machine and time
'''


class HCSR04:

    # echo_timeout_us is based in chip range limit (400cm)
    def init(self, trigger, echo):
        '''!@brief              Constructs an ultrasonic sensor object
            @details            Defines limits, sets pins and their values
            @param              pinA Pin for channel 1 of the Timer
            @param              pinB Pin for channel 2 of the Timer
            @param              tim_N Timer for the encoder
        '''
        self.echo_timeout_us = 500230 #4m limit

        self.trigger = trigger # Init trigger pin (out)

        self.trigger.value(0)

        self.echo = echo   # Init echo pin (in) 

    def _send_pulse_and_wait(self):
        '''!@brief              Sends a 10us pulse from the transmitter and waits for response
            @details            Times the time the echo pin is high after recieving a pulse
        '''
        self.trigger.value(0) # zero out
        time.sleep_us(5)

        self.trigger.value(1) # Send a 10us pulse.
        time.sleep_us(10)

        #self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        '''!@brief              Calulates the distance from the echo pin's time spent high
            @returns            Distance in mm
        '''
        pulse_time = self._send_pulse_and_wait()
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        '''!@brief              Calulates the distance from the echo pin's time spent high
            @returns            Distance in cm
        '''
        pulse_time = self._send_pulse_and_wait()
        cms = (pulse_time / 2) / 29.1
        return cms