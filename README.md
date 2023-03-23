# ME_405_term_project

Learn By Dueling

Authors: Jason Davis, Adam Westfall, Conor Fraser


Overview:

The ME 405 Term Project consisted of altering a manually operated toy NERF dart gun into a automated heat seeking turret.
We were tasked with implementing a targetting, aiming, and firing system that would allow our turret to eliminate an enemy before the enemy eliminated us. 
The winner of the duel would be the first turret to land a "hit" on the opponent across a long table.
The first five seconds of the bout would be a period of movement where each human target could move back and forth between the edges of the table.
The second five seconds of the bout would be a frozen period where each human target was required to stand still.
Any missed shots would count against the turret and any repeated shots after the first hit would count for nothing.
The goal was to create an automatic sniper turret that would fire once and hit the target in the quickest time possible.
This turret can be used to entertain kids, teens, adults, and engineers.


Hardware Design:


![Alt text, alt right, alt left](md_front_view_png.png)
Figure 1. Shows the front view of the physical system.

![Alt text, alt right, alt left](md_side_view_1_png.png)
Figure 2. Shows a side view of the physical system.

![Alt text, alt right, alt left](md_side_view_2_png.png)
Figure 3. Shows another side view of the physical system.


Our design focused on reliability, speed, and precision.
We utulized the entire allotted physical space to create a stable platform rated for the large interia's being shifted.
The following parts list contains the major components that dictated our hardware design.


Parts List:
1.	Electronically Actuated Dart Gun
2.	Gun Magazine
3.	24V DC Motor used for Yaw control
4.	24V DC Motor used for Pitch control
5.	Emergency Stop Button
6.	Start/Stop/Reset Button
7.	Indicator LED's
8.	Lazy Susan Turn Table
9.	Baseplate
10.	A-Frame Support


The Electronically Actuated Dart Gun uses a design similar to a baseball pitching machine.
Two drums spun by a 12V DC motor grip onto a foam dart and accelerate it to a speed acceptable for firing.
These motors run constantly when the gun is in use, which confirms a bullet will be fired if actuated.
To adjust the default gun for the duel, auxillary power and data cords were wired through a drilled hole in the base of the handle and soldered to the necessary connections. 
This allowed us to start and stop the gun motors as well as interact with the plunger based firing system without using the gun's physical buttons.


The default gun relied on a belt fed rotating drum to supply the rollers with ammunition.
The belt did not fit in the A-frame support systems so a 3D printed magazine was designed and printed.
It slides into the top portion of the nerf gun and has a clip to stay secure. 

![Alt text, alt right, alt left](CAD_Gun.png)
Figure 4. Shows the CAD model for the Magazine.


A 24V DC motor provided the necessary speed and torque for yaw control.
Using a timing belt sourced from McMaster Carr allows the encoders on the motor to turn the motors to a consistent theta value.
Without the timing belt, setting angles such as 180 degrees would not be feasible.


A 24V DC motor was also used to provide the necessary speed and torque for the pitch control.
The pitch was also controlled by a timing belt since it allows for precise angle control.


All robotic systems are at risk for malfunction and endangerment of the user, so it is imperative to include fail safes.
An emergency stop button breaks the circuit that connects the aftermentioned yaw, pitch, and gun motors to the power supply.


To prevent the overuse of the emergency stop button, a black start/stop/reset button implemented into the control panel allows a user to safely start and stop the gun's automation.


Indicator LED's on the control panel allow a user to diagnose the power state of the nerf gun and motors.


A "lazy susan" style turntable	








Auxillary power from the power supply and GPIO wires 
A rotating drum 
	



The mainpage.py file sets up doxygen to output screenshots of the necessary Task Diagrams and FSM's.
