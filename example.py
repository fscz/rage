# -*- coding: utf-8 -*-
from pygre import *
from camera import PerspectiveCamera
from mesh import Mesh
from light import RadialLight
from overlay import LightBuffer, NormalBuffer
import signal
import struct

class MyScene(Scene):

    def __init__(self):
        Scene.__init__(self)

        camera = PerspectiveCamera([0.0, 0.0, 0.0], near=0.001, far=500.0, fov=90)
        
        self.lion = Mesh("res/models/lion.obj", camera, position = [0, -10, 50], scale = 40.0)
        self.add(self.lion)
        
        colorWhite = Uniform(struct.pack('3f', 1.0, 1.0, 1.0))
        colorBlue = Uniform(struct.pack('3f', 0.0, 0.0, 1.0))
        colorGreen = Uniform(struct.pack('3f', 0.0, 1.0, 0.0))
        whiteIntensity = Uniform(struct.pack('1f', 15.0))
        colorIntensity = Uniform(struct.pack('1f', 30.0))

        self.add(RadialLight(Uniform(struct.pack('3f', -50.0, -10.0, 0.0)), camera, colorWhite, whiteIntensity ))      
        self.add(RadialLight(Uniform(struct.pack('3f', 50.0, -10.0, 0.0)), camera, colorWhite, whiteIntensity ))
        self.add(RadialLight(Uniform(struct.pack('3f', -10.0, 50.0, 50.0)), camera, colorBlue, colorIntensity ))
        self.add(RadialLight(Uniform(struct.pack('3f', 10.0, 50.0, 50.0)), camera, colorGreen, colorIntensity ))

        size = Display.width/2.0
        self.add(NormalBuffer(0,0, size, size/Display.aspect))
        self.add(LightBuffer(size,0,size, size/Display.aspect))

        def handle_sigint(signum, frame):
            self.stop()
        signal.signal(signal.SIGINT, handle_sigint)


    def update(self, overruns):
        self.lion.rotation = [0, (self.lion.rotation[1] + 1 + overruns) % 360, 0]
        

scene = MyScene()
scene.start()

