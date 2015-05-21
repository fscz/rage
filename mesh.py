import pygre
import matrix as m
from helpers import *
import struct
from obj import Obj


screen_size = pygre.Display.size
screenWidth = float(screen_size[0])
screenHeight = float(screen_size[1])


#####################################################
########################### Mesh
#####################################################

vShaderMesh = '''
    attribute vec4 a_position;
    attribute vec3 a_normal;
    uniform mat4 u_proj;
    uniform mat4 u_view;
    uniform mat4 u_world;
    varying vec3 v_normal;
    void main()                  
    {                            
       gl_Position = u_proj * u_view * u_world * a_position;  
       vec4 normal = vec4(a_normal, 0.0);
       v_normal = normalize((u_view * u_world * normal).rgb);
    }                            '''

fShaderMesh = '''
    varying vec3 v_normal;
    uniform sampler2D s_lightbuffer;
    uniform vec2 u_vpsize;
    void main()                                  
    {                                            
      vec2 texcoord = gl_FragCoord.xy / u_vpsize;
      vec4 sample = texture2D(s_lightbuffer, texcoord);
      float pos4 = v_normal.y == 0.0 ? 1.0 : v_normal.y / v_normal.y;
      gl_FragColor = vec4(vec3(0.1, 0.1, 0.1)+sample.xyz, 1.0);
    }                                            '''

class Mesh(pygre.SceneObject):

    def __init__(self, vertices, normals, camera, position=[0.0, 0.0, 0.0], rotation=[0.0,0.0,0.0], scale=1.0):
        pygre.SceneObject.__init__(self, 5, vShaderMesh, fShaderMesh, Draw( 0x0004, 0, len(vertices) / 3, None))

        a_position = Attribute(
            struct.pack ('%df' % len(vertices), *vertices)
            , 0x1406
            , 3
            , True
            )

        a_normal = Attribute(
            struct.pack('%df' % len(normals), *normals)
            , 0x1406
            , 3
            , True
            )        

        self.__position = position
        self.__rotation = rotation
        self.__scale = scale
        self.__world = Uniform16f()
        self.__update_world()
        self.setAttribute("a_position", a_position)
        self.setAttribute("a_normal", a_normal)
        self.setUniform("u_world", self.__world)
        self.setUniform("u_view", camera.view)
        self.setUniform("u_proj", camera.projection)
        self.setUniform("u_vpsize", Uniform(struct.pack('2f', screenWidth, screenHeight)))
        self.setUniform("s_lightbuffer", Uniform(0xfffe, 0x2901));
        self.setUniform("u_farplane", camera.far)

    def __update_world(self):
        self.__world.update(
        (m.translate(*self.__position) 
         * m.rotationZ(self.__rotation[0]) * m.rotationY(self.__rotation[1]) * m.rotationX(self.__rotation[2])
         * m.scale(self.__scale)).flatten())

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value
        self.__update_world()

    @position.getter
    def position(self):
        return self.__position

    @property
    def rotation(self):
        return self.__rotation

    @position.setter
    def rotation(self, value):
        self.__rotation = value
        self.__update_world()

    @rotation.getter
    def rotation(self):
        return self.__rotation

    @property
    def scale(self):
        return self.__scale

    @position.setter
    def scale(self, value):
        self.__scale = value
        self.__update_world()

    @scale.getter
    def scale(self):
        return self.__scale
        

def fromObjFile(objPath, camera, position=[0.0, 0.0, 0.0], rotation=[0.0,0.0,0.0], scale=1.0):
    meshObj = Obj(objPath)
    return Mesh(meshObj.vertices, meshObj.normals, camera, position, rotation, scale)
