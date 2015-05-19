# -*- coding: utf-8 -*-
from camera import PerspectiveCamera
from mesh import Mesh
from light import PointLight
from overlay import LightBuffer, NormalBuffer
from game import Game
from display import Display
import signal
import struct

class MyGame(Game):

    def __init__(self):
        Game.__init__(self)

        camera = PerspectiveCamera([0.0, 0.0, 0.0], near=0.001, far=500.0, fov=90)
        
        self.lion = Mesh("res/models/lion.obj", camera, position = [0, -5, 50], scale = 40.0)
        self.add(self.lion)
        
        colorWhite = [1.0, 1.0, 1.0]
        colorBlue = [0.0, 0.0, 1.0]
        colorGreen = [0.0, 1.0, 0.0]
        intensityWhite = 10.0
        intensityColor = 15.0

        self.add(PointLight([-50, -10, 0], camera, colorWhite, intensityWhite ))      
        self.add(PointLight([50, -10, 0], camera, colorWhite, intensityWhite ))
        self.add(PointLight([-10,50,50], camera, colorBlue, intensityColor ))
        self.add(PointLight([10,50,50], camera, colorGreen, intensityColor ))

        size = Display.width/2.0
        self.add(NormalBuffer(0,0, size, size/Display.aspect))
        self.add(LightBuffer(size,0,size, size/Display.aspect))

        def handle_sigint(signum, frame):
            self.stop()
        signal.signal(signal.SIGINT, handle_sigint)


    def update(self, overruns):
        self.lion.rotation = [0, (self.lion.rotation[1] + 1 + overruns) % 360, 0]
        

game = MyGame()
game.start()

