from vector import Vector3

'''
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

NP_ACCL = 0.15
NPS_ACCL = 0.1
NPL_ACCL = 0.02  # gain


def filter_accl(val, prev_val):
    if (val < (prev_val - NP_ACCL)) or (val > (prev_val + NP_ACCL)):
        return val
    else:
        if (val < (prev_val - NPS_ACCL)) or (val > (prev_val + NPS_ACCL)):
            return (val + prev_val)/2
        else:
            return (1 - NPL_ACCL) * prev_val + NPL_ACCL * val


NP_MAG = 3
NPS_MAG = 3
NPL_MAG = 0.025  # gain


def filter_mag(val, prev_val):
    if (val < (prev_val - NP_MAG)) or (val > (prev_val + NP_MAG)):
        return val
    else:
        if (val < (prev_val - NPS_MAG)) or (val > (prev_val + NPS_MAG)):
            return (val + prev_val)/2
        else:
            return (1 - NPL_MAG) * prev_val + NPL_MAG * val


NP_GYRO = 0.267
NPS_GYRO = 0.267
NPL_GYRO = 0  # gain


def filter_gyro(val):
    if (val < -NP_GYRO) or (val > NP_GYRO):
        return val
    else:
        if (val < -NPS_GYRO) or (val > NPS_GYRO):
            return val/2
        else:
            return NPL_GYRO * val
