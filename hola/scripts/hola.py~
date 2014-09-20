#!/usr/bin/env python

import time
import math
import rospy
import random
import operator
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

#global lazer_measurements
lazer_measurements=[]
xspeed=.1

def neto_turn_lft(lft_trn_amt):
    speed=Vector3(float(xspeed),0.0,0.0) 
    
    angular=Vector3(0.0,0.0,math.fabs(float(lft_trn_amt)))
    #print 'lft turn ', lft_trn_amt
    #Construct publish data:
    return Twist(speed,angular)
    
def neto_turn_rt(rt_trn_amt):
    #make sure the robot will be turning left
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(0.0,0.0,-1.0*float(math.fabs(rt_trn_amt)))
    #print 'rt_trn_amt ', rt_trn_amt
    #Construct publish data:
    return Twist(speed,angular)
    
def neto_move_fwd(): #have the neeto move forward in a straight line:
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(0.0,0.0,0.0)
    return Twist(speed,angular)
    
def objects_in_ft():
        lft_ft_scn = [x for x in lazer_measurements[:10] if x != 0]
        rt_ft_scn=lazer_measurements[-10:]
        rt_ft_scn=[x for x in lazer_measurements[-10:] if x != 0]
        qnty_nonzero_elements=len(lft_ft_scn)+len(rt_ft_scn)
        if qnty_nonzero_elements==0:
            return 0
        else:
            return (sum(lft_ft_scn)+sum(rt_ft_scn))/qnty_nonzero_elements #Avg degrees of scan data
    
def wall_follow(pub):
    """Directs the robot follow a wall on the left side from the laser scann data. 
    """
    
    print 'wall follow'
    while not rospy.is_shutdown():
        while lazer_measurements==[]: #wait for laser to start up:
            time.sleep(.1)
        
        lft_side_dist=0.0
        d30ab= 0.0#Distance to wall from 30 degrees Above Beam
        d30bb=0.0 #", but Below Beam
        
        set_pt=5.0 #distance from wall which the robot should keep
        dist_tol=0.3 #tolerence of distance measurements
        angle_tol=.8 #tolerence of the angle of the robot WRT the wall
        shitty_data_tol=.01
        
        turn_gain=0.4
        angle_gain=0.2
        
        #read in distances from robot to wall:
        for i in range(88,93): #average dist to the right of the robot
            if lazer_measurements[i]>0:
                lft_side_dist+=lazer_measurements[i]
                
        for i in range(58,63): #average dist to 30 degrees above the beam of robot
            if lazer_measurements[i]>0:
                d30ab+=lazer_measurements[i]
                    
        for i in range(118,123):
            if lazer_measurements[i]>0:
                d30bb+=lazer_measurements[i]
        
        #keep the robot the correct distance from the wall:    
        if ((lft_side_dist-set_pt)>dist_tol) and (lft_side_dist>shitty_data_tol): #if the robot is too far from the wall:
            trn_lft_amt=turn_gain*(lft_side_dist-set_pt)
            print 'FAR            ', 'LFT_DST: ', lft_side_dist
            pub.publish(neto_turn_lft(trn_lft_amt))
            
        elif ((lft_side_dist-set_pt)<dist_tol) and (lft_side_dist>shitty_data_tol): #if the robot is too close to the wall: TODO
            print 'CLOSE          ', 'LFT_DST: ',lft_side_dist
            trn_rt_amt=turn_gain*(set_pt-lft_side_dist)
            pub.publish(neto_turn_rt(trn_rt_amt))
        else:
            pub.publish(neto_move_fwd())
        
        #keep robot parallel to wall:    
        if math.fabs(lft_side_dist-set_pt)<2.5: #only try to get parallel to the wall when close to it
            if d30bb-d30ab<angle_tol: #case where it's heading toward the wall
                pub.publish(neto_turn_rt(angle_gain*(d30bb-d30ab)))
                print 'ANGLED--TOWARD'
            if d30ab-d30bb<angle_tol: #case where it's heading away from wall
                pub.publish(neto_turn_lft(angle_gain*(d30ab-d30bb)))
                print 'ANGLED--AWAY'
        time.sleep(.07)
                
       
        #yield control to master state keeper when needed:
        if objects_in_ft()<.4: #switch to obs avoid mode when it would hit things
            return 'obs_avoid'
            
            
            
def obs_avoid(pub):
    """Keeps the robot from hitting objects when trying to move forward."""
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
        
        if drc==1: #turn left to avoid obstacle
            pub.publish(neto_turn_rt(obs_avd_gn*(dist_tol-ft)))
        elif drc==-1: #turn right to avoid obstacle
            pub.publish(neto_turn_rt(obs_avd_gn*(dist_tol-ft))) #TODO make it turn rt too
        elif drc==0:
            pub.publish(neto_move_fwd)
        
        time.sleep(.1) #keeps sensor noise from making it gitter and reduces terminal output to a useful level
            
def obs_avd_2(pub):
    dist_tol=1.4
    min_gap=30
    
    if (ft<dist_tol):
        pass
    

def straight_line_mode(pub):
    pub.publish(neto_move_fwd)

def scan_received(msg):
    print 'in scan received'
    global distance_to_wall
    if len(msg.ranges) != 360:
        print 'unexpcted laser scan message'
        return

    valid_msgs = 0.0
    sum_valid = 0.0
    for i in range(5):
        if msg.ranges[i] > 0.1 and msg.ranges[i] < 7.0:
            valid_msgs += 1
            sum_valid += msg.ranges[i]
            print msg.ranges[i]
    if valid_msgs > 0:
        distance_tg_wall = sum_valid / valid_msgs
    else:
        distance_to_wall = -1
   
def read_in_laser(msg):
    """ Processes data from the laser scanner, msg is of type sensor_msgs/LaserScan """
    #print 'in read_in_laser'
    global lazer_measurements
    valid_ranges = []
    
    for i in range(10):
        #print 'laser reading ',msg.ranges[i]
        if msg.ranges[i] > 0 and msg.ranges[i] < 8:
            valid_ranges.append(msg.ranges[i])
    if len(valid_ranges) > 0:
        mean_distance = sum(valid_ranges)/float(len(valid_ranges))
#    print 'ms rng', msg.ranges, '\n', '\n'
    #print 'type msg rng: ', type(list(msg.ranges))
    
    lazer_measurements=list(msg.ranges)

    
def getch():
    """ Return the next character typed on the keyboard """
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
            if state=='straight_line_mode':
                state=straight_line_mode(pub)
            if state=='testing':
                while not rospy.is_shutdown():
                    pub.publish(neto_turn_rt(.4))
            #elif state == 'approach_wall':
            #    state = approach_wall(pub)
    except rospy.ROSInterruptException: pass

