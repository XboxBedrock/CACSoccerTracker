from math import sqrt


class Vector3:
    def __init__(self, x, y=None, z=None):
        if type(x) == tuple:
            x, y, z = x
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, n):
        return self.__class__(self.x*n, self.y*n, self.z *n)

    def __rmul__(self, n):
        return self * n

    def __add__(self, other):
        if type(other) == tuple:
            other = self.__class__(other)
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

    def __eq__(self, other):
        return tuple(self.x) == tuple(other)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __abs__(self):
        return sqrt(self.x**2+self.y**2+self.z**2)

    def __neg__(self):
        return self.__class__(-self.x, -self.y, -self.z)

    def __sub__(self, other):
        if type(other) == tuple:
            other = self.__class__(other)
        return self + (-other)

    def __truediv__(self, n):
        return self*(1/n)

    def __lt__(self, other):
        if type(other) == tuple:
            other = self.__class__(other)
        return abs(self) < abs(other)

    def __gt__(self, other):
        if type(other) == tuple:
            other = self.__class__(other)
        return abs(self) > abs(other)

    def __ge__(self, other):
        if type(other) == tuple:
            other = self.__class__(other)
        return abs(self) >= abs(other)

    def __le__(self, other):
        if type(other) == tuple:
            other = self.__class__(other)
        return abs(self) <= abs(other)

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __repr__(self):
        return 'Vector3'+str(self)
