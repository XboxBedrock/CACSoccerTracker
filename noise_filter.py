import math

from vector import Vector3


'''  complementary + low-pass
if (Value < CompareValue - NP | Value > CompareValue + NP)
{
    FilteredValue = Value;
}
else
{
    if (Value < CompareValue - NPS | Value > CompareValue + NPS)
        {
            FilteredValue = (Value + PreviousCorrect)/2;
        }
    else
        {
            FilteredValue = (1 - NPL)*PreviousCorrect + NPL*Value;
        }
}
'''

"""  Prajwal's
f(d, variance) => x s.t.
x -> -variance as d ->  infty
x ->  variance as d -> -infty,

where d = val-prev_val

filter_val = measured_val + f(measured_val-prev_filter_val, variance)
"""

NP_ACCL = 0.119
NPS_ACCL = 0.0898
GAIN_ACCL = 0.025  # gain


def filter_accel(val, prev_val):
    if (val < (prev_val - NP_ACCL)) or (val > (prev_val + NP_ACCL)):
        res = val
    else:
        if (val < (prev_val - NPS_ACCL)) or (val > (prev_val + NPS_ACCL)):
            res = (val + prev_val)/2
        else:
            res = (1 - GAIN_ACCL) * prev_val + GAIN_ACCL * val

    if abs(res) > 0.06:
        return res
    else:
        return 0

# variance = 0.01
# k = 3

# def filter_accl(val, prev_val):
#     diff = val-prev_val
#     return val-variance*math.tanh(k*diff/(2*variance))


NP_MAG = 3
GAIN_MAG = 0.025  # gain

def filter_mag(val, prev_val):
    if (val < (prev_val - NP_MAG)) or (val > (prev_val + NP_MAG)):
        res = val
    else:
        res = (1 - GAIN_MAG) * prev_val + GAIN_MAG * val

    if abs(res) > 0.06:
        return res
    else:
        return 0


NP_GYRO = 0.267
GAIN_GYRO = 0  # gain


def filter_gyro(val):
    if (val < -NP_GYRO) or (val > NP_GYRO):
        res = val
    else:
        res = GAIN_GYRO * val

    if abs(res) > 0.06:
        return res
    else:
        return 0
