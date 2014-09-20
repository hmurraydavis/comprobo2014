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


##Obstacle Avoid Behavior##
