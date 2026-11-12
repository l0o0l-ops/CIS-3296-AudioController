from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.robotics import DriveBase

hub = InventorHub()
#back wheel
motor_b = Motor(Port.B)

#front wheel angle
motor_a = Motor(Port.A)
motor_a.reset_angle(0)

#arms
motor_d = Motor(Port.D)
motor_d.reset_angle(0)



def move(speed, time):
    
    motor_b.run(speed)
    wait(time)
    motor_b.stop()

    return True

def turn(angle):

    
    motor_a.run_target(300, angle)
    wait(1000)

    move(360, 3000)

    motor_a.run_target(300, 0)

    return True

def grab():
    
    motor_d.run_target(300, 360)
    

    wait(500)

    motor_b.run(-200)
    wait(1000)
    motor_b.stop()

    wait(500)
    
    motor_d.run_target(300, 0)
    

    return True

move(-360, 4000)
grab()
move(720, 4000)






