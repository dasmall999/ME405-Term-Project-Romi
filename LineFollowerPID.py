'''!@file                       LineFollowerPID.py
    @brief                      A class for PID control
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       December 11, 2023
'''

class LineFollowerPID:

    def init(self, v_target, omega_target, Kp, Ki, Kd):
        '''!@brief              Constructs a PID controller object
            @details            Defines constants, sets PID variables
            @param              v_target Target linear velocity
            @param              omega_target Setpoint for angular velocity of the robot
            @param              Kp Proportional gain of controller
            @param              Ki Integral gain of controller
            @param              Kd Derivative gain of controller
        '''
        self.r = .035 #m
        self.L = .14 #m
        self.v_target = v_target
        self.omega_target = omega_target
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # Initialize PID vars
        self.error = 0.0
        self.last_error = 0.0
        self.integral = 0.0


    def get_wheel_speed(self):
        '''!@brief              Uses PID to get an output, uses output to calulate angular velocity of wheels
            @returns            Tuple of the target angular velocities of each wheel
        '''
        # Add to the integral error
        self.integral += self.error

        #find output
        output = self.Kp * self.error + self.Ki * self.integral + self.Kd * (self.error - self.last_error)

        # Calculate angular velocities of the wheels using the output
        omega_r = (self.v_target + self.L * self.omega_target / 2) / self.r + output
        omega_l = (self.v_target - self.L * self.omega_target / 2) / self.r - output

        # Save current error for integral next loop
        self.last_error = self.error

        return omega_r, omega_l