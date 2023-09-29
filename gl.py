import struct
from collections import namedtuple
import numpy as np
from figures import *
from lights import *
from math import cos, sin, tan, pi
from obj import Obj
import math_lib as ml 


STEPS = 1
MAX_RECURSION_DEPTH = 3

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point4', ['x', 'y', 'z', 'w'])

def char(c):
    #1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes
    return struct.pack('=h', w)

def dword(d):
    #4 bytes
    return struct.pack('=l', d)

def color(r, g, b):
    return bytes([int(b * 255),
                  int(g * 255),
                  int(r * 255)] )

def baryCoords(A, B, C, P):

    areaPBC = (B.y - C.y) * (P.x - C.x) + (C.x - B.x) * (P.y - C.y)
    areaPAC = (C.y - A.y) * (P.x - C.x) + (A.x - C.x) * (P.y - C.y)
    areaABC = (B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)

    try:
        # PBC / ABC
        u = areaPBC / areaABC
        # PAC / ABC
        v = areaPAC / areaABC
        # 1 - u - v
        w = 1 - u - v
    except:
        return -1, -1, -1
    else:
        return u, v, w

class Raytracer(object):
    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.fov = 60
        self.nearPlane = 0.1
        self.camPosition = V3(0,0,0)

        self.scene = [ ]
        self.lights = [ ]

        self.envMap = None


        self.clearColor = color(0,0,0)
        self.currColor = color(1,1,1)

        self.glViewport(0,0,self.width, self.height)
        
        self.glClear()

    def glViewport(self, posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height

    def glClearColor(self, r, g, b):
        self.clearColor = color(r,g,b)

    def glColor(self, r, g, b):
        self.currColor = color(r,g,b)

    def glClear(self):
        self.pixels = [[ self.clearColor for y in range(self.height)]
                         for x in range(self.width)]

    def glClearViewport(self, clr = None):
        for x in range(self.vpX, self.vpX + self.vpWidth):
            for y in range(self.vpY, self.vpY + self.vpHeight):
                self.glPoint(x,y,clr)


    def glPoint(self, x, y, clr = None): 
        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[x][y] = clr or self.currColor

    def scene_intersect(self, orig, dir, sceneObj):
        depth = float('inf')
        intersect = None

        for obj in self.scene:
            hit = obj.ray_intersect(orig, dir)
            if hit != None:
                if sceneObj != hit.sceneObj:
                    if hit.distance < depth:
                        intersect = hit
                        depth = hit.distance

        return intersect

    def cast_ray(self, orig, dir, sceneObj = None, recursion = 0):
        intersect = self.scene_intersect(orig, dir, sceneObj)

        if intersect == None or recursion >= MAX_RECURSION_DEPTH:
            if self.envMap:
                return self.envMap.getEnvColor(dir)
            else:
                return (self.clearColor[0] / 255,
                        self.clearColor[1] / 255,
                        self.clearColor[2] / 255)

        material = intersect.sceneObj.material

        finalColor = [0,0,0]
        objectColor = [material.diffuse[0],
                                material.diffuse[1],
                                material.diffuse[2]]

        if material.matType == OPAQUE:
            for light in self.lights:
                diffuseColor = light.getDiffuseColor(intersect, self)
                specColor = light.getSpecColor(intersect, self)
                shadowIntensity = light.getShadowIntensity(intersect, self)

                lightColor = (diffuseColor + specColor) * (1 - shadowIntensity)

                finalColor = ml.add(finalColor, lightColor)

        elif material.matType == REFLECTIVE:
            
            tempdir =[]
            for i in range(len(dir)):
                val2 = dir[i] * -1
                tempdir.append(val2)
                
            reflect = reflectVector(intersect.normal,tempdir)
            reflectColor = self.cast_ray(intersect.point, reflect, intersect.sceneObj, recursion + 1)
            reflectColor = reflectColor

            specColor = [0,0,0]
            for light in self.lights:
                specColor = ml.add(specColor, light.getSpecColor(intersect, self))
            finalColor = ml.add(reflectColor,specColor)
        elif material.matType == TRANSPARENT:
            outside = ml.dot(dir, intersect.normal) < 0

            bias = []
            for i in range(len(intersect.normal)):
                val = intersect.normal[i] * 0.001
                bias.append(val)
            
            tempdir2 =[]
            for i in range(len(dir)):
                val3 = dir[i] * -1
                vv = round(val3,8)
                tempdir2.append(vv)
            
            specColor = [0,0,0]
            for light in self.lights:
                specColor = ml.add(specColor, light.getSpecColor(intersect, self))

            reflect = reflectVector(intersect.normal, np.array(dir) * -1)
            reflectOrig = ml.add(intersect.point, bias) if outside else ml.subtract(intersect.point, bias)
            reflectColor = self.cast_ray(reflectOrig, reflect, None, recursion + 1)

            kr = fresnel(intersect.normal, dir, material.ior)

            refractColor = [0,0,0]
            if kr < 1:
                refract = refractVector(intersect.normal, dir, material.ior)
                refractOrig = ml.subtract(intersect.point, bias) if outside else ml.add(intersect.point, bias)
                refractColor = self.cast_ray(refractOrig, refract, None, recursion + 1)


            tempRC = []
            for i in range(len(reflectColor)):
                valor = reflectColor[i] * kr 
                tempRC.append(valor)

            tempRC2 = []
            for i in range(len(refractColor)):
                valor = refractColor[i] * (1 - kr)
                tempRC2.append(valor)

            finalColor = ml.addx3(tempRC,tempRC2,specColor)
        
        FCOC =[]
        for j in range(len(finalColor)):
            tam =  objectColor[j] * finalColor[j] 
            FCOC.append(tam)
        finalColor = FCOC
        

        if material.texture and intersect.texcoords:
            texColor = material.texture.getColor(intersect.texcoords[0], intersect.texcoords[1])
            finalColor *= texColor
      
        
        if len(finalColor) == 0:
            return (finalColor)

        r = min(1, finalColor[0])
        g = min(1, finalColor[1])
        b = min(1, finalColor[2])

        return (r,g,b)


    def glRender(self):

        t = tan((self.fov * pi / 180) / 2) * self.nearPlane
        r = t * self.vpWidth / self.vpHeight

        for y in range(self.vpY, self.vpY + self.vpHeight + 1, STEPS):
            for x in range(self.vpX, self.vpX + self.vpWidth + 1, STEPS):

                Px = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
                Py = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1

                Px *= r
                Py *= t

                direction = V3(Px, Py, -self.nearPlane)
                direction = ml.normalized(direction)

                rayColor = self.cast_ray(self.camPosition, direction)

                if rayColor is not None and len(rayColor) != 0:
                    rayColor = color(rayColor[0],rayColor[1],rayColor[2])
                    self.glPoint(x, y, rayColor)

    def glFinish(self, filename):
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            #InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            #Color table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])









