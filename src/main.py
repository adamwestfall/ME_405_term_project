"""!
@file main.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

    This file contains the code to succesfully run 2 motors with motor control 
    according to lab3 of ME-405. 
        * the motors run a step response and dump that data to the terminal in
            which it can be copied to a csv (this can be replaced by a uart or other connection 
            but is simple this way)
        * only the data from the step response is printed to the terminal once 
            the rest of the data from the run is not printed to the terminal

        

@author Adam Westfall
@author Jason Davis
@author Conor Fraser
@copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
@date                               January 9, 2023
TODO: 
    * Test prevous functionality on boards
    * Implement motor control for one motor 
        * cotask.py should have timing at around 10ms
        * make sure run() method in controllor class only does one calc each time
        * Run the motor with a flywheel
            * print results and plot step response like before
            * find the slowest rate at which the controllers preformance is noticably worse
            * Record the slowest rate at which the performance is not significantly worse than when running the controller at a fast rate
            * choose a good run rate for the motor control task - it should be a bit faster than the slowest rate which works for a factor of safety
            * Save copies of the step response plots for the slowest rate at which the response is good and for a rate at which the response isn't as good.
    * make two tasks which run two motors under closed-loop control at the same time
        * write a test program which moves your motors simultaneously through different distances and holds them at the desired positions

"""

import gc
import pyb
import cotask
import task_share, encoder, motor_driver, closed_loop_controller, utime

def task1_get_encoder():
    """!
    Task that starts the encoder and dumps the data to the terminal

    """
    state = 0
    while True:
        if state == 0:
            # initial state setting up the motor and encoder
            # enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
            # input1 = pyb.Pin.cpu.B4
            # input2 = pyb.Pin.cpu.B5
            # timer1 = pyb.Timer(3, freq=20000)
            
            # creating encoder
            encoder_A = encoder.Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4, ID="ENCODER A")
            encoder_A.zero()
            state = 1

        if state == 1:
            encoder_A.update()
            current_pos = encoder_A.read()

            print(current_pos)

        yield

            






def our_task2_fun():
    """!
    Task that runs another motor driver and dumps the data to the terminal 
    @param Kp a floating point value for the proportional coefficient
    @param setpoint an integer value for the position the motor is to go to (can be -/+)
    """
    state = 0
    while True:
        if state == 0:
            # initial state setting up the motor and encoder
            enable2 = pyb.Pin(pyb.Pin.cpu.C1, pyb.Pin.OUT_PP)
            input3 = pyb.Pin.cpu.A0
            input4 = pyb.Pin.cpu.A1
            timer2 = pyb.Timer(5, freq=20000)

            # creating motor
            motor_2_driver = motor_driver.MotorDriver(enable2, input3, input4, timer2)
            motor_2 = motor_2_driver.motor(input3, input4, 1, 2, "MOTOR B")
            motor_2_driver.enable()
            
            # creating encoder
            encoder_B = encoder.Encoder(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 8, ID="ENCODER A")
            encoder_B.zero()

            # creating controller
            controller2 = closed_loop_controller.Closed_loop_controller()
            # different setpoint from the motor above
            setpoint = 20000
            Kp = 0.06
            controller2.set_setpoint(setpoint)
            controller2.set_kp(Kp)

            # setting up to read the time
            initial_time = utime.ticks_ms()
            # getting the final step time in ms
            final_step_time = 2/0.001
            
            # setting up the storage lists
            state = 1

        if state == 1:
            # running the controller
            # want to get data for only a certain amount of time 
            time = utime.ticks_diff(utime.ticks_ms(),initial_time)
            encoder_B.update()
            current_pos = encoder_B.read()
            # this runs only if the time 
            if  time <= final_step_time:
                # times.append(time)
                # positions.append(current_pos)
                #print(utime.ticks_diff(time,initial_time))
                print(f"{time} {current_pos}")
                
            duty = controller2.run(current_pos)
            motor_2.set_duty(duty)

        yield




# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    """
    TODO:
        * implement the two functions with cotsk.py shouldnt be any task_share stuff

    
    """
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    # share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    # q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
    #                       name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    
    task1 = cotask.Task(task1_get_encoder, name="Task_1", priority=1, period=100,
                        profile=True, trace=False)
    # task2 = cotask.Task(our_task2_fun, name="Task_2", priority=2, period=35,
    #                      profile=True, trace=False)
    cotask.task_list.append(task1)
    # cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # # Print a table of task data and a table of shared information data
    # print('\n' + str (cotask.task_list))
    # print(task_share.show_all())
    # print(task1.get_trace())
    # print('')