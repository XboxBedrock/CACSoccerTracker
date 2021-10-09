"""  complementary + low-pass
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
"""

"""  Prajwal's
f(d, variance) => x s.t.
x -> -variance as d ->  infty
x ->  variance as d -> -infty,

where d = val-prev_val

filter_val = measured_val + f(measured_val-prev_filter_val, variance)


variance = 0.01
k = 3

def filter_accl(val, prev_val):
    diff = val-prev_val
    return val-variance*math.tanh(k*diff/(2*variance))
"""


NP_ACCL = 0.119
NPS_ACCL = 0.0898
GAIN_ACCL = 0.025


def filter_accel(val, prev_val):
    if (val < (prev_val - NP_ACCL)) or (val > (prev_val + NP_ACCL)):
        return val
    elif (val < (prev_val - NPS_ACCL)) or (val > (prev_val + NPS_ACCL)):
        return (val + prev_val)/2
    else:
        return (1 - GAIN_ACCL) * prev_val + GAIN_ACCL * val


NP_MAG = 3.5  # thesis paper says 3, I noticed 3.5 while stationary though
GAIN_MAG = 0.025


def filter_mag(val, prev_val):
    if (val < (prev_val - NP_MAG)) or (val > (prev_val + NP_MAG)):
        return val
    return (1 - GAIN_MAG) * prev_val + GAIN_MAG * val


NP_GYRO = 0.267


def filter_gyro(val):
    if abs(val) < NP_GYRO:
        return val
    return 0
