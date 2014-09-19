#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

lazer_measurements=[]

def neto_turn_right(rt_trn_amt):
    xspeed=0.3
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(float(rt_trn_amt),0.0,0.0)
    
    #Construct publish data:
    return Twist(speed,angular)
    
def neto_turn_left(lft_trn_amt):
    xspeed=0.3
    
    #make sure the robot will be turning left
    -1*lft_trn_amt if lft_trn_amt >0 else lft_trn_amt 
    speed=Vector3(float(xspeed),0.0,0.0) 
    angular=Vector3(float(lft_trn_amt),0.0,0.0)
    
    #Construct publish data:
    return Twist(speed,angular)
    
def wall_follow(pub):
    """Directs the robot to find a wall and follow it from the laser scann data. 
    does this by trying to keep the average of the right or left laser scan in range."""
    print 'hla'
    
    global lazer_measurements
    msg=lazer_measurements
    
    print 'type for the laser scan data', type(msg)
    print 'msg 1 element: ', msg
    rt_side_dist=[]
    d30ab=[] #Distance to wall from 30 degrees Above Beam
    d30bb=[] #", but Below Beam
    
    set_pt=.2 #distance from wall which the robot should keep
    dist_tol=.1 #tolerence of distance measurements
    angle_tol=.1 #tolerence of the angle of the robot WRT the wall
    
    turn_gain=.9
    
    #read in distances from robot to wall:
#    for i in range(88,93): #average dist to the right of the robot
#        if msg.ranges[i]>0:
#            rt_side_dist+=msg.ranges[i]
#            
#    for i in range(58,63): #average dist to 30 degrees above the beam of robot
#        if msg.ranges[i]>0:
#            d30ab+=msg.ranges[i]
#                
#    for i in range(118,123):
#        if msg.ranges[i]>0:
#            d30bb+=msg.ranges[i]
#            
#    if (rt_side_dist-set_pt)>dist_tol: #if the robot is too far from the wall:
#        trn_rt_amt=trun_gain*(rt_side_dist-set_pt)
#        pub.publish(neto_turn_right(trn_rt_amt))
    
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
    valid_ranges = []
    for i in range(10):
        print 'laser reading ',msg.ranges[i]
        if msg.ranges[i] > 0 and msg.ranges[i] < 8:
            valid_ranges.append(msg.ranges[i])
    if len(valid_ranges) > 0:
        mean_distance = sum(valid_ranges)/float(len(valid_ranges))
    global lazer_measurements
    print 'about to write to the laser global!'
    lazer_measurements=msg
    print 'Written: ', lazer_measurements
        
        #print mean_distance
    
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
