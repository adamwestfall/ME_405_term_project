'''   @file                            main.py
   @brief                              Main file to run the ME 405 Autmatic Nerf Gun Term Project.
   @details                            A DC motor and encoder actuated nerf gun is controled by a thermal camera to automatically fire at targets.
                                       Note: Portions of this project have not been tested due to health concerns.
                                       Contains a task1_start_button method to instantiate a pin for the start button. 
                                       Contains a task2_thermal_camera method which includes the states and necessary implementation to retrieve and analyze camera image data.
                                       Contains a task3_pitch_control method to interact with the pitch motors.
                                       Contains a task4_yaw_control method to interact with the yaw motors.
                                       Contains a task5_nerf_gun method which actuates the nerf firing system.
   @author                             Jason Davis
   @author                             Adam Westfall
   @author                             Conor Fraser
   @copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
   @date                               March 1, 2023
'''

"""!
@file main.py
    This file contains code to run the ME405 term project. A nerf gun is controled by a thermal camera
    to fire at a hot region 2 times. Note: portions of this project have not been tested and are 
    based on the code of previous projects and intuition.

    

        

@author Adam Westfall
@author Jason Davis
@author Conor Fraser
@copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
@date                               March 1, 2023


"""

import gc
import math
import pyb
import cotask
import task_share, encoder, motor_driver, closed_loop_controller, utime, mlx_cam


def task1_start_button(shares):
    '''!  @brief                              Controls the start button functionality.
       @details                               Instantiates the pins required for the start button. 
                                              Checks that the button has been pressed for an adequate amount of time to prevent false positive readings.
       @param shares                          A list holding the shares used for this task.
    '''

    state = 0
    while True:
        if state == 0:
            # initial state setting up the pin to check for the signal
            # unsure where this pin is actually plugged in but designing it to not interfere with other pins
            # thinking this is a digital input so should be fine on this pin if not this will need to be changed
            start_pin = pyb.Pin(pyb.Pin.cpu.A5, pyb.Pin.IN)
            start = False
            
            state = 1

        elif state == 1:
            # Check for Start: check if the button is pressed for a sufficient amount of time
           
            # assuming a logic high will be a press of the button
            if start_pin.value() == True:
                # wait for 1 second to get rid of bouncing
                utime.sleep(1)
                # check that the pin is still high
                if start_pin.value() == True:
                    state = 2
        elif state == 2:
            # Start: this will set the start variable 
            start = True
            shares.put(start)

        yield

def task2_thermal_camera(shares):
    '''!  @brief                              Controls the thermal camera functionality.
       @details                               Instantiates the requirements for I2C communication with the camera.
                                              Grabs the heatmap image from the thermal camera after a 5 second delay.
                                              Filters the image, identifies the center of the hotspot and extropolates this into a physical location.
                                              This code has been tested externally in the edits made to mlx_cam.py in the main.
       @param shares                          A list holding the shares used for this task.
    '''
    
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
            # this is attempting to be somewhat cooperative and not completely blocking may need some adjustment
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
            
            # finding approx x location of the brightest pixels
            # reshape to 2-D list
            img = [pix_array[i:i+camera._width] for i in range(0, len(pix_array), camera._width)]  
            threshold = 75  # adjust as needed we were unable to test this fully but this value was working woutside of the full assembly
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
            
            # all real world distances needed these were never measured as the full assembly was unable to be put together
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
    '''!  @brief                              Controls the pitch DC motors functionality.
       @details                               Instantiates the necessary pins to interact with the pitch motors.
                                              Establishes a start position for the nerf gun.
                                              Utilizes the encoder, motor_driver, and closed_loop_controller files.
       @param shares                          A list holding the shares used for this task.
    '''
    
    start_share, pitch_done_share = shares
    state = 0
    while True:
        if state == 0:
            # initial state setting up the motor, encoder, and controller
            # pins were assumed based on the pins used for previous labs 
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
            # might be able to just check zero but this is here just in case
            if abs(duty) < 0.001:
                pitch_done_share.put(True)

        yield

def task4_yaw_control(shares):
    '''!  @brief                              Controls the yaw DC motors functionality.
       @details                               Instantiates the necessary pins to interact with the yaw motors.
                                              Establishes a start position for the nerf gun.
                                              Utilizes the encoder, motor_driver, and closed_loop_controller files.
                                              The position of the target from the thermal camera is used to locate the gun in the yaw direction.
       @param shares                          A list holding the shares used for this task.
    '''

    start_share, yaw_angle_share, yaw_done_share = shares
    state = 0
    while True:
        if state == 0:
            # initial state setting up the motor, encoder, and controller
            # pins were assumed based on the pins used for previous labs 
            enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
            input1 = pyb.Pin.cpu.B4
            input2 = pyb.Pin.cpu.B5
            timer1 = pyb.Timer(3, freq=20000)

            # creating motor
            motor_2_driver = motor_driver.MotorDriver(enable1, input1, input2, timer1)
            motor_2 = motor_2_driver.motor(input1, input2, 1, 2, "MOTOR B")
            motor_2_driver.enable()
            
            # creating encoder
            encoder_B = encoder.Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 8, ID="ENCODER A")
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
            # check that the duty cycle is very small so it is basically done
            # might be able to just check zero but this is here just in case
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
            
            deg_2_encoder = 20 # need to find this value   
            setpoint = angle*deg_2_encoder 
            Kp = 0.06        # might need to tune this
            controller2.set_setpoint(setpoint)
            controller2.set_kp(Kp) 
            encoder_B.update()
            current_pos = encoder_B.read()    
            duty = controller2.run(current_pos)
            motor_2.set_duty(duty) 
            # check that the duty cycle is very small so it is basically done
            # might be able to just check zero but this is here just in case
            small_duty = 0.005 
            if abs(duty) < small_duty:
                yaw_done_share.put(True)
                
        yield

def task5_nerf_gun(shares):
    '''!  @brief                              Controls the gun firing sequence.
       @details                               Instantiates the necessary pins to interact with the firing motors.
                                              Utilizes the data in shares that establishes yaw and pitch positions to confirm that the target is in the crosshairs.
                                              Establishes logic to fire when aimed at the target.
       @param shares                          A list holding the shares used for this task.
    '''
    
  
    start_share, pitch_done_share, yaw_done_share = shares
    state = 0
    while True:
        if state == 0:
            # initial state: setting up the output pins and initializing them to low
            # pin for rotating motors for firing assuming digital output
            motor_pin = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
            # pin for plunger assuming digital output 
            plunger_pin = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
            
            state = 1

        elif state == 1:
            # wait for start: wait for start to be true
            start = start_share.get()
            if start == True:
                # getting the motors spinning to be ready quickly
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
            num_to_fire = 2
            for i in range(num_to_fire):
                plunger_pin.high()
                # kinda arbitrary time at the moment needs testing
                # not sure if this is how the plunger needs to work
                utime.sleep(1)
                plunger_pin.low()
            motor_pin.low()

        yield
# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    """
    TODO:
        * fix period for all of the tasks

    
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
    task2 = cotask.Task(task2_thermal_camera, name="Thermal Camera", priority=2, period=100,
                         profile=True, trace=False, shares=(start,yaw_angle))
    task3 = cotask.Task(task3_pitch_control, name="Pitch Control", priority=3, period=100,
                         profile=True, trace=False, shares=(start,pitch_done))
    task4 = cotask.Task(task4_yaw_control, name="Yaw Control", priority=4, period=100,
                         profile=True, trace=False, shares=(start,yaw_angle,yaw_done))
    task5 = cotask.Task(task5_nerf_gun, name="Fire Nerf Gun", priority=5, period=100,
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