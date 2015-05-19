from pygre import *
from helpers import ScreenQuad
import struct

vLightShader = '''
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

fLightShader = '''
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
    float specular = pow(match, 2.0);
    gl_FragColor = vec4(u_lightcolor * u_lightintensity * match * attenuation, specular);
  }'''


class PointLight(ScreenQuad):
    def __init__(self, position, camera,  color, intensity):
        ScreenQuad.__init__(self, 2, vLightShader, fLightShader)
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
        self.setAttribute("a_texcoord", self.texcoord)
        self.setUniform("u_view", camera.view)
        self.setUniform("u_lightpos", Uniform(struct.pack('3f', *position)))
        self.setUniform("u_lightcolor", Uniform(struct.pack('3f', *color)))
        self.setUniform("u_lightintensity", Uniform(struct.pack('f', intensity)))
        self.setUniform("u_farplane", camera.far)
        self.setUniform("u_vpsize", Uniform(struct.pack('2f', Display.width, Display.height)))
        self.setUniform("s_gbuffer", Uniform(0xffff, 0x2901));

    
