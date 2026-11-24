from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

# Standard MicroPython modules
from usys import stdin, stdout
from uselect import poll

wheel_motor = Motor(Port.B)
dir_motor = Motor(Port.A)
dir_motor.reset_angle(0)
grb_motor = Motor(Port.D)
grb_motor.reset_angle(0)


# Optional: Register stdin for polling. This allows
# you to wait for incoming data without blocking.
keyboard = poll()
keyboard.register(stdin)

while True:

    # Let the remote program know we are ready for a command.
    stdout.buffer.write(b"rdy")

    # Optional: Check available input.
    while not keyboard.poll(0):
        # Optional: Do something here.
        wait(10)

    # Read three bytes.
    cmd = stdin.buffer.read(3)

    # Decide what to do based on the command.
    if cmd == b"mof": #move forward
        wheel_motor.dc(-50)
    elif cmd == b"mob": #move backwards
        wheel_motor.dc(50)
    elif cmd == b"mos": #stop moving
        wheel_motor.stop() 
    elif cmd == b"tur": #turn right
        dir_motor.dc(-30)
        wait(1)
        dir_motor.stop
    elif cmd == b"tul": #turn left
        dir_motor.dc(30)
        wait(1)
        dir_motor.stop
    elif cmd == b"res": #reset front wheel angle
        dir_motor.run_target(150, 0)
    elif cmd == b"grb": #grab
        grb_motor.run_target(300, 360)

        wait(500)

        wheel_motor.run(-200)
        wait(1000)
        wheel_motor.stop()

        wait(500)
        
        grb_motor.run_target(300, 0)
    elif cmd == b"bye":
        break
    else:
        wheel_motor.stop()

