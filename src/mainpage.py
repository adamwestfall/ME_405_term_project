'''! @file                mainpage.py
   @brief               Mainpage for the ME 405 Automatic Nerf Gun Project
   @details             Includes the necessary Task Diagrams, FSM's, and Youtube link of our working Project.

   @mainpage
     
                          
   @section tst_rpz                     ME 405 Term Project Cover Page 
                                        This Documentation includes all necessary information and files for the Automatic Nerf Gun Project. <br>
       .
   @section abc_def                     Software Design 
                                        Below you will find an outline ofthe software design of the ME 405 autmatic nerf gun project. <br>
                                        A Task Diagram including Thermal Camera, Yaw Control, Pitch Control, and Gun Firing Actuation is included below. <br> 
                                        Attached you will see the associated Finite State Machines. <br>
                                        The files required to operate the automatic nerf gun are as follows. <br>
                                        Motor Control: closed_loop_controller.py, encoder.py, motor_driver.py <br>
                                        Camera Control: mlx_cam.py, __init__.py, calibration.py, image.py, regmap.py, utils.py<br>
                                        Code Cooperation: cotask.py,task_share.py <br>
                                        Documentation: mainpage.py <br>
                                        
                                        
   @subsection abc_qwe                  Thermal Camera 
                                        The thermal camera runs on I2C communciation and produces a heatmap. <br>
                                        By filtering the data based on a minimum temperature, an algorithim can easily find <br>
                                        the hottest and larget heat blob. This represents our target. <br>
                                        Using the field of view and length of the dueling table, a physical location can be deduced <br>
                                        from the camera's thermal image. <br>
   
   @subsection abc_qle                  Yaw Control 
                                        Yaw of the system is controlled through encoders and motors. <br>
                                        A timing belt ensures that an encoder value will produce the correct angle. <br>
                                        A proprtional closed loop controller allows us to tune the speed of the motor response. <br>
   
   @subsection abc_qii                  Pitch Control 
                                        Pitch of the system is controlled through encoders and motors. <br>
                                        A timing belt ensures that an encoder value will produce the correct angle. <br>
                                        A proprtional closed loop controller allows us to tune the speed of the motor response. <br>
   
   @subsection abc_qpo                  Gun Actuation Control 
                                        The gun fires nerf bullets by spinning two drums like a baseball pitching machine. <br>
                                        When the nerf gun is powered, we can toggle its DC motors to start spinning. <br>
                                        Once the motors are up to speed and ready to fire, we send a signal to the gun to <br>
                                        indicate Pin high on the plunger firing sequence. Here, the plunger will push the <br>
                                        foam dart into the firing drums. <br>
           
   @section fsm_tok     Task Diagrams and FSM's
                        <br>
                        Overall Task Diagram<br>
                        \image html task_diagram_task_diagram.png
                        <br>
                        Thermal Camera FSM <br>
                        \image html task_diagram_thermal_camera.png
                        <br>
                        Yaw Control FSM <br>
                        \image html task_diagram_yaw_control.png
                        <br>
                        Pitch Control FSM <br>
                        \image html task_diagram_pitch_control.png
                        <br>
                        Gun Actuation FSM <br>
                        \image html task_diagram_fire_nerf_gun.png
                        <br>
                        Start Button FSM <br>
                        \image html task_diagram_start_button.png
                        <br>
                        
                        
   @section fnl_www     Pitch and Yaw Demonstration
                        Video Link:
                        <br>
                        \htmlonly
                        <iframe width="560" height="315" src="https://youtube.com/shorts/QEfIl4nILfw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        \endhtmlonly
                        <br>
                        
    @section fnl_www     Thermal Camera Demonstration
                         Video Link:
                         <br>
                         \htmlonly
                         <iframe width="560" height="315" src="https://youtube.com/shorts/f9dJt45VfJc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                         \endhtmlonly
                         <br>
                        
                       
    
   @author              Adam Westfall, Jason Davis, Conor Fraser

   @copyright           License Info

   @date                March 20, 2023
'''