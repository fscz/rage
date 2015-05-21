from pygre import *
import numpy
import math
import struct
import matrix as m
from helpers import Uniform16f

class PerspectiveCamera(object):
    def __init__(self, position=[0.0,0.0,0.0], rotation=[0.0,0.0,0.0], near=0.001, far=500.0, fov=90):
        screenWidth = Display.width
        screenHeight = Display.height

        h = 1 / math.tan(math.radians(fov/2.0))
        a = -(near + far) / (near - far)
        b = -(2 * far * near / (far - near))
        aspect = screenHeight / float(screenWidth)        

        self.__near = Uniform(struct.pack('f', near))
        self.__far = Uniform(struct.pack('f', far))
        self.__fov = fov
        self.__position = position
        self.__rotation = rotation
        rt2byrt3 = math.sqrt(2) / math.sqrt(3)
        rayX = math.cos(math.radians((180 - fov)/2.0)) * rt2byrt3
        rayY = math.sin(math.radians((180 - fov)/2.0)) * rt2byrt3
        rayZ = 1 / math.sqrt(3)
        self.__frustumrays = [
            -rayX, -rayY, rayZ,
             rayX, -rayY, rayZ,
            -rayX, rayY, rayZ,
             rayX, rayY, rayZ,
            ]
        self.__view = Uniform16f()
        self.__inv_view = Uniform16f()
        self.__update_view()

        self.__projection = Uniform (
                struct.pack('16f', 
                        h, 0.0, 0.0, 0.0,
                        0.0, h/aspect, 0.0, 0.0,
                        0.0, 0.0, a, 1.0,
                        0.0, 0.0, b, 0.0))

    def __update_view(self):
        self.view.update(
            (m.translate(-self.__position[0], -self.__position[1], -self.__position[2]) 
             * m.rotationX(-self.__rotation[0]) * m.rotationY(-self.__rotation[1]) * m.rotationZ(-self.__rotation[2])).flatten())
        self.inv_view.update((m.translate(self.__position[0], self.__position[1], self.__position[2]) 
             * m.rotationX(self.__rotation[0]) * m.rotationY(self.__rotation[1]) * m.rotationZ(self.__rotation[2])).flatten())
                            
    @property
    def position(self):
        return self.__position

    @position.getter
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):        
        self.__position = value
        self.__update_view()        

    @property
    def rotation(self):
        return self.__rotation

    @rotation.getter
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self, value):        
        self.__rotation = value
        self.__update_view()

    @property
    def near(self):
        return self.__near

    @near.getter
    def near(self):
        return self.__near

    @near.setter
    def near(self, value):
        self.__near = value
        self.__update_view()

    @property
    def far(self):
        return self.__far

    @far.getter
    def far(self):
        return self.__far

    @far.setter
    def near(self, value):
        self.__far = value
        self.__update_view()
    
    @property
    def frustumrays(self):
        return self.__frustumrays                            

    @frustumrays.getter
    def frustumrays(self):
        return self.__frustumrays

    @property
    def view(self):
        return self.__view

    @view.getter
    def view(self):
        return self.__view

    @property
    def inv_view(self):
        return self.__inv_view

    @inv_view.getter
    def inv_view(self):
        return self.__inv_view


    @property
    def projection(self):
        return self.__projection

    @projection.getter
    def projection(self):
        return self.__projection
