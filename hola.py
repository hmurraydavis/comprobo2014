#!/usr/bin/env python

import time
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

#global lazer_measurements
lazer_measurements=[]

def neto_turn_lft(lft_trn_amt):
    xspeed=0.3
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(float(lft_trn_amt),0.0,0.0)
    
    #Construct publish data:
    return Twist(speed,angular)
    
def neto_turn_rt(rt_trn_amt):
    xspeed=0.3
    
    #make sure the robot will be turning left
    -1*rt_trn_amt if rt_trn_amt >0 else rt_trn_amt 
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(float(rt_trn_amt),0.0,0.0)
    
    #Construct publish data:
    return Twist(speed,angular)
    
def wall_follow(pub):
    """Directs the robot to find a wall and follow it from the laser scann data. 
    does this by trying to keep the average of the right or left laser scan in range."""
    
    while lazer_measurements==[]: #wait for laser to start up:
        time.sleep(.1)
    
    print 'laser start'
    rt_side_dist=0.0
    d30ab= 0.0#Distance to wall from 30 degrees Above Beam
    d30bb=0.0 #", but Below Beam
    
    set_pt=1.5 #distance from wall which the robot should keep
    dist_tol=.1 #tolerence of distance measurements
    angle_tol=.1 #tolerence of the angle of the robot WRT the wall
    
    turn_gain=.9
    
    #read in distances from robot to wall:
    for i in range(88,93): #average dist to the right of the robot
        if lazer_measurements[i]>0:
            rt_side_dist+=lazer_measurements[i]
        #print 'raw beam: ', lazer_measurements[i]
    print 'rt sd ', rt_side_dist
            
    for i in range(58,63): #average dist to 30 degrees above the beam of robot
        if lazer_measurements[i]>0:
            d30ab+=lazer_measurements[i]
    print '30 degrees above =: ', d30ab
                
    for i in range(118,123):
        if lazer_measurements[i]>0:
            d30bb+=lazer_measurements[i]
        #print 'raw 30 degrees below: ', lazer_measurements[i]
    print '30 degrees below: ',d30bb
        
    #print 'conditional val: ', rt_side_dist-set_pt
    if (rt_side_dist-set_pt)>dist_tol: #if the robot is too far from the wall:
        print 'robot too far from wall'
        trn_rt_amt=turn_gain*(rt_side_dist-set_pt)
        pub.publish(neto_turn_rt(trn_rt_amt))
    
def avoid_obstacles():
    """Keeps the robot from hitting objects when trying to move forward."""
        


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
    #print 'ms rng', msg.ranges, '\n', '\n'
    #print 'type msg rng: ', type(list(msg.ranges))
    
    lazer_measurements=list(msg.ranges) #TODO
    #print 'lsr msg', lazer_measurements
    
    #lazer_measurements='hi'

    
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
            if state=='lazer':
                print 'In lazer mode!'
                #state =read_in_laser()
            #elif state == 'approach_wall':
            #    state = approach_wall(pub)
    except rospy.ROSInterruptException: pass
