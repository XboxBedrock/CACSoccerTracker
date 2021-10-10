import machine
import ustruct
import utime
import mpu9250

from ak8963 import AK8963
from mpu6500 import MPU6500


# ---------- OPTIONS ---------- #
SAMPLE_FREQ = 5

PRAJWAL = True

SDA = machine.Pin(0)
SCL = machine.Pin(1)
START_STOP_BUTTON = machine.Pin(13)
CALIB_BUTTON = machine.Pin(14)
STATUS_LED = machine.Pin(15, machine.Pin.OUT)
STATUS_LED.value(0)
# ----------------------------- #


PRAJWAL_MAGNO_OFFSET = (29.04609, 34.06641, -52.03125)
SUSHRUT_MAGNO_OFFSET = (3.153517, 26.01416, -29.99121)
PRAJWAL_MAGNO_SCALE = (0.9980365, 1.032012, 0.9717683)
SUSHRUT_MAGNO_SCALE = (0.9808451, 1.061359, 0.9631287)

if PRAJWAL:
    MAGNO_OFFSET = PRAJWAL_MAGNO_OFFSET
    MAGNO_SCALE = PRAJWAL_MAGNO_SCALE
else:
    MAGNO_OFFSET = SUSHRUT_MAGNO_OFFSET
    MAGNO_SCALE = SUSHRUT_MAGNO_SCALE


i2c = machine.I2C(0, scl=SCL, sda=SDA)
print(i2c.scan())

_ = mpu9250.MPU9250(i2c)  # opens bypass to access AK8963

mpu6500 = MPU6500(i2c)

magno = AK8963(i2c, offset=PRAJWAL_MAGNO_OFFSET, scale=PRAJWAL_MAGNO_SCALE)
sensor = mpu9250.MPU9250(i2c, ak8963=magno, mpu6500=mpu6500)


while True:
    while START_STOP_BUTTON.value() != 1:
        continue

    STATUS_LED.value(1)

    while CALIB_BUTTON.value() != 1:
        continue

    mpu6500.calibrate()

    STATUS_LED.value(0)

    with open(f'{int(utime.time())}.bin', 'wb') as logfile:
        while START_STOP_BUTTON.value() != 1:
            for val in sensor.acceleration+sensor.gyro+sensor.magnetic:
                logfile.write(ustruct.pack('f', val))
            utime.sleep(1/SAMPLE_FREQ)

    utime.sleep(0.5)
