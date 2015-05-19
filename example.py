# -*- coding: utf-8 -*-
from camera import PerspectiveCamera
from mesh import Mesh
from light import PointLight, TubeLight
from game import Game
from display import Display
import signal
import struct

class MyGame(Game):

    def __init__(self):
        Game.__init__(self)

        camera = PerspectiveCamera([0.0, 0.0, 0.0], near=0.001, far=500.0, fov=90)
        
        self.lion = Mesh("res/models/lion.obj", camera, position = [0, -10, 50], scale = 40.0)
        self.add(self.lion)
        
        colorWhite = [1.0, 1.0, 1.0]
        colorBlue = [0.0, 0.0, 1.0]
        colorGreen = [0.0, 1.0, 0.0]
        intensityWhite = 10.0
        intensityColor = 15.0

        self.add(PointLight(camera, [-50, -10, 0], colorWhite, intensityWhite ))      
        self.add(PointLight(camera, [50, -10, 0], colorWhite, intensityWhite ))
        self.add(PointLight(camera, [-10,50,50], colorBlue, intensityColor ))
        self.add(PointLight(camera, [10,50,50], colorGreen, intensityColor ))
        self.laser = TubeLight(camera, [-50, 18.0, 25], [1.0, 0, 0], 10.0, 10.0, [1, 0, 0], 100)
        self.add(self.laser)    

        def handle_sigint(signum, frame):
            self.stop()
        signal.signal(signal.SIGINT, handle_sigint)


    def update(self, overruns):
        self.lion.rotation = [0, (self.lion.rotation[1] + 1 + overruns) % 360, 0]
        laserpos = self.laser.position[0]+2
        if laserpos > 50:
            laserpos = -50
        self.laser.position = [laserpos, self.laser.position[1], self.laser.position[2]]

game = MyGame()
game.start()

