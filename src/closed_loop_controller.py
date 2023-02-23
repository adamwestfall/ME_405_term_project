'''   @file                            closed_loop_controller.py
   @brief                              Proportional closed loop controller that can be applied to mechanical systems.
   @details                            Contains a Closed_loop_controller class that includes init, run, set_setpoint, and set_kp functions. 
                                       The user will input a prefered Kp value to set the controller gain.                                    
   @author                             Jason Davis
   @author                             Conor Fraser
   @author                             Adam Westfall
   @copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
   @date                               January 9, 2023
'''

#imports
import utime, encoder, motor_driver, pyb

class Closed_loop_controller:
    '''!  @brief                              Closed loop controller class.
       @details                               Contains init, run, set_setpoint, and set_kp functions. 
    '''
    
    def __init__ (self):
        '''!  @brief                              Initializes the closed loop controller object.
           @details                               Kp and setpoint self variables are established. 
        '''
        
        self.kp = 0
        self.setpoint = 0
        
        
    def run(self, current_pos):
        '''!  @brief                              Runs the proportional closed loop controller.
           @details                               Proportional controller that returns the necessary motor duty cycle.
           @return                                Returns the duty cycle needed by the motor.
        '''
        
        # duty cycle or torque = Kp * (position_want - position_current)
        duty_cycle = -1 * self.kp * (self.setpoint - current_pos)
        return duty_cycle
                    
    def set_setpoint(self, setpoint):
        '''!  @brief                              Sets the setpoint for the closed loop controller.
           @details                               Sets the setpoint for the closed loop controller.
        '''
        
        self.setpoint = setpoint
                    
    def set_kp(self, kp):
        '''!  @brief                              Sets the Kp for the closed loop controller.
           @details                               Sets the Kp for the closed loop controller.
        '''
            
        self.kp = kp
 
 
if __name__ == '__main__':

    #enable any motor and encoder pins, probaby imported    
    enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
    input1 = pyb.Pin.cpu.B4
    input2 = pyb.Pin.cpu.B5
    
    timer1 = pyb.Timer(3, freq = 20000) 

    #creating motor driver / motor objects
    # enable pin, input1, input2, timer
    m1_driver = motor_driver.MotorDriver(enable1, input1, input2, timer1)
    m1 = m1_driver.motor(input1, input2, 1, 2, "MOTOR A")
    
    encoder_A = encoder.Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4, ID="ENCODER A")
    
    # turning on the motor
    m1_driver.enable()
    
    # setting motor
    #m1.set_duty(75)
    # zero encoder
    encoder_A.zero()
    
    controller = Closed_loop_controller()
    
    #While loop to continously run the controller
    try:
        while True:
            
            controller.set_Kp()
            controller.set_setpoint(setpoint)
            
            time = []     
            position = []
            
            t_end = utime.time() + 2
            
            while utime.time() < t_end:
            
                #get position from encoder object
                encoder_A.update()
                current_pos = encoder_A.read()
                position.append(current_pos)
                time.append(utime.ticks_ms())
                pwm = control_loop.run(current_pos)
                m1.set_duty(pwm)
                
                #get time from utime.time()
                
            
                utime.sleep_ms(10)
                
            #print the output of time and position
            print(time)
            print(position)
            
        
    except KeyboardInterrupt:
        print('Program Terminated')
        m1.set_duty(0)
        
        
            
    
    