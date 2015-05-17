from pygre import *
import struct

def Uniform16f():
    return Uniform(struct.pack('16f', 
                               1,0,0,0,
                               0,1,0,0,
                               0,0,1,0,
                               0,0,0,0))

class ScreenQuad(SceneObject):
    def __init__(self, layer, vShader, fShader):
        SceneObject.__init__(self, layer, vShader, fShader, Draw( 0x0004, 0, 6, None))
        a_position = Attribute(
            struct.pack ('12f', 
                         -1.0, -1.0,
                         1.0, -1.0,
                         -1.0, 1.0,
                         -1.0, 1.0,
                         1.0, -1.0,
                         1.0, 1.0)

            , 0x1406
            , 2
            , True
            )
        self.setAttribute("a_position", a_position)

