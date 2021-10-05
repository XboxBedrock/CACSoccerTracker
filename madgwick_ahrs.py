"""
An implementation of https://github.com/morgil/madgwick_py without using

numpy: https://github.com/numpy/numpy

  OR

ulab (Micropython alternative to numpy): https://github.com/v923z/micropython-ulab.
"""

import math

from quaternion import Quaternion


def norm(x):
    """Returns Euclidean norm of a matrix.

    The Euclidean norm is defined as the square root of the sum of the squares
    of all elements.

    If `x` is a vector with dimension `n`, interprets as an `n x 1` matrix.

    :param x: matrix (as an iterable of iterables)
    :return: float
    """
    if not hasattr(x[0], '__iter__'):
        x = [x]

    res = 0
    for r in x:
        for i in r:
            res += i**2
    return math.sqrt(res)


def transpose(x):
    """Returns transpose of a matrix `x` (i.e. the matrix flipped over the LR
    diagonal).

    :param x: A matrix (list of lists).
    :return: An `n x m` matrix (where `x` is an `m x n` matrix)."""
    m, n = len(x), len(x[0])
    res = [[0]*m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            res[i][j] = x[j][i]
    return res


def mul(x, y):
    """Multiply two matrices or a matrix and a number.

    A vector with dimension `n` is interpreted as an `n x 1` matrix, unless the
    other argument is a number, in which case a vector is returned.

    :param x: A matrix (list of lists) or a number
    :param y: A matrix (list of lists) or a number
    :return:
        If `x` is an `a x b` matrix and `y` is a `b x c` matrix: an `a x c` matrix
        If `x` is an `a x b` matrix and `y` is a number (or vice versa): an `a x b` matrix
        If `x` is a number and `y` is a number: a number"""
    if hasattr(x, '__iter__') and hasattr(y, '__iter__'):  # matrix x matrix
        if not hasattr(x[0], '__iter__'):
            x = [x]
        if not hasattr(y[0], '__iter__'):
            y = [y]
        a, b = len(x), len(x[0])
        _b, c = len(y), len(y[0])
        if b != _b:
            raise ValueError('The number of columns of x should equal the number of rows of y')
        del _b

        res = [[0]*c for _ in range(a)]
        for i in range(a):
            for j in range(c):
                for k in range(b):
                    res[i][j] += x[i][k]*y[k][j]

        return res

    if not hasattr(x, '__iter__') and hasattr(y, '__iter__'):
        x, y = y, x
    if hasattr(x, '__iter__') and not hasattr(y, '__iter__'):  # matrix x num
        if not hasattr(x[0], '__iter__'):
            x = [x]
            vec = True
        else:
            vec = False
        a, b = len(x), len(x[0])
        res = [[0]*b for _ in range(a)]
        for i in range(a):
            for j in range(b):
                res[i][j] = x[i][j] * y
        if vec:
            return res[0]
        else:
            return res

    return x * y


class MadgwickAHRS:
    sample_period = 1/256
    quaternion = Quaternion(1, 0, 0, 0)
    beta = 0.082

    def __init__(self, sample_period_=None, quaternion_=None, beta_=None):
        """
        Initialize the class with the given parameters.
        :param sampleperiod: The sample period
        :param quaternion: Initial quaternion
        :param beta: Algorithm gain beta
        """
        if sample_period_ is not None:
            self.sample_period = sample_period_
        if quaternion_ is not None:
            self.quaternion = quaternion_
        if beta_ is not None:
            self.beta = beta_

    def update_9DOF(self, gyroscope, accelerometer, magnetometer):
        """
        Perform one update step with data from a AHRS sensor array.
        :param gyroscope: A three-element tuple containing the gyroscope data in
            radians per second.
        :param accelerometer: A three-element tuple containing the accelerometer
            data. Can be any unit since a normalized value is used.
        :param magnetometer: A three-element tuple containing the magnetometer
            data. Can be any unit since a normalized value is used.
        """
        q = self.quaternion

        # Normalize magnetometer measurement
        if norm(magnetometer) is 0:
            # TODO: find alternative to CPython warnings module
            # warnings.warn("magnetometer is zero")
            self.update_6DOF(gyroscope, accelerometer)
            return
        magnetometer = mul(magnetometer, 1/norm(magnetometer))

        # Normalize accelerometer measurement
        if norm(accelerometer) is 0:
            # TODO: find alternative to CPython warnings module
            # warnings.warn("accelerometer is zero")
            return
        accelerometer = mul(accelerometer, norm(accelerometer))

        # NOTE: Quaternion multiplication is non-commutative, do NOT remove the parentheses
        h = q * (Quaternion(0, magnetometer[0], magnetometer[1], magnetometer[2]) * q.conj())
        b = (0, norm(h[1:3]), 0, h[3])

        # Gradient descent algorithm corrective step
        f = [
            2*(q[1]*q[3] - q[0]*q[2]) - accelerometer[0],
            2*(q[0]*q[1] + q[2]*q[3]) - accelerometer[1],
            2*(0.5 - q[1]**2 - q[2]**2) - accelerometer[2],
            2*b[1]*(0.5 - q[2]**2 - q[3]**2) + 2*b[3]*(q[1]*q[3] - q[0]*q[2]) - magnetometer[0],
            2*b[1]*(q[1]*q[2] - q[0]*q[3]) + 2*b[3]*(q[0]*q[1] + q[2]*q[3]) - magnetometer[1],
            2*b[1]*(q[0]*q[2] + q[1]*q[3]) + 2*b[3]*(0.5 - q[1]**2 - q[2]**2) - magnetometer[2]
        ]
        J = [
            [-2*q[2],                  2*q[3],                  -2*q[0],                  2*q[1]                  ],
            [2*q[1],                   2*q[0],                  2*q[3],                   2*q[2]                  ],
            [0,                        -4*q[1],                 -4*q[2],                  0                       ],
            [-2*b[3]*q[2],             2*b[3]*q[3],             -4*b[1]*q[2]-2*b[3]*q[0], -4*b[1]*q[3]+2*b[3]*q[1]],
            [-2*b[1]*q[3]+2*b[3]*q[1], 2*b[1]*q[2]+2*b[3]*q[0], 2*b[1]*q[1]+2*b[3]*q[3],  -2*b[1]*q[0]+2*b[3]*q[2]],
            [2*b[1]*q[2],              2*b[1]*q[3]-4*b[3]*q[1], 2*b[1]*q[0]-4*b[3]*q[2],  2*b[1]*q[1]             ]
        ]
        step = mul(transpose(J), f)
        step = mul(step, 1/norm(step))  # normalize step magnitude

        # Compute rate of change of quaternion
        dq = (q * Quaternion(0, gyroscope[0], gyroscope[1], gyroscope[2])) * 0.5 - Quaternion(self.beta * transpose(step))

        # Integrate to yield quaternion
        q += dq * self.sample_period
        self.quaternion = Quaternion(q / norm(q))  # normalize quaternion

    def update_6DOF(self, gyroscope, accelerometer):
        """
        Perform one update step with data from a IMU sensor array
        :param gyroscope: A three-element array containing the gyroscope data in
            radians per second.
        :param accelerometer: A three-element array containing the accelerometer
            data. Can be any unit since a normalized value is used.
        """
        q = self.quaternion

        # Normalize accelerometer measurement
        if norm(accelerometer) == 0:
            # TODO: find alternative to CPython warnings module
            # warnings.warn("accelerometer is zero")
            return
        accelerometer = mul(accelerometer, 1/norm(accelerometer))

        # Gradient descent algorithm corrective step
        f = [
            2*(q[1]*q[3] - q[0]*q[2]) - accelerometer[0],
            2*(q[0]*q[1] + q[2]*q[3]) - accelerometer[1],
            2*(0.5 - q[1]**2 - q[2]**2) - accelerometer[2]
        ]
        J = [
            [-2*q[2], 2*q[3], -2*q[0], 2*q[1]],
            [2*q[1], 2*q[0], 2*q[3], 2*q[2]],
            [0, -4*q[1], -4*q[2], 0]
        ]
        step = mul(transpose(J), f)
        step = mul(step, 1/norm(step))  # normalize step magnitude

        # Compute rate of change of quaternion
        dq = (q * Quaternion(0, gyroscope[0], gyroscope[1], gyroscope[2])) * 0.5 - self.beta * transpose(step)

        # Integrate to yield quaternion
        q += dq * self.sample_period
        self.quaternion = q / norm(q)  # normalize quaternion
