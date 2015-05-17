import numpy
import math
import struct

class Matrix:
    def __init__(self, m):
        self.m = numpy.array(m)

    def __mul__(self, other):
        return Matrix(numpy.dot(self.m, other.m))

    def flatten(self):
        return struct.pack('16f', *numpy.ndarray.flatten(self.m, 'F'))

    def invert(self):
        return Matrix(numpy.linalg.inv(self.m))

    def __str__(self):
        return str(self.flatten())

def mul(*args):
    ll = list(args)
    return reduce(lambda a, b: a * b, ll, identity)

identity = Matrix(
        [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        ]
)

def rotationX(degrees):
    angle = math.radians(degrees)
    return Matrix(
        [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, math.cos(angle), -math.sin(angle), 0.0],
        [0.0, math.sin(angle), math.cos(angle), 0.0],
        [0.0, 0.0, 0.0, 1.0]
        ]
)

def rotationY(degrees):
    angle = math.radians(degrees)
    return Matrix(
        [
        [math.cos(angle), 0.0, math.sin(angle), 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-math.sin(angle), 0.0, math.cos(angle), 0.0],
        [0.0, 0.0, 0.0, 1.0]
        ]
          
)


def rotationZ(degrees):
    angle = math.radians(degrees)
    return Matrix(
        [
        [math.cos(angle), math.sin(angle), 0.0, 0.0],
        [-math.sin(angle), math.cos(angle), 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
        ]
)

def scale(factor):
    return Matrix(
        [
        [factor, 0.0, 0.0, 0.0],
        [0.0, factor, 0.0, 0.0],
        [0.0, 0.0, factor, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        ]
)

def translate(x, y, z):
    return Matrix(
        [
        [1.0, 0.0, 0.0, x],
        [0.0, 1.0, 0.0, y],
        [0.0, 0.0, 1.0, z],
        [0.0, 0.0, 0.0, 1.0],
        ]
)
