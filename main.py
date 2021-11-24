import os
import sys
import select
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
# CALIB_BUTTON = machine.Pin(14)
STATUS_LED = machine.Pin(15, machine.Pin.OUT)
STATUS_LED.value(1)  # test
utime.sleep(1)  # test
STATUS_LED.value(0)
# ----------------------------- #

PRAJWAL_MAGNO_OFFSET = (29.04609, 34.06641, -52.03125)
SUSHRUT_MAGNO_OFFSET = (3.153517, 26.01416, -29.99121)
PRAJWAL_MAGNO_SCALE = (0.9980365, 1.032012, 0.9717683)
SUSHRUT_MAGNO_SCALE = (0.9808451, 1.061359, 0.9631287)
PRAJWAL = True

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

if os.path.exists('./magno_offset.txt'):
    with open('./magno_offset.txt', 'r') as f:
        magno = AK8963(i2c, offset=tuple(map(float, f.read().split())), scale=MAGNO_SCALE)
else:
    magno = AK8963(i2c)

sensor = mpu9250.MPU9250(i2c, ak8963=magno, mpu6500=mpu6500)

print(START_STOP_BUTTON.value())  # DEBUG
while True:
    # not logging, checking if connected to app
    while START_STOP_BUTTON.value() != 1:
        # NOTE: inefficient, consider porting to select.poll()
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            msg = sys.stdin.readline().rstrip('\n')
            if msg == 'flash':
                STATUS_LED.value(1)
                utime.sleep(0.5)
                STATUS_LED.value(0)
                sys.stdout.write("done")
            elif msg == 'calibmag':
                with open('magno_offset.txt', 'w') as f:
                    f.write(str(' '.join(map(str, magno.calibrate()))))
                sensor = mpu9250.MPU9250(i2c, ak8963=magno, mpu6500=mpu6500)
            elif msg == 'issetup':
                is_setup = 'magno_offset.txt' in os.listdir()
                sys.stdout.write("true" * int(is_setup) + "false" * int(not is_setup))
            elif msg == 'sendfiles':
                STATUS_LED.value(1)
                utime.sleep(0.5)
                STATUS_LED.value(0)
                session_files = []
                if os.path.exists("./sessions"):
                    for fname in os.listdir('./sessions'):
                        # if os.path.getsize() doesn't work, use os.stat().st_size
                        if os.path.getsize(fname):
                            session_files.append(fname)
                    # try:
                    #     with open(fname, 'r') as f:
                    #         data = f.read()
                    #         if data:
                    #             sys.stdout.write(fname[:-4])  # session timestamp
                    #             sys.stdout.write(data)    # session data
                    # except Exception as err:
                    #     try:
                    #         sys.stdout.write(data)
                    #         sys.stdout.write(fname)
                    #         sys.stdout.write(err)
                    #     except NameError:
                    #         print("'data' was not defined")
                    sys.stdout.write(str(len(session_files))+'\n')
                    for fname in session_files:
                        with open(fname, 'r') as f:
                            data = f.read()
                            sys.stdout.write(fname[:-4]+'\n')      # session timestamp
                            sys.stdout.write(str(len(data))+'\n')  # number of bytes in data
                            sys.stdout.write(data)                 # session data

    STATUS_LED.value(1)

    while START_STOP_BUTTON.value() != 1:
        continue

    mpu6500.calibrate()

    STATUS_LED.value(0)

    with open(f'./sessions/{int(utime.time())}.bin', 'wb') as logfile:
        while START_STOP_BUTTON.value() != 1:
            # 4 bytes per number
            logfile.write(ustruct.pack('f'*9, sensor.acceleration+sensor.gyro+sensor.magnetic))
            utime.sleep(1/SAMPLE_FREQ)

    # NOTE: Consider changing hang time
    utime.sleep(0.5)  # so that one button press is not counted as multiple
