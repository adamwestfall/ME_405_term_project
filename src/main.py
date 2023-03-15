"""!
@file main.py
    This file contains code to run the ME405 term project. A nerf gun is controled by a thermal camera
    to fire at a hot region.

    

        

@author Adam Westfall
@author Jason Davis
@author Conor Fraser
@copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
@date                               March 1, 2023

TODO:
    * check that the logic of putting True and False in shares that expect an 8bit number is valid
    * see if we need to be checking for very small duty cycles to be done or just use a duty cycle of 0


"""

import gc
import math
import pyb
import cotask
import task_share, encoder, motor_driver, closed_loop_controller, utime, mlx_cam


def task1_start_button(shares):
    """!
    Checks the state of the button and acts if the button is pressed for a sufficient amount of time


    """
    state = 0
    while True:
        if state == 0:
            # initial state setting up the pin to check for the signal
            
            
            
            state = 1

        elif state == 1:
            # Check for Start: check if the button is pressed for a sufficient amount of time
           
            # right now this is sudo code
            if button_press == True:
                # wait for 1 second
                # check if button press is still true
                state = 2
        elif state == 2:
            # Start: this will set the start variable 
            start = True
            shares.put(start)

        yield

def task2_thermal_camera(shares):
    """!
    Task that sets up and gets images from the thermal camera. This is kind of the brains of this code.
    This task assumes the camera is on the 1st I2C bus.
    TODO:
        * set up the thermal camera as an I2c device
        * change from psuedo code
        * update this to be handled in an external file
        * look into how frequency will affect the waiting time
    """
    start, yaw_angle = shares
    state = 0
    while True:
        if state == 0:
            # initial state: setting up the camera as an I2C device and ensuring it is connected
            # the following code was take directly from Dr. Ridgleys mlx_cam.py
            # Select MLX90640 camera I2C address, normally 0x33, and check the bus
            i2c_bus = pyb.I2C(1)

            # Create the camera object and set it up in default mode
            camera = mlx_cam.MLX_Cam(i2c_bus)
            state = 1

        elif state == 1:
            # wait for start: wait for start to be true
            if start.get() == True:
                state = 2

        elif state == 2:
            # wait: this state waits for 5 seconds for the duel to actually start
            # this is attempting to be somewhat cooperative and not completely blocking
            total_time = 5 # seconds
            wait_time = .1 # seconds

            i = total_time/wait_time 
            while i > 0:
                utime.sleep(.1)
                i -= 1
                yield
            state = 3

        elif state == 3:
            # get image: get the image from the thermal camera
            image = camera.get_image()
            pix_array = camera.get_array(image.buf)
            
            state = 4

        elif state == 4:
            # get output vector: get the angle for the yaw to move
            # TODO: 
            #       * check what threshhold should be
            #       * convert x coord to an angle
            #           * figure out distance from camera to edge of table
            #           * figure out field of view
            
            # finding approx x location of the brightest pixels
            # reshape to 2-D list
            img = [pix_array[i:i+camera._width] for i in range(0, len(pix_array), camera._width)]  
            threshold = 100  # adjust as needed
            # apply threshold
            binary_img = [[1 if pixel > threshold else 0 for pixel in row] for row in img] 
            # find center of mass
            total_mass = 0
            center_mass = 0
            for y, row in enumerate(binary_img):
                mass = sum(row)
                total_mass += mass
                center_mass += y * mass
            if total_mass > 0:
                center_y = center_mass / total_mass
            else:
                center_y = None
            
            # all real world distances needed
            Field_x_len = 24 # distance of the camera field of view at the table edge in inches
            dist_from_pivot = 2 # distance from pivot value in inches
            
            # converting from an x index to the inches value
            x_dist = center_y * (Field_x_len/camera._width)

            # solving for the distance from the centerline of the person
            x = (Field_x_len/2) - x_dist

            # getting the angle
            if x > 0:
                angle = math.atan(x/dist_from_pivot)
            elif x < 0:
                angle = -math.atan(abs(x)/dist_from_pivot)
            
            # not sure if we need this but could be good to check the angle
            yaw_angle.put(angle)
            state = 1

        yield

def task3_pitch_control(shares):
    """!
    Task that runs another motor driver and dumps the data to the terminal 
    TODO:
        * ensure the correct pins are being used
        * figure out the values needed for state 2
    """
    start_share, pitch_done_share = shares
    state = 0
    while True:
        if state == 0:
            # initial state setting up the motor, encoder, and controller
            # TODO: Check all of the pins not sure if these are the correct ones
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

            # set pitch_done to False
            pitch_done_share.put(False)
            state = 1

        elif state == 1:
            # wait for start: wait for the start button to be pressed
            start = start_share.get()
            if start == True:
                state = 2

        elif state == 2:
            # pitch up to horizontal: the motor pitches to horizontal or set angle
            # this will require the gun to be in a known starting location
            setpoint = 20000 # need to figure out this value
            Kp = 0.06
            controller2.set_setpoint(setpoint)
            controller2.set_kp(Kp) 
            encoder_B.update()
            current_pos = encoder_B.read()    
            duty = controller2.run(current_pos)
            motor_2.set_duty(duty)
            # check that the duty cycle is very small so it is almost done
            if abs(duty) < 0.001:
                pitch_done_share.put(True)

        yield

def task4_yaw_control(shares):
    """!
    Task that starts the encoder and dumps the data to the terminal
    TODO:
        * ensure the correct pins are being used
        * figure out the values needed for state 2

    """
    start_share, yaw_angle_share, yaw_done_share = shares
    state = 0
    while True:
        if state == 0:
            # initial state setting up the motor, encoder, and controller
            # TODO: Check all of the pins not sure if these are the correct ones
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

            # init yaw_done
            yaw_done_share.put(False)
            state = 1

        elif state == 1:
            # wait for start: wait for start to be true
            start = start_share.get()
            if start == True:
                state = 2
        
        elif state == 2:
            # turn 180 degrees: the motor turns 180 degrees
            # this will require the gun to be in a known starting location
            # will have to play with this value to ensure it is getting to the location
            small_duty = 0.005   
            setpoint = 20000 # need to figure out this value
            Kp = 0.06        # might need to tune this
            controller2.set_setpoint(setpoint)
            controller2.set_kp(Kp) 
            encoder_B.update()
            current_pos = encoder_B.read()    
            duty = controller2.run(current_pos)
            if abs(duty) > small_duty:
                motor_2.set_duty(duty) 
            else:
                encoder_B.zero()
                state = 3
        
        elif state == 3:
            # wait for angle: wait for an angle to be set by the camera 
            angle = yaw_angle_share.get()
            if angle != 0:
                state = 4

        elif state == 4:
            # move to angle: once an angle is recieved move to the angle
            # TODO:
            #     * make sure the motor is moving in the correct direction
            
            deg_2_encoder = 20 # need to find this value   
            setpoint = angle*deg_2_encoder # need to figure out this value
            Kp = 0.06        # might need to tune this
            controller2.set_setpoint(setpoint)
            controller2.set_kp(Kp) 
            encoder_B.update()
            current_pos = encoder_B.read()    
            duty = controller2.run(current_pos)
            motor_2.set_duty(duty) 
            # check that the duty cycle is very small so it is basically done
            small_duty = 0.005 
            if abs(duty) < small_duty:
                yaw_done_share.put(True)
            
        

        yield

def task5_nerf_gun(shares):
    """!
    Task that runs the firing sequence of the motor 
    TODO: 
        * correct the pin locations

    """
    start_share, pitch_done_share, yaw_done_share = shares
    state = 0
    while True:
        if state == 0:
            # initial state: setting up the output pins and initializing them to low
            # pin for rotating motors for firing
            # correct pin
            motor_pin = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
            # pin for plunger
            # correct the pin
            plunger_pin = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
            
            state = 1

        elif state == 1:
            # wait for start: wait for start to be true
            start = start_share.get()
            if start == True:
                motor_pin.high()
                state = 2
        
        elif state == 2:
            # wait for motion: state that waits for other motion to finish to fire
            pitch_done = pitch_done_share.get()
            yaw_done = yaw_done_share.get()
            if pitch_done & yaw_done:
                state = 3
        
        elif state == 3:
            # firing sequence: sequence of spinning the motors and then firing a dart with the plunger
            # TODO: 
            #       * figure out if this is how this works
            num_to_fire = 2
            for i in range(num_to_fire):
                plunger_pin.high()
                #kinda arbitrary time at the moment
                # not sure if this is how the plunger needs to work
                utime.sleep(.2)
                plunger_pin.low()
            motor_pin.low()

        yield
# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    """
    TODO:
        * fix priority and period for all of the tasks

    
    """
    print("Running ME405 termproject \r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create the shares all of the intertask communication variables
    start = task_share.Share('b', thread_protect=False, name="Start")
    yaw_angle = task_share.Share('f', thread_protect=False, name="Yaw Angle")
    yaw_done = task_share.Share('b', thread_protect=False, name="Yaw Done")
    pitch_done = task_share.Share('b', thread_protect=False, name="Pitch Done")

 

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    
    task1 = cotask.Task(task1_start_button, name="Start Button", priority=1, period=100,
                        profile=True, trace=False, shares=(start))
    task2 = cotask.Task(task2_thermal_camera, name="Thermal Camera", priority=2, period=35,
                         profile=True, trace=False, shares=(start,yaw_angle))
    task3 = cotask.Task(task3_pitch_control, name="Pitch Control", priority=3, period=35,
                         profile=True, trace=False, shares=(start,pitch_done))
    task4 = cotask.Task(task4_yaw_control, name="Yaw Control", priority=4, period=35,
                         profile=True, trace=False, shares=(start,yaw_angle,yaw_done))
    task5 = cotask.Task(task5_nerf_gun, name="Fire Nerf Gun", priority=5, period=35,
                         profile=True, trace=False, shares=(start,pitch_done,yaw_done))
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    cotask.task_list.append(task5)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break