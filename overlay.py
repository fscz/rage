from pygre import *
import struct
import matrix as m
from helpers import *
import simplejson
from PIL import Image



screenWidth = Display.width
screenHeight = Display.height


#####################################################
########################### Image
#####################################################

vShaderImage = ''' 
    attribute vec4 a_position;
    attribute vec2 a_texcoord;
    varying vec2 v_texcoord;
    void main() {
    gl_Position = a_position;
    v_texcoord = a_texcoord;
    }'''
fShaderImage = '''
    varying vec2 v_texcoord;
    uniform sampler2D s_texture;
    void main() {
    vec4 sample = texture2D(s_texture, v_texcoord);
    gl_FragColor = vec4(sample.xyz, 1);
    }'''


class Image(SceneObject):
    def __init__(self, sourcefile, x, y, width, height):
        SceneObject.__init__(self, 16, vShaderImage, fShaderImage, Draw(0x0004, 0, 6, None))
        raw = open(sourcefile, 'r').read()
        raw_size = len(raw)
        self.sampler = Uniform(
            data = struct.pack("%dc" % raw_size, *raw ),
            width = 512,
            height = 512,
            textureFormat = 0x1907,
            textureType = 0x1401,
            sampleMode = 0x812F)
        sx = 2 * (x / screenWidth) - 1
        sw = 2 * (x + width) / screenWidth - 1
        sy = 2 * (y / screenHeight) -1
        sh = 2 * (y + height) / screenHeight - 1
        self.position = Attribute(
            data = struct.pack('12f',     
                               sx, sy,
                               sw, sy, 
                               sx, sh, 
                               sx, sh, 
                               sw, sy, 
                               sw, sh ),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
            
        self.texcoord = Attribute(
            data = struct.pack('12f',
                               0.0, 1.0,
                               1.0, 1.0, 
                               0.0, 0.0,
                               0.0, 0.0,
                               1.0, 1.0,
                               1.0, 0.0),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
        self.setAttribute("a_position", self.position)
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("s_texture", self.sampler)


#####################################################
########################### Label
#####################################################

vShaderText= '''
  uniform vec4          u_color;
  attribute vec4		a_position;
  attribute vec2		a_texcoord;
  varying vec2		        v_texcoord;
  varying vec4		        v_color;
  void main(void) {
         v_texcoord = a_texcoord;
         gl_Position = a_position;
         v_color = u_color;
  }'''


fShaderText= '''
  precision mediump float;
  uniform sampler2D		s_atlas;
  varying vec2 v_texcoord;
  varying vec4		        v_color;
  void main()
  {
      gl_FragColor = vec4(v_color.rgb, v_color.a * texture2D(s_atlas, v_texcoord).a);
  }'''


fontTex = None
fontInfo = None
with open('res/fonts/Vera_20.data', 'rb') as f:
    fontTex = f.read()
with open('res/fonts/Vera_20.json', 'r') as f:
    fontInfo = simplejson.loads(f.read())

textureAtlas = Uniform(
    data = fontTex,
    width = 512,
    height = 512,
    textureFormat = 0x1906,
    textureType = 0x1401,
    sampleMode = 0x812F
    )

class Label(SceneObject):
    def __init__(self, text, x, y, width, height, color):        

        l = -0.5
        b = 0.0

        #t = (y + height) * 2 - 1
        #r = (x + width) * 2 - 1

        r = 0
        t = 0

        attrib_pos = []
        attrib_st = []

        texture_width = float(fontInfo['width'])
        texture_height = float(fontInfo['height'])

        for c in text:            
            glyph = fontInfo['chars']['%d' % ord(c)]
            r = l + (40 / screenWidth)
            t = 40 / screenHeight
            attrib_pos.extend([
                    l, b,
                    r, b,
                    l, t,
                    l, t,
                    r, b,
                    r, t
            ])
            l = r
            texcoords = glyph['texcoords']
            
            attrib_st.extend([
                    texcoords[0], texcoords[3], 
                    texcoords[2], texcoords[3],
                    texcoords[0], texcoords[1],
                    texcoords[0], texcoords[1],
                    texcoords[2], texcoords[3],
                    texcoords[2], texcoords[1],
                    ])            
        SceneObject.__init__(self, 16, vShaderText, fShaderText, Draw( 0x0004, 0, len(attrib_pos)/2, None))

        a_position = Attribute(
            struct.pack('%df' % len(attrib_pos), *attrib_pos),
            0x1406,
            2,
            True
            )
        a_texcoord = Attribute(
            struct.pack('%df' % len(attrib_st), *attrib_st),
            0x1406,
            2,
            True
            )
            
        self.setAttribute("a_position", a_position)
        self.setAttribute("a_texcoord", a_texcoord)
        self.setUniform("s_atlas", textureAtlas)
        self.setUniform("u_color", Uniform(struct.pack('4f', 1.0, 0.0, 0.0, 1.0)))



#####################################################
########################### NormalBuffer
#####################################################


vShaderGBuffer = ''' 
    attribute vec4 a_position;
    attribute vec2 a_texcoord;
    varying vec2 v_texcoord;
    void main() {
    gl_Position = a_position;
    v_texcoord = a_texcoord;
    }'''

fShaderGBuffer = '''
    varying vec2 v_texcoord;
    uniform sampler2D s_gbuffer;
    const vec4 nothing = vec4(0.0, 0.0, 0.0, 0.0);
    vec3 decodeNormal(in vec2 encodedNormal) {
    vec3 dec;
    dec.xy = encodedNormal.xy * 2.0 - 1.0;
    dec.z = sqrt(1.0 - dot(dec.xy, dec.xy));
    return dec;
    }
    void main() {
    vec4 sample = texture2D(s_gbuffer, v_texcoord);
    if (all(equal(sample, nothing))) discard;
    gl_FragColor = vec4(decodeNormal(sample.xy), 1.0);
    }'''


class NormalBuffer(ScreenQuad):
    def __init__(self, x, y, width, height):
        SceneObject.__init__(self, 16, vShaderGBuffer, fShaderGBuffer, Draw(0x0004, 0, 6, None))
        sx = 2 * (x / Display.width) - 1
        sw = 2 * (x + width) / Display.width - 1
        sy = 2 * (y / Display.height) -1
        sh = 2 * (y + height) / Display.height - 1
        self.position = Attribute(
            data = struct.pack('12f',     
                               sx, sy,
                               sw, sy, 
                               sx, sh, 
                               sx, sh, 
                               sw, sy, 
                               sw, sh ),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
            
        self.texcoord = Attribute(
            data = struct.pack('12f',
                               0.0, 0.0,
                               1.0, 0.0, 
                               0.0, 1.0,
                               0.0, 1.0,
                               1.0, 0.0,
                               1.0, 1.0),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
        self.setAttribute("a_position", self.position)
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("s_gbuffer", Uniform(0xffff, 0x2901));


#####################################################
########################### LightBuffer
#####################################################


vShaderLightBuffer = ''' 
    attribute vec4 a_position;
    attribute vec2 a_texcoord;
    varying vec2 v_texcoord;
    void main() {
    gl_Position = a_position;
    v_texcoord = a_texcoord;
    }'''
fShaderLightBuffer = '''
    varying vec2 v_texcoord;
    uniform sampler2D s_lightbuffer;
    const vec4 nothing = vec4(0.0, 0.0, 0.0, 0.0);
    void main() {
    vec4 sample = texture2D(s_lightbuffer, v_texcoord);
    if (all(equal(nothing, sample))) discard;
    gl_FragColor = vec4(sample.xyz, 1.0);
    }'''

class LightBuffer(SceneObject):    
    def __init__(self, x, y, width, height):
        SceneObject.__init__(self, 16, vShaderLightBuffer, fShaderLightBuffer, Draw(0x0004, 0, 6, None))
        sx = 2 * (x / Display.width) - 1
        sw = 2 * (x + width) / Display.width - 1
        sy = 2 * (y / Display.height) -1
        sh = 2 * (y + height) / Display.height - 1
        self.position = Attribute(
            data = struct.pack('12f',     
                               sx, sy,
                               sw, sy, 
                               sx, sh, 
                               sx, sh, 
                               sw, sy, 
                               sw, sh ),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
            
        self.texcoord = Attribute(
            data = struct.pack('12f',
                               0.0, 0.0,
                               1.0, 0.0, 
                               0.0, 1.0,
                               0.0, 1.0,
                               1.0, 0.0,
                               1.0, 1.0),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
        self.setAttribute("a_position", self.position)
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("s_lightbuffer", Uniform(0xfffe, 0x2901));

        

#####################################################
########################### DepthBuffer
#####################################################


vShaderDepthBuffer = ''' 
    attribute vec4 a_position;
    attribute vec2 a_texcoord;
    varying vec2 v_texcoord;
    void main() {
    gl_Position = a_position;
    v_texcoord = a_texcoord;
    }'''

fShaderDepthBuffer = '''
    varying vec2 v_texcoord;
    uniform sampler2D s_gbuffer;
    const vec4 nothing = vec4(0.0, 0.0, 0.0, 0.0);
    void main() {
    vec4 sample = texture2D(s_gbuffer, v_texcoord);
    if (all(equal(sample, nothing))) discard;
    float depth = sample.z+sample.w/256.0;
    gl_FragColor = vec4(depth, depth, depth, 1.0);
    }'''


class DepthBuffer(SceneObject):
    def __init__(self, x, y, width, height):
        SceneObject.__init__(self, 16, vShaderDepthBuffer, fShaderDepthBuffer, Draw(0x0004, 0, 6, None))
        sx = 2 * (x / Display.width) - 1
        sw = 2 * (x + width) / Display.width - 1
        sy = 2 * (y / Display.height) -1
        sh = 2 * (y + height) / Display.height - 1
        self.position = Attribute(
            data = struct.pack('12f',     
                               sx, sy,
                               sw, sy, 
                               sx, sh, 
                               sx, sh, 
                               sw, sy, 
                               sw, sh ),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
            
        self.texcoord = Attribute(
            data = struct.pack('12f',
                               0.0, 0.0,
                               1.0, 0.0, 
                               0.0, 1.0,
                               0.0, 1.0,
                               1.0, 0.0,
                               1.0, 1.0),
            dataType = 0x1406,
            numComponents = 2,
            useBuffer = True)
        self.setAttribute("a_position", self.position)
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("s_gbuffer", Uniform(0xffff, 0x2901));


#####################################################
########################### ViewRayBuffer
#####################################################

vShaderViewRay = '''
  attribute vec4 a_position;  
  uniform vec3 u_frustumrays[4];
  varying vec3 v_viewray;
  void main() {
    gl_Position = a_position;
    v_viewray = u_frustumrays[int(a_position.y + 1.0 + a_position.x * 0.5 + 0.5)];
  }'''

fShaderViewRay = '''
    varying vec3 v_viewray;
    void main() {
    gl_FragColor = vec4(v_viewray.yyy, 1.0);
    }'''


class ViewRayBuffer(SceneObject):
    def __init__(self):
        SceneObject.__init__(self, 16, vShaderViewRay, fShaderViewRay, Draw(0x0004, 0, 6, None))
        screenQuad = Attribute(
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
        
        self.setAttribute("a_position", screenQuad)
        self.setUniform("u_frustumrays", Uniform(
                struct.pack('12f',
                        -1.0, -1.0, 1.0,
                         1.0, -1.0, 1.0,
                         -1.0, 1.0, 1.0,
                         1.0, 1.0, 1.0,
                        )
        ))
