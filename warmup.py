import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

def wall_follow():
    """Directs the robot to find a wall and follow it from the laser scann data. 
    does this by trying to keep the average of the right or left laser scan in range."""
    
    for i in range(88,93):
        wallDist+=msg.ranges[i]
    
    
    
def avoid_obstacles():
    """Keeps the robot from hitting objects when trying to move forward."""
    
    
def read_in_laser(msg):
    """ Processes data from the laser scanner, msg is of type sensor_msgs/LaserScan """
    valid_ranges = []
    for i in range(5):
        if msg.ranges[i] > 0 and msg.ranges[i] < 8:
            valid_ranges.append(msg.ranges[i])
    if len(valid_ranges) > 0:
        mean_distance = sum(valid_ranges)/float(len(valid_ranges))
        
        print mean_distance
    print "scan received"
    
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
    
def teleop():
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    sub = rospy.Subscriber('scan', LaserScan, scan_received)
    rospy.init_node('teleop', anonymous=True)
    r = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        ch = getch()
        if ch == 'i':
            msg = Twist(Vector3(0.2, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
        elif ch == 'k':
            msg = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
        elif ch == 'j':
            msg = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 1))
        elif ch == 'q':
            break
        pub.publish(msg)
        r.sleep()
        
if __name__ == '__main__':
    try:
        rospy.init_node('my_fsm', anonymous=True)
        pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        sub = rospy.Subscriber('scan', LaserScan, scan_received)
        state = "teleop"

        while not rospy.is_shutdown():
            if state == 'teleop':
                state = teleop(pub)
            #elif state == 'approach_wall':
            #    state = approach_wall(pub)
    except rospy.ROSInterruptException: pass

