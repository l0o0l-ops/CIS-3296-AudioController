from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

hub = InventorHub()
# ポートAに接続したモーターを1秒間正転させる
motor_a = Motor(Port.B)
motor_a.run(500)
wait(1000)
motor_a.stop()