import numpy.linalg as LA
import numpy

NULLVECTOR = [0.0, 0.0, 0.0]

def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError, "mtl file doesn't start with newmtl stmt"
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            surf = pygame.image.load(mtl['map_Kd'])
            image = pygame.image.tostring(surf, 'RGBA', 1)
            ix, iy = surf.get_rect().size
            texid = mtl['texture_Kd'] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                GL_UNSIGNED_BYTE, image)
        else:
            mtl[values[0]] = map(float, values[1:])
    return contents


class Obj:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.__vertexbuffer__ = []
        self.__normalbuffer__ = []
        self.__texcoordbuffer__ = []
        self.vertices = []
        self.normals = []        
        self.texcoords = []
        self.mtllib = None

        material = None
        self.__process_file__(filename, swapyz)
    
    def __append_buffers__(self, w):
        self.vertices += (self.__vertexbuffer__[int(w[0])-1])

        if len(w) >= 2 and len(w[1]) > 0:
            self.texcoords += (self.__texcoordbuffer__[int(w[1])-1])
        else:
            self.texcoords += (NULLVECTOR)

        if len(w) >= 3 and len(w[2]) > 0:
            self.normals += (self.__normalbuffer__[int(w[2])-1])
        else:
            self.normals += (NULLVECTOR)

    def __process_file__(self, filename, swapyz):
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.__vertexbuffer__.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.__normalbuffer__.append(numpy.ndarray.tolist(numpy.multiply(v, 1 / LA.norm(v))))
            elif values[0] == 'vt':
                self.__texcoordbuffer__.append(map(float, values[1:3]))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                #self.mtllib = MTL(values[1])
                pass
            elif values[0] == 'f':
                face = values[1:]

                if len (face) > 4:
                    raise "error. polygon size > 4 not supported"

                if len(face) == 3:
                    for v in face[0:3]:
                        w = v.split('/')
                        self.__append_buffers__(w)                        

                elif len(face) == 4: 
                    for v in [face[0], face[1], face[3], face[3], face[1], face[2]]:
                        w = v.split('/')
                        self.__append_buffers__(w)

        
