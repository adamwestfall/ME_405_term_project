# ME_405_term_project

Learn By Dueling

Authors:
Jason Davis
Adam Westfall
Conor Fraser


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


1.
The Electronically Actuated Dart Gun uses a design similar to a baseball pitching machine.
Two drums spun by a 12V DC motor grip onto a foam dart and accelerate it to a speed acceptable for firing.
These motors run constantly when the gun is in use, which confirms a bullet will be fired if actuated.
To adjust the default gun for the duel, auxillary power and data cords were wired through a hole in the base of the handle and soldered to the necessary connections. 
This allowed us to start and stop the gun motors as well as interact with the plunger based firing system without using the gun's physical buttons.

Auxillary power from the power supply and GPIO wires 
A rotating drum 
	



The mainpage.py file sets up doxygen to output screenshots of the necessary Task Diagrams and FSM's.
