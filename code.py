import machine
import utime
import mpu9250
import lp_filter

from ak8963 import AK8963
from mpu6500 import MPU6500
from vector import Vector3


SDA = machine.Pin(0)
SCL = machine.Pin(1)

i2c = machine.I2C(0, scl=SCL, sda=SDA)
print(i2c.scan())

_ = mpu9250.MPU9250(i2c)  # opens bypass to access AK8963

mpu6500 = MPU6500(i2c)
offset = mpu6500.calibrate(count=256, delay=0)


magno = AK8963(
    i2c,
    offset=(3.153517, 26.01416, -29.99121),
    scale=(0.9808451, 1.061359, 0.9631287)
)
sensor = mpu9250.MPU9250(i2c, ak8963=magno, mpu6500=mpu6500)

accel = 0
while True:
    #print(prev_val)
    #prev_val = lp_filter.filter_accl(Vector3(sensor.acceleration), prev_val)
    prev_accel = accel
    accel = sensor.acceleration[0]
    print((temp := lp_filter.filter_accl(accel, prev_accel)), accel)
    accel = temp
    utime.sleep(0.5)
