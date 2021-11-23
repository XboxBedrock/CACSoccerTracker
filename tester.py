import machine
import utime
import noise_filter

from mpu6500 import MPU6500

SDA = machine.Pin(0)
SCL = machine.Pin(1)

i2c = machine.I2C(0, scl=SCL, sda=SDA)
print(i2c.scan())

mpu6500 = MPU6500(i2c)

mpu6500.calibrate()

prev_vals = 0, 0, 0
i = 0
while i < 500:
    vals = mpu6500.acceleration
    vals = tuple(noise_filter.filter_accel(vals[i], prev_vals[i]) for i in range(len(vals)))
    print(vals)
    prev_vals = vals
    utime.sleep(0.1)
    i += 1
