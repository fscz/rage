from pygre import *
from helpers import ScreenQuad
import struct

vPointLight = '''
  attribute vec4 a_position;  
  attribute vec2 a_texcoord;
  uniform vec3 u_frustumrays[4];
  varying vec3 v_viewray;
  varying vec2 v_texcoord;
  void main() {
    gl_Position = a_position;
    v_viewray = u_frustumrays[int(a_position.y + 1.0 + a_position.x * 0.5 + 0.5)];
    v_texcoord = a_texcoord;
  }'''

fPointLight = '''
  uniform sampler2D s_gbuffer;
  uniform mat4 u_view;
  uniform vec2 u_vpsize;
  uniform float u_farplane;
  uniform vec4 u_lightpos;
  uniform vec3 u_lightcolor;
  uniform float u_lightintensity;
  varying vec3 v_viewray;
  varying vec2 v_texcoord;
  const vec4 nothing = vec4(0.0, 0.0, 0.0, 0.0);
  const vec2 unpackMask = vec2(1.0, 1.0 / 256.0);

  vec3 decodeNormal(in vec2 encodedNormal) {
    vec3 dec;
    dec.xy = encodedNormal.xy * 2.0 - 1.0;
    dec.z = sqrt(1.0 - dot(dec.xy, dec.xy));
    return dec;
  }   

  float unpackFloat(in vec2 value) {
    return dot(unpackMask, value);
  }

  void main() {    
    vec4 sample = texture2D(s_gbuffer, v_texcoord);

    if (all(equal(sample,nothing))) discard;

    vec3 normal = decodeNormal(sample.xy);
    normal.z = -normal.z;

    float depth = unpackFloat(sample.zw) * u_farplane;

    vec3 reconstPos = v_viewray * depth;

    vec3 lightDir = (u_view * u_lightpos).xyz - reconstPos;

    float lightDist = sqrt(dot(lightDir, lightDir));
    lightDir = lightDir / lightDist;
    float match = clamp(dot(lightDir, normal), 0.0, 1.0);

    float attenuation = 1.0 / (1.0 + 0.1*lightDist + 0.01*lightDist*lightDist);

    gl_FragColor = vec4(u_lightcolor * u_lightintensity * match * attenuation, 1.0);
  }'''


class PointLight(ScreenQuad):
    def __init__(self, camera, position, color, intensity):
        ScreenQuad.__init__(self, 2, vPointLight, fPointLight)
        self.setUniform("u_frustumrays", Uniform(
                struct.pack('12f', *camera.frustumrays)
        ))
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
        self.__position = position
        self.__positionUniform = Uniform(struct.pack('3f', *position))
        self.__color = color
        self.__colorUniform = Uniform(struct.pack('3f', *color))
        self.__intensity = intensity
        self.__intensityUniform = Uniform(struct.pack('f', intensity))
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("u_view", camera.view)
        self.setUniform("u_lightpos", self.__positionUniform)
        self.setUniform("u_lightcolor", self.__colorUniform)
        self.setUniform("u_lightintensity", self.__intensityUniform)
        self.setUniform("u_farplane", camera.far)
        self.setUniform("u_vpsize", Uniform(struct.pack('2f', Display.width, Display.height)))
        self.setUniform("s_gbuffer", Uniform(0xffff, 0x2901));


    def __update(self):
        self.__positionUniform.update(struct.pack('3f', *self.position))
        self.__colorUniform.update(struct.pack('3f', *self.color))
        self.__intensityUniform.update(struct.pack('f', self.intensity))

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value
        self.__update()

    @position.getter
    def position(self):
        return self.__position

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        self.__color = value
        self.__update()

    @color.getter
    def color(self):
        return self.__color

    @property
    def intentsity(self):
        return self.__intentsity

    @intentsity.setter
    def intentsity(self, value):
        self.__intentsity = value
        self.__update()

    @intentsity.getter
    def intentsity(self):
        return self.__intentsity


vTubeLight = '''
  attribute vec4 a_position;  
  attribute vec2 a_texcoord;
  uniform vec3 u_frustumrays[4];
  varying vec3 v_viewray;
  varying vec2 v_texcoord;
  void main() {
    gl_Position = a_position;
    v_viewray = u_frustumrays[int(a_position.y + 1.0 + a_position.x * 0.5 + 0.5)];
    v_texcoord = a_texcoord;
  }'''

fTubeLight = '''
  uniform sampler2D s_gbuffer;
  uniform mat4 u_view;
  uniform vec2 u_vpsize;
  uniform float u_farplane;
  uniform vec4 u_lightpos;
  uniform vec3 u_lightcolor;
  uniform float u_lightintensity;
  uniform vec3 u_lightdirection;
  uniform float u_lightradius;
  uniform float u_lightlength;
  varying vec3 v_viewray;
  varying vec2 v_texcoord;
  const vec4 nothing = vec4(0.0, 0.0, 0.0, 0.0);
  const vec2 unpackMask = vec2(1.0, 1.0 / 256.0);

  vec3 decodeNormal(in vec2 encodedNormal) {
    vec3 dec;
    dec.xy = encodedNormal.xy * 2.0 - 1.0;
    dec.z = sqrt(1.0 - dot(dec.xy, dec.xy));
    return dec;
  }   

  float unpackFloat(in vec2 value) {
    return dot(unpackMask, value);
  }

  void main() {    
    vec4 sample = texture2D(s_gbuffer, v_texcoord);

    if (all(equal(sample,nothing))) discard;
        
    float depth = unpackFloat(sample.zw) * u_farplane;
    vec3 reconstPos = v_viewray * depth;
    vec3 tubePos = (u_view * u_lightpos).xyz;
    vec3 tubeDirection = normalize((u_view * vec4(u_lightdirection, 0.0)).xyz);

    vec3 lineEnd = tubePos + u_lightlength * tubeDirection;

    vec3 lightDif = reconstPos - tubePos;
    float alpha = dot ( normalize(lightDif), tubeDirection );

    if ( dot ( normalize(reconstPos - lineEnd), tubeDirection ) > 0.0 || alpha < 0.0 ) {
       discard; 
    } // points must be perpendicular to the line that is given by (lightpos, lightlength, lightdirection)

    // find the perpendicular
    vec3 perpPoint = tubePos + cos(alpha) * sqrt(dot(lightDif,lightDif)) * tubeDirection;
    vec3 perpDif = perpPoint - reconstPos;
    float perpDist = sqrt( dot (perpDif, perpDif) );    

    vec3 normal = decodeNormal(sample.xy);
    normal.z = -normal.z;

    float match = clamp(dot(perpDif/perpDist, normal), 0.0, 1.0);

    float atDif = max(perpDist - u_lightradius, 0.0);   

    float attenuation = 1.0 / (1.0 + atDif*atDif*atDif);
    gl_FragColor = vec4(u_lightcolor * u_lightintensity * match * attenuation, 1.0);
  }'''


class TubeLight(ScreenQuad):
    def __init__(self, camera, position, direction, radius, length, color, intensity):
        ScreenQuad.__init__(self, 2, vTubeLight, fTubeLight )
        
        self.setUniform("u_frustumrays", Uniform(
                struct.pack('12f', *camera.frustumrays)
        ))
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
        

        self.__position = position
        self.__positionUniform = Uniform(struct.pack('3f', *position))
        self.__color = color
        self.__colorUniform = Uniform(struct.pack('3f', *color))
        self.__intensity = intensity
        self.__intensityUniform = Uniform(struct.pack('f', intensity))
        self.__direction = direction
        self.__directionUniform = Uniform(struct.pack('3f', *direction))
        self.__radius = radius
        self.__radiusUniform = Uniform(struct.pack('f', radius))
        self.__length = length
        self.__lengthUniform = Uniform(struct.pack('f', length))
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("u_view", camera.view)
        self.setUniform("u_lightpos", self.__positionUniform)
        self.setUniform("u_lightcolor", self.__colorUniform)
        self.setUniform("u_lightintensity", self.__intensityUniform)
        self.setUniform("u_farplane", camera.far)
        self.setUniform("u_vpsize", Uniform(struct.pack('2f', Display.width, Display.height)))
        self.setUniform("s_gbuffer", Uniform(0xffff, 0x2901));        
        self.setUniform("u_lightdirection", self.__directionUniform)
        self.setUniform("u_lightlength", self.__lengthUniform)
        self.setUniform("u_lightradius", self.__radiusUniform)

    def __update(self):
        self.__positionUniform.update(struct.pack('3f', *self.position))
        self.__colorUniform.update(struct.pack('3f', *self.color))
        self.__intensityUniform.update(struct.pack('f', self.intensity))
        self.__directionUniform.update(struct.pack('3f', self.direction))
        self.__lengthUniform.update(struct.pack('3f', self.length))
        self.__radiusUniform.update(struct.pack('f', self.radius))

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value
        self.__update()

    @position.getter
    def position(self):
        return self.__position

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, value):
        self.__direction = value
        self.__update()

    @direction.getter
    def direction(self):
        return self.__direction

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        self.__radius = value
        self.__update()

    @radius.getter
    def radius(self):
        return self.__radius

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        self.__color = value
        self.__update()

    @color.getter
    def color(self):
        return self.__color

    @property
    def intentsity(self):
        return self.__intentsity

    @intentsity.setter
    def intentsity(self, value):
        self.__intentsity = value
        self.__update()

    @intentsity.getter
    def intentsity(self):
        return self.__intentsity
