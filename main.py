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
START_STOP_BUTTON = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
STATUS_LED = machine.Pin(15, machine.Pin.OUT)
DEBUG_LED = machine.Pin(25, machine.Pin.OUT)
STATUS_LED.value(1)  # test
utime.sleep(1)  # test
STATUS_LED.value(0)
BUTTON_HANG = 0.5

FILE_DEBUGGING = False
# ----------------------------- #

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'


def get_size(filename):
    return os.stat(filename)[6]


def to_base64(num):
    lst = []
    while num:
        lst.append(num % 64)
        num = num//64
    res = ''
    for n in lst[::-1]:
        res += alphabet[n]

    while len(res) < 12:
        res = 'A'+res

    return res


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
print(i2c.scan())  # DEBUG

_ = mpu9250.MPU9250(i2c)  # opens bypass to access AK8963

mpu6500 = MPU6500(i2c)

try:
    with open('./magno_offset.txt', 'r') as f:
        offset_and_scale = list(map(float, f.read().split()))
        offset, scale = offset_and_scale[:3], offset_and_scale[3:]
        magno = AK8963(i2c, offset=offset, scale=scale)
except OSError:
    magno = AK8963(i2c, offset=MAGNO_OFFSET, scale=MAGNO_SCALE)

sensor = mpu9250.MPU9250(i2c, ak8963=magno, mpu6500=mpu6500)


while True:
    # not logging, checking if connected to app
    while START_STOP_BUTTON.value() != 1:
        DEBUG_LED.value(1)
        utime.sleep(0.1)
        DEBUG_LED.value(0)
        utime.sleep(0.1)
        # NOTE: inefficient, consider porting to select.poll()
        if select.select([sys.stdin], [], [], 0)[0]:
            msg = sys.stdin.readline().rstrip('\n')
            if msg == 'flash':
                for i in range(10):  # DEBUG
                    DEBUG_LED.value(1)
                    # STATUS_LED.value(1)
                    utime.sleep(0.1)
                    DEBUG_LED.value(0)
                    # STATUS_LED.value(0)
                    utime.sleep(0.1)
                sys.stdout.write("done")
            elif msg == 'calibmag':
                with open('magno_offset.txt', 'w') as f:
                    calib_data = magno.calibrate()
                    calib_data = calib_data[0] + calib_data[1]
                    f.write(' '.join(map(str, calib_data)))
                sensor = mpu9250.MPU9250(i2c, ak8963=magno, mpu6500=mpu6500)
            elif msg == 'issetup':
                if 'magno_offset.txt' in os.listdir():
                    sys.stdout.write("true")
                else:
                    sys.stdout.write("false")
            elif msg == 'sendfiles':
                STATUS_LED.value(1)
                utime.sleep(0.5)
                STATUS_LED.value(0)
                session_files = []
                try:
                    os.stat("./sessions")
                except OSError:
                    os.mkdir("./sessions")
                for fname in os.listdir('./sessions'):
                    if get_size(f'./sessions/{fname}'):
                        session_files.append(fname)
                    else:
                        os.remove(f'./sessions/{fname}')
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
                    with open(f'./sessions/{fname}', 'r') as f:
                        data = f.read()
                        sys.stdout.write(fname[:-4]+'\n')  # session timestamp
                        sys.stdout.write(data+'\n')  # session data
                    os.remove(f'./sessions/{fname}')

    STATUS_LED.value(1)
    print('waiting for calib')  # DEBUG

    utime.sleep(BUTTON_HANG)

    while START_STOP_BUTTON.value() != 1:
        continue

    mpu6500.calibrate()
    print('calibrated')

    STATUS_LED.value(0)

    try:
        os.stat("./sessions")
    except OSError:
        os.mkdir("./sessions")

    if FILE_DEBUGGING:
        try:
            os.stat("./test-sessions")
        except OSError:
            os.mkdir("./test-sessions")

    max_file_num = 0
    for fname in os.listdir('./sessions'):
        if fname.endswith('.txt'):
            max_file_num = max(max_file_num, int(fname[:-4]))

    if FILE_DEBUGGING:
        with open(f'./sessions/{max_file_num+1}.txt', 'w') as logfile, open(f'./test-sessions/{max_file_num+1}.txt', 'w') as testfile:
            while START_STOP_BUTTON.value() != 1:
                # 4 bytes per number (little-endian) that are converted to base-64
                reading = sensor.gyro + sensor.acceleration + \
                    (sensor.magnetic[1], sensor.magnetic[0], -sensor.magnetic[2])
                s = ustruct.pack('<' + 'f' * 9, *reading)
                num = int.from_bytes(s, 'big')
                num_base64 = to_base64(num)
                logfile.write(num_base64)
                testfile.write(f"{repr(reading)} {str(list(s))} {str(num)} {num_base64}\n")
                utime.sleep(1/SAMPLE_FREQ)
    else:
        with open(f'./sessions/{max_file_num+1}.txt', 'w') as logfile:
            while START_STOP_BUTTON.value() != 1:
                # 4 bytes per number (little-endian) that are converted to base-64
                logfile.write(to_base64(int.from_bytes(ustruct.pack('<'+'f'*9, *(sensor.gyro+sensor.acceleration
                                                                                 + (sensor.magnetic[1], sensor.magnetic[0], -sensor.magnetic[2]))), 'big')))
                utime.sleep(1/SAMPLE_FREQ)

    # NOTE: Consider changing hang time
    utime.sleep(BUTTON_HANG)  # so that one button press is not counted as multiple
