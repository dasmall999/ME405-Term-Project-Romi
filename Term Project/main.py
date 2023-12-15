'''!@file                       main.py
    @brief                      Main file for Romi running the course
    @details
    @author                     Andrew Whitacre
                                Drake Small
    @date                       October 22, 2023
'''

from pyb import UART, repl_uart, Timer, Pin, I2C, ADC
from task_share import Queue, Share
import cotask
import Motor_A_Task as MAT
import Motor_B_Task as MBT
import user_input_data_transfer as UI
import QTRSensorAnalog as QTR
import QTR_Task as QTRT
import gc
import L6206
import BNO055
import IMU_Task as IMUT
import HCSR04 as HCR
'''!@package              Import Tasks, devices, gc, cotask, and pyb
'''

def main():
    '''!@brief              The main function the passes in data shares, queues, task objects, pin definitions, schedules tasks
        @details            Currently only runs the QTR task which runs the ultrasonic code as well
    '''
    # Disable REPL on UART2
    repl_uart(None)
    
    # Create i2c object for the IMU
    # i2c = I2C(3)
    # imu = BNO055.BNO055(i2c)
    
    # Create some shares to use for the task
    let = Share('B', name="let_share") #for unsigned ascii char
    dc = Share('i', name="duty_cycle_share")
    sp = Share('i', name="set_point_share")
    gn = Share('f', name="gain_share")
    oc = Share('B', name="oc_share") #for unsigned int
    AV = Share('f', name="angular_vel_share")
    EA = Share('f', name="euler_angle_share")
    cc = Share('f', name="calib_coeff_share")
    mode = Share('i', name="mode_ID_share")
    # Create an object of the data transfer task
    oc.put(0) #init at open loop
    
    
    # Create Queues needed for data transfer to Jupyter
    mot_A_pos = Queue('H', 1, name="mot_A_pos")
    mot_A_spd = Queue('H', 1, name="mot_A_spd")
    mot_B_pos = Queue('H', 1, name="mot_B_pos")
    mot_B_spd = Queue('H', 1, name="mot_B_spd")

    
    # Create motor objects and Timer for them
    tim_4 = Timer(4, freq=20_000)
    mot_A = L6206.L6206(tim_4, Pin.cpu.B6, Pin.cpu.A8, Pin.cpu.A9, 1)
    mot_B = L6206.L6206(tim_4, Pin.cpu.B7, Pin.cpu.C2, Pin.cpu.C3, 2)
    # Create objects of the required Tasks
    user_input = UI.user_input_data_transfer(let, oc, dc, gn, sp)
    mot_A_obj = MAT.Motor_A_Task(mot_A, dc, oc, sp, gn, let, mot_A_pos, mot_A_spd)
    mot_B_obj = MBT.Motor_B_Task(mot_B, dc, oc, sp, gn, let, mot_B_pos, mot_B_spd)
    
    # Create Line Sensor objects, front
    C4 = Pin(Pin.cpu.C4, mode=Pin.ANALOG)
    C5 = Pin(Pin.cpu.C5, mode=Pin.ANALOG)
    adc0 = ADC(C4) #define ADCs with the pins
    adc1 = ADC(C5) #Channel 2 on the sensor
    QTR_F = QTR.QTRSensorAnalog(adc0, adc1)
    
    # Create Line Sensor objects, left
    B0 = Pin(Pin.cpu.B0, mode=Pin.ANALOG)
    B1 = Pin(Pin.cpu.B1, mode=Pin.ANALOG)
    adc2 = ADC(B0) #define ADCs with the pins
    adc3 = ADC(B1) #Channel 2 on the sensor
    QTR_L = QTR.QTRSensorAnalog(adc2, adc3)
    
    # Create Line Sensor objects, right
    A4 = Pin(Pin.cpu.A4, mode=Pin.ANALOG)
    A5 = Pin(Pin.cpu.A5, mode=Pin.ANALOG)
    adc4 = ADC(A4) #define ADCs with the pins
    adc5 = ADC(A5) #Channel 2 on the sensor
    QTR_R = QTR.QTRSensorAnalog(adc4, adc5)
    
    # Create Ultrasonic Sensor
    A6 = Pin(Pin.cpu.A6, mode=Pin.OUT_PP)
    A7 = Pin(Pin.cpu.A7, mode=Pin.IN)
    
    hcr = HCR.HCSR04(A6,A7)
    
    
    qtr_obj = QTRT.QTR_Task(QTR_F,QTR_L, QTR_R, mot_A, mot_B, hcr)
    # imu_obj = IMUT.IMU_Task(imu, mode, EA, AV, cc, let, mot_A, mot_B)
    
    
    
    # Create a task object using the run method from the data transfer object
    task1 = cotask.Task(user_input.run, name="UI Out",
                        priority = 1, period=10)
    task2 = cotask.Task(mot_A_obj.run, name="Motor_A_Driver",
                        priority = 2, period=100)
    task3 = cotask.Task(mot_B_obj.run, name="Motor_B_Driver",
                        priority = 2, period=100)
    task4 = cotask.Task(qtr_obj.run, name="QTR Sensor",
                        priority=2, period=30)
    # task5 = cotask.Task(imu_obj.run, name="IMU_Sensor",
                        # priority = 2, period=100)

    
    # Append the newly created task to the task list
    #cotask.task_list.append(task1)
    #cotask.task_list.append(task2)
    #cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    #cotask.task_list.append(task5)
    
    
    gc.collect()
    
    # Run the scheduler
    while True:
        try:
            cotask.task_list.pri_sched()
        
    # Trying to catch the "Ctrl-C" keystroke to break out
    # of the program cleanly
        except KeyboardInterrupt:
            break

# Once the program is over, do any sort of cleanup as needed
print('Program terminated')
    
    
if __name__ == '__main__':
    main()