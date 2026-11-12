from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.robotics import DriveBase

hub = InventorHub()
# ポートAに接続したモーターを1秒間正転させる
motor_b = Motor(Port.B)
motor_a = Motor(Port.A)


def move_forward(speed, time):
    
    motor_b.run(speed)
    wait(time)
    motor_b.stop()

    return True

def turn_left():
    


    motor_a.reset_angle(0)
    motor_a.run_target(300, 45)
    wait(1000)

    move_forward(500, 7000)

    motor_a.run_target(300, 0)

    return True

def grab():
    motor_d = Motor(Port.D)
    motor_b = Motor(Port.B)

    motor_d.run(250)
    wait(2500)
    

    wait(500)
    
    motor_b.run(-200)
    wait(1000)
    motor_b.stop()



    
    motor_d.run(-250)
    wait(2500)
    motor_d.stop()


turn_left()


