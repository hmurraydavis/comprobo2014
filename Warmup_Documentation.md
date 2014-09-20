#Warmup Project#

##Overview and Objectives##
This was written as a homework assignment for [Computational Robotics](https://sites.google.com/site/comprobofall14/home) at Olin College. The objective of the assignment was to gain familarity working wih [ROS](http://www.ros.org/), implemennt a finite state controler, and develop behaviors for a robot. This was achieved by iniating the nodes and subscribes for ROS, then progressing into a finite state controler which governed which behavior the robot opperated in at a given time. 

##Finite State Controler##
The finite state controler was implemented by initially setting the state of the robot's behavior shortly after ROS's services were iniated. From here, the behaviors passed code back to the main controler when defined events occured. This managed the act of switching the robot's state to the appropriate mode. In pseudo code:

'''
  behavor1() {
    while (shutdown==False){
      act on behavior 1
      
      if (eventA==True){
        return 'behavor2'
      }
    }
  }
  
  behavor2(){
    while (shutdown==False){
      act on behavor 2
      
      if (eventB==True){
        return 'behavor1
      }
    }
  }
  
  init(){
    iniatiate ROS services
    
    'state'=behavor1
    
    while (shutdown==False){
      if (state=='behavor1){
        behavor1()
      }
      
      if (state=='behavor2'){
        state=='behavor2'
      }
    }
  }
'''

From this, it is easy to see the flow of the code. Control of state initially relys on the init function; however, the indivigual behavors will be executed by the robot until the break conditions are met causing the behavor functions to exit. When this occurs, control of state regresses to the init function. 

##Wall Follow Behavor##
Wall following is the default mode of the robot. To wall follow, the robot first makes sure there's a wall close to directly off it's side. Then, if this wall is an acceptable length from the robot's side, it will attempt to make itself more parallel with the wall. To do this, it taes distance reaings at 30 degrees above and behind directly off its side. If these two lengths are the same, then the robot considers itself perfect and continues along its merry way. If not, it turns accordingly. To determine how much to turn, it simply takes the difference of the two lengths and multiplies this difference by a gain. While the angle of the robot with respect to the wall can be determined from two laser scans with the law of cosigns since these form a non-right SAS triangle (two known side lengths and the included angle), this method is trivally more computationally intensive and does not produce any real benefit over calculating the robot's angle with respect to the wall. That angle must then be forward integrated across the timestep between computations to correctly position the robot, or it must me multiplied by a gain, as I did with my difference. Therefore, it has few advantages besides providing the humans working with the robot with more intuitive units with which to work.

##Obstacle Avoid Behavior##
