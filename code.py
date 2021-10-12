import math
import machine
import ustruct
import utime
import mpu9250

from madgwick_ahrs import MadgwickAHRS
from ak8963 import AK8963
from mpu6500 import MPU6500

SAMPLE_FREQ = 5

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

val = 0
madgwick = MadgwickAHRS()

with open(f'{int(utime.time())}.bin', 'wb') as logfile:
    while True:
        for val in sensor.acceleration+sensor.gyro+sensor.magnetic:
            logfile.write(ustruct.pack('e', val))
        utime.sleep(1/SAMPLE_FREQ)
