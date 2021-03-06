#!/usr/bin/env python

import time
import math
import rospy
import random
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

#global lazer_measurements
lazer_measurements=[]
xspeed=.1

def neto_turn_lft(lft_trn_amt):
    '''Constructs an input that will make the robot turn left.
    INPUT: amout for robot to turn left
    OUTPUT: Twist data structure to make a robot move forward and turn left '''
    speed=Vector3(float(xspeed),0.0,0.0) 
    
    angular=Vector3(0.0,0.0,math.fabs(float(lft_trn_amt)))
    #print 'lft turn ', lft_trn_amt
    #Construct publish data:
    return Twist(speed,angular)
    
def neto_turn_rt(rt_trn_amt):
    '''Constructs an input that will make the robot turn right.
    INPUT: amout for robot to turn right
    OUTPUT: Twist data structure to make a robot move forward and turn right '''
    #make sure the robot will be turning left
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(0.0,0.0,-1.0*float(math.fabs(rt_trn_amt)))
    #print 'rt_trn_amt ', rt_trn_amt
    #Construct publish data:
    return Twist(speed,angular)
    
def neto_move_fwd(): #have the neeto move forward in a straight line:
    '''Constructs an input that will make the robot move forward at a set speed.
    INPUT: void
    OUTPUT: Twist data structure to make a robot move forward '''
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(0.0,0.0,0.0)
    return Twist(speed,angular)
    
def objects_in_ft():
    '''Checks to see if any objects are within a 20 degree radial propigation in
    front of the robot. If there are, it averages the nonzero values
    INPUT: void
    OUTPUT: float of the average distance to objects in front of the robot '''
    lft_ft_scn = [x for x in lazer_measurements[:10] if x != 0]
    rt_ft_scn=lazer_measurements[-10:]
    rt_ft_scn=[x for x in lazer_measurements[-10:] if x != 0]
    qnty_nonzero_elements=len(lft_ft_scn)+len(rt_ft_scn)
    if qnty_nonzero_elements==0:
        return 0
    else:
        return (sum(lft_ft_scn)+sum(rt_ft_scn))/qnty_nonzero_elements #Avg degrees of scan data

def angle_robot_wrt_wall(d30ab,d30bb,angle_tol):
    '''Checks the robots angle with respect to a wall. 
    INPUT: Distance to objects 30 degrees in front of off the robot's left side (60 degres from zero)
           Distance to objects 30 degrees bedhind off the robot's left side (120 degrees from zero)
           Angle tolerence for thresholding the justification of angle with respect to the wall]
    OUTPUT: Dictionary of form: {'angle_robot_wrt_wall': difference in the angled distances}
            if an unexpected error happens, it returns: {'error':0.0} but does not raise an error'''
    if (d30bb-d30ab)>angle_tol: #case where it's heading toward the wall
        return {'toward':(d30bb-d30ab)}
    elif (d30ab-d30bb)>angle_tol: #case where it's heading away from wall
        return {'away':(d30ab-d30bb)}           
    elif math.fabs(d30ab-d30bb) < angle_tol:
        return {'straight':(d30ab-d30bb)}
    else:
        return {'error':0.0}
    
def wall_follow(pub):
    """Directs the robot follow a wall on the left side from the laser scann data. 
    INPUT: node to which the robot should publish motion instructions
    OUTPUT: String of next state the robot should take
    """
    
    print 'wall follow'
    while not rospy.is_shutdown():
        while lazer_measurements==[]: #wait for laser to start up:
            time.sleep(.1)
        
        set_pt=2.0 #distance from wall which the robot should keep
        dist_tol=0.6 #tolerence of distance measurements
        angle_tol=.8 #tolerence of the angle of the robot WRT the wall
        shitty_data_tol=.01
        
        turn_gain=0.4
        angle_gain=0.2
        
        #read in distances from robot to wall:
        lft_side_dist=[x for x in lazer_measurements[88:93] if x != 0]
        if len(lft_side_dist)>0:
            lft_side_dist=sum(lft_side_dist)/len(lft_side_dist)
        else: 
            lft_side_dist=0
                
        d30ab=[x for x in lazer_measurements[58:63] if x != 0] #Distance to wall from 30 degrees Above Beam
        if len(d30ab)>0:
            d30ab=sum(d30ab)/len(d30ab)
        else:
            d30ab=0
                        
        d30bb=[x for x in lazer_measurements[118:123] if x != 0] # " " " ", but Below Beam
        if len(d30bb)>0:
            d30bb=sum(d30bb)/len(d30bb)
        else:
            d30bb=0
        
        #keep the robot the correct distance from the wall:    
        if ((lft_side_dist-set_pt)>dist_tol) and (lft_side_dist>shitty_data_tol): #if the robot is too far from the wall:
            trn_lft_amt=turn_gain*(lft_side_dist-set_pt)
            print 'FAR            ', 'LFT_DST: ', lft_side_dist
            pub.publish(neto_turn_lft(trn_lft_amt))
            
        elif ((lft_side_dist-set_pt)<dist_tol) and (lft_side_dist>shitty_data_tol): #if the robot is too close to the wall
            print 'CLOSE          ', 'LFT_DST: ',lft_side_dist
            trn_rt_amt=turn_gain*(set_pt-lft_side_dist)
            pub.publish(neto_turn_rt(trn_rt_amt))
        else:
            pub.publish(neto_move_fwd())
        
        #keep robot parallel to wall:    
        if math.fabs(lft_side_dist-set_pt)<2.5: #only try to get parallel to the wall when close to it
            angle_robot=angle_robot_wrt_wall(d30ab,d30bb,angle_tol)
            if 'toward' in angle_robot:
                pub.publish(neto_turn_rt(angle_gain*angle_robot['toward']))
                print 'ANGLED--TOWARD'
            elif 'away' in angle_robot:
                pub.publish(neto_turn_lft(angle_robot['away']))
                print 'ANGLED--AWAY'
            elif 'straight' in angle_robot:
                pub.publish(neto_move_fwd())

        time.sleep(.5)
                
        #yield control to master state keeper when needed:
        if objects_in_ft()<.4: #switch to obs avoid mode when it would hit things
            return 'obs_avoid'         
            
def obs_avoid(pub):
    """Keeps the robot from hitting objects when trying to move forward.
    INPUT: node to which the robot should publish motion instructions
    OUTPUT: String of next state the robot should take
    """
    print 'obs avoid'
    trn_drc=0
    
    while not rospy.is_shutdown():
        while lazer_measurements==[]: #wait for laser to start up:
            time.sleep(.1)
            
        obs_avd_gn=2.0
        dist_tol=1.1 #not the same as wall following so they can be tuned sepratly
        ft=objects_in_ft()
        
        if (ft<dist_tol) and (ft > 0): #something in ft of robot
            if trn_drc==0:
                drc=random.randrange(100)%2
                if drc==0:
                    drc=-1            
        else:
            return 'wall_follow'
        
        #this is from the turn direction was random
        if drc==1: #turn left to avoid obstacle
            pub.publish(neto_turn_rt(obs_avd_gn*(dist_tol-ft)))
        elif drc==-1: #turn right to avoid obstacle
            pub.publish(neto_turn_rt(obs_avd_gn*(dist_tol-ft)))
        elif drc==0:
            pub.publish(neto_move_fwd)
        
        time.sleep(.1) #keeps sensor noise from making it gitter and reduces terminal output to a useful level
   
def read_in_laser(msg):
    """ Processes data from the laser scanner and makes it available to other functions
    INPUT: The data from a single laser scan_received
    OUTPUT: 
    **Writes laser scan data to the global variable: lazer_measurements"""

    global lazer_measurements
    valid_ranges = []
    
    for i in range(10):
        #print 'laser reading ',msg.ranges[i]
        if msg.ranges[i] > 0 and msg.ranges[i] < 8:
            valid_ranges.append(msg.ranges[i])
    if len(valid_ranges) > 0:
        mean_distance = sum(valid_ranges)/float(len(valid_ranges))
    
    lazer_measurements=list(msg.ranges)

def getch():
    """ Return the next character typed on the keyboard 
    INPUT: void
    OUTPUT: String of he first typed key character
    **Waits until a character is received to exit and return"""
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
    
def teleop(pub):
    ''' Provides functionality for a teleoperated mode for testing purposes. 
    While there is no way to get into this mode under normal operation, it can 
    be set initially in the name=='__main__' function.
    INPUT: The node to which to publish movement messages 
    OUTPUT: none'''
    r = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        ch = getch()
        print ch
        if ch == 'i':
            msg = Twist(Vector3(2.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
            print "in i"
        elif ch == 'k':
            msg = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
        elif ch == ',':
            msg=Twist(Vector3(-2.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
        elif ch == 'j':
            msg = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 1))
        elif ch == 'q':
            break
        else :
            print 'unknown character'
            continue
        pub.publish(msg)
        print"pub mesg",msg
        r.sleep()
        
if __name__ == '__main__':
    '''Initializes ROS processes and controls the state of the robot once 
    indivigual behaviors yield controls
    INPUT: none
    OUTPUT: none'''
    try:
        rospy.init_node('my_fsm', anonymous=True)
        pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        sub = rospy.Subscriber('scan', LaserScan, read_in_laser)
        state = "wall_follow"

        while not rospy.is_shutdown():
            if state == 'teleop':
                state = teleop(pub)
            if state=='wall_follow':
                state=wall_follow(pub)
            if state=='obs_avoid':
                state=obs_avoid(pub)
            if state=='testing':
                #put test code here:
                break
    except rospy.ROSInterruptException: pass

