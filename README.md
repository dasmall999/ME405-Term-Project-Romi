# Line-Following Two-Wheeled Robot

Team Mecha06
-Andrew Whitacre
-Drake Smalls
 

# Introduction

Our two-wheeled robot uses cooperative multitasking along with several tasks and helper classes in order to follow a line around
a path, navigating obstacles as necessary. There are several challenges to the objective, such as complicated geometry for the
reflectance sensors, walls to go around, or navigating back to the starting position after finishing the route.

# Features

- STM32-L476RG
- Pololu Romi Chassis robot
- 3 two-channel Pololu Reflectance sensors
- BNO055 IMU
- User Interface for debugging
- HCSR04 ultrasonic sensor for detecting obstacles


# Challenges

The largest challenge was the closed loop feedback for the angular velocity of the wheels. In total the 
logic had to be rewritten 4 times in order to acquire functioning feedback and following the line accurately. Another challenge was
accidentally frying the STM32 we used for our robot, just two days before the demonstatrion, due to wiring complications. Tuning 
the robot was less challenging and more time-consuming, however it did help use learn a lot about closed loop feedback.



# Future Improvements

One of the biggest improvements we would want to implement is separating all of the wall logic from the rest of the line-following. This
is because right now our single task has 10 states, where it could just have two or three, then there could be wall-handling task that
would handle the rest, to make it not only easier to read, but debug and tune. Another improvement would be to use the IMU for the
location of the home, so we know where our robot is and make navigation much simpler that it currently is. There were certain solutions 
done at late hours of the night/morning that are not elegant or good coding practice. There is some unused code that is left in that 
would be removed at a later date.

# Equations

There are two main equations used in our code. The first is an equation derived from a homework assignment earlier in the quarter.
(V + (L*omega/2))/r_wheels

The following equation is used for calculating the output of the PID controller used for closed loop feedback in our line following task.
output = kP * error + kI * integral + kD*(error-prev_error)

# Acknowledgments

[We used this library for our ultrasonic sensor](https://github.com/rsc1975/micropython-hcsr04)

Equations used for calculating closed loop feedback, also used in homework 0x03, were derived with the help of [UCR Robotics](https://ucr-robotics.readthedocs.io/en/latest/tbot/moRbt.html)

Task_Share and cotask were created by JR Ridgely, referenced in the [ME405 Support Manual](https://github.com/spluttflob/ME405-Support/blob/main/src/cotask.py)

[This is the datasheet for the MCU used in this project](https://www.st.com/resource/en/datasheet/stm32l476je.pdf)