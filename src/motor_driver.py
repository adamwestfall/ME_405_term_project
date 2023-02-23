'''   @file                            motor_driver.py
   @brief                              Hardware driver for the L6206 dual H-bridge chip.
   @details                            Hardware driver for the L6206 dual H-bridge chip.  This driver 
                                       provides functionality to the nSleep pin to enable/disable either
                                       1 stepper motor or 2 DC motors.  Driver provides fault reset functionality
                                       and internally creates virtual motor objects based on user implementation.  
                                       Includes MotorDriver class and Motor class.
   @author                             Jason Davis
   @author                             Conor Fraser
   @author                             Adam Westfall
   @copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
   @date                               January 24, 2023
'''


import pyb, time

class MotorDriver:
    '''!  @brief                              Motor Driver class.
       @details                               Contains init, enable, disable, fault_cb, getEnableState, and motor functions.
                                              Used to set up motor objects.
    '''
    
    def __init__(self, en_pin, in1pin, in2pin, timer): 
        '''!  @brief                           Constructor for L6206 motor driver hardware
           @details                            Constructor for L6206 motor driver hardware   
           @param en_pin                       Encoder Pin
           @param in1pin                       Motor Pin 1
           @param in2pin                       Motor Pin 2
           @param timer                        Defines the hardware timer used with the motorDriver
        '''
        
        # enable pin
        self.en_pin = en_pin

        #input pins
        self.in1pin = in1pin
        self.in2pin = in2pin

        # initializing timer
        self.timer = timer
        
    def enable (self):
        '''!  @brief                           Enable the motors to spin
           @details                            Allows the motors to spin by writing the en_pin
                                               to logic high
        '''
        self.en_pin.high()
    
    def disable (self):
        '''!  @brief                           Disables motor function
           @details                            Keeps the motors from spinning by writing the en_pin
                                               to logic low
        '''
        self.en_pin.low()


        
    ## There are several fault conditions that may damage the motor / driver
    ## This function must disable the motor when a fault condition occurs
    ## Reference the button interrupt code used in lab 1  
# =============================================================================
#     5 Fault conditions possible:
#       undervoltage
#       overcurrent
#       short-circuit
#       open-load
#       overtemperature        
# =============================================================================

    def fault_cb (self, IRQ_src):
        '''!  @brief                           Detects a hardware fault condition
           @details                            Detects a hardware fault condition and interrupts harware function
                                               by disabling motor function
           @param IRQ_src                      The source of the interrupt causing a motor fault
        '''
        print('  *** FAULT DETECTED! SUSPENDING L6206 HARDWARE OPERATION ***')
        self.disable()
        
    def getEnableState(self):
        '''!  @brief                           Returns state of the motor.
           @details                            Reads the enable pin.
           @return                             Returns state of the motor.
        '''
        return self.en_pin.value()
    
    # def clearFaultCondition(self):
    #     '''   @brief                           Tests the value of the fault pin 
    #        @details                            
    #        @return                             Returns a boolean based on the fault pin
    #     '''
        
    #     faultCondition = self.faultCondition
    #     print('INITIAL FAULT STATUS: {0}'.format(self.nFAULT))
    #     if (not self.faultCondition):
    #           faultCondition = True
    #           print('MODIFIED FAULT STATUS: {0}'.format(self.nFAULT))
              
    #     return faultCondition
    
    ##also sets the direction
    # def set_duty(self, duty):
        
    #     if (duty > 0):
    #         self.duty = duty
    #         self.direction = 1
    #         #set the "reverse" channel to zero first
    #         self.channel2.pulse_width_percent(0)
    #         self.channel1.pulse_width_percent(duty)
            
    #     elif (duty < 0):
    #         duty *= -1
    #         self.duty = duty
    #         self.direction = -1
    #         #set the "forward channel to zero first
    #         self.channel1.pulse_width_percent(0)
    #         self.channel2.pulse_width_percent(duty)
            
    #     elif (duty == 0):
    #         self.duty = duty
    #         self.direction = 0
    #         self.brake()
    #         # print("{0} is stationary\n".format(self.motorID))
                    
    def motor (self, inputA, inputB, channelA, channelB, motorID):
        '''!  @brief                           Constructor for Motor function
           @details                            Constructor for Motor function
           @param inputA                       Input pin 1 of 2
           @param inputB                       Input pin 2 of 2
           @param motorTimer                   Timer associated with the motor
           @param channelA                     Timer channel 1 of 2
           @param channelB                     Timer channel 2 of 2
           @param motorID                      Identifier for the motor
           @return                             Returns motor object.
        '''
        return Motor(inputA, inputB, self.timer, channelA, channelB, motorID)
    
class Motor:
    '''!  @brief                              Motor class.
       @details                               Contains init, getMotorID, getDuty, set_duty, getEnableState, getDirection, 
                                              getRunState, toggleRunState, coast, and brake functions. 
                                              Used to interact with the motor objects.
    '''
        
    def __init__ (self, inputA, inputB, motorTimer, channelA, channelB, motorID):
        '''!  @brief                           Constructor for Motor class
           @details                            Constructor for Motor class
           @param inputA                       Input pin 1 of 2
           @param inputB                       Input pin 2 of 2
           @param motorTimer                   Timer associated with the motor
           @param channelA                     Timer channel 1 of 2
           @param channelB                     Timer channel 2 of 2
           @param motorID                      Identifier for the motor
        '''
        self.inputA = inputA
        self.inputB = inputB
               
        self.motorTimer = motorTimer
        # establish the motor timer channels here
        self.channel1 = self.motorTimer.channel(channelA, pyb.Timer.PWM, pin = inputA)
        self.channel2 = self.motorTimer.channel(channelB, pyb.Timer.PWM, pin = inputB)
        
        self.channelA = channelA
        self.channelB = channelB
        self.motorID = motorID
        
        # initialized to zero (off)
        self.duty = 0
        
        self.isRunning = False
        self.direction = 0
        
    def getMotorID(self):
        '''!  @brief                           Returns Motor ID
           @details                            Returns Motor ID
           @return                             Returns Motor ID        
        '''
        return self.motorID
    
    def getDuty(self):
        '''!  @brief                           Returns Motor Duty Cycle.
           @details                            Returns Motor Duty Cycle.
           @return                             Returns Motor Duty Cycle.       
        '''
        return self.duty
    
    def set_duty(self, duty):
        '''!  @brief                           Sets Motor Duty Cycle.
           @details                            Includes a set of if and elif blocks to establish the direction of the motor 
                                               as well as setting the duty cycle of the motor.
           @param duty                         Duty cycle parsed in from user input.
        '''
        
        if (duty > 0):
            self.duty = duty
            self.direction = 1
            #set the "reverse" channel to zero first
            self.channel1.pulse_width_percent(0)
            self.channel2.pulse_width_percent(duty)
            
        elif (duty < 0):
            duty *= -1
            self.duty = duty
            self.direction = -1
            #set the "forward channel to zero first
            self.channel2.pulse_width_percent(0)
            self.channel1.pulse_width_percent(duty)
            
        elif (duty == 0):
            self.duty = duty
            self.direction = 0
            self.brake()
            # print("{0} is stationary\n".format(self.motorID))

    def getDirection(self):
        '''!  @brief                           Returns spinning motor direction.
           @details                            Returns spinning motor direction.
           @return                             Returns spinning motor direction.       
        '''
        return self.direction
    
    def getRunState(self):
        '''!  @brief                           Returns motor run state.
           @details                            Returns motor run state.
           @return                             Returns motor run state.      
        '''
        return self.isRunning
    
    def toggleRunState(self):
        '''!  @brief                           Toggles motor run state.
           @details                            Inverses motor run state.
        '''
        self.isRunning = not(self.isRunning)  
        
    def coast(self):
        '''!  @brief                           Sets motor duty cycle to zero.
           @details                            Both motor channels have duty cycles set to zero.
        '''
        self.channel1.pulse_width_percent(0)
        self.channel2.pulse_width_percent(0)
    
    def brake(self):
        '''!  @brief                           Applies 100% duty cycle to the motors.
           @details                            Both motor channels have duty cycles set to 100% to brake the motors quickly.
        '''
        self.channel1.pulse_width_percent(100)
        self.channel2.pulse_width_percent(100)
        
if __name__ == '__main__' :
    
    #This is the way to set the condition of the enable pin. Since it is an input, we do not change its value in code.
    # Instead, we check its value and write code to have the hardware either enable or disable based off of the input 
    # pin condition.  We need to refactor the existing code to make this possible and delete methods which attempt to
    # the value of the input.  Lastly, we need to connect an external power supply to the shield and apply ~ 10 volts
    # to spin the motor.
    enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
    #enable2 = pyb.Pin(pyb.Pin.cpu.C1, pyb.Pin.OUT_PP)

    #defining motor inputs
    # refactored for ME 405 hardware
    input1 = pyb.Pin.cpu.B4
    input2 = pyb.Pin.cpu.B5
    #input3 = pyb.Pin.cpu.A0
    #input4 = pyb.Pin.cpu.A1

    timer1 = pyb.Timer(3, freq = 20000)
    #timer2 = pyb.Timer(5, freq = 20000)

    #creating motor driver / motor objects
    # enable pin, input1, input2, timer
    m1_driver = MotorDriver(enable1, input1, input2, timer1)
    m1 = m1_driver.motor(input1, input2, 1, 2, "MOTOR A")
    #m2_driver = MotorDriver(enable2, input3, input4, timer2)
    #m2 = m2_driver.motor(input3, input4, 1, 2, "MOTOR B")
    
    # turning on the motor
    m1.set_duty(25)