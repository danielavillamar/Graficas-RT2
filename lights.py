import math_lib as ml 

DIR_LIGHT = 0
POINT_LIGHT = 1
AMBIENT_LIGHT = 2


def reflectVector(normal, direction):
### Calcula el vector reflejado.

  #Args:
    #normal: El vector normal a la superficie.
    #direction: El vector incidente.

  #Returns:
    #El vector reflejado.
###
    temp = []
    reflect = 2 * ml.dot(normal, direction)
    for i in range(len(normal)):
        mul = normal[i] * reflect
        temp.append(mul)
    reflect = temp
    reflect = ml.subtract(reflect, direction)
    reflect = ml.normalized(reflect)
    return reflect
    
def refractVector(normal, direction, ior):
### Calcula el vector refractado.

  #Args:
    #normal: El vector normal a la superficie.
    #direction: El vector incidente.
    #ior: El índice de refracción.

  #Returns:
    #El vector refractado, o None si no hay refracción.
###
    cosi = max(-1, min(1, ml.dot(direction, normal)))
    etai = 1
    etat = ior

    if cosi < 0:
        cosi = -cosi
    else:
        etai, etat = etat, etai
        normal = normal * -1

    eta = etai / etat
    k = 1 - (eta**2) * (1 - (cosi**2) )

    if k < 0: # Refracción total interna
        return None

    middle = (eta * cosi - k**0.5)
    mul1 = []
    mul2 = []
    for i in range(len(direction)):
        val = direction[i] * eta
        mul1.append(val)
   
    for j in range(len(normal)):
       val = normal[j] * middle
       mul2.append(val)

    R = mul1 + mul2
    return R


def fresnel(normal, direction, ior):
### Calcula el coeficiente de Fresnel.

  #Args:
    #normal: El vector normal a la superficie.
    #direction: El vector incidente.
    #ior: El índice de refracción.

  #Returns:
    #El coeficiente de Fresnel.
###
    cosi = max(-1, min(1, ml.dot(direction, normal)))
    etai = 1
    etat = ior

    if cosi > 0:
        etai, etat = etat, etai

    sint = etai / etat * (max(0, 1 - cosi**2) ** 0.5)


    if sint >= 1: # Refracción total interna
        return 1

    cost = max(0, 1 - sint**2) ** 0.5
    cosi = abs(cosi)

    Rs = ((etat * cosi) - (etai * cost)) / ((etat * cosi) + (etai * cost))
    Rp = ((etai * cosi) - (etat * cost)) / ((etai * cosi) + (etat * cost))

    return (Rs**2 + Rp**2) / 2

# Clases de luces / Uso labs pasados

class DirectionalLight(object):
    def __init__(self, direction = (0,-1,0), intensity = 1, color = (1,1,1)):
        self.direction = ml.normalized(direction)
        self.intensity = intensity
        self.color = color
        self.lightType = DIR_LIGHT

    def getDiffuseColor(self, intersect, raytracer):
        tempLight = []
        for i in range(len(self.direction)):
            values = self.direction[i] * -1
            tempLight.append(values)
        
        light_dir = tempLight
        intensity = ml.dot(intersect.normal, light_dir) * self.intensity
        intensity = float(max(0, intensity))            
     
        diffuseColor = [intensity * self.color[0],
                        intensity * self.color[1],
                        intensity * self.color[2]]

        return diffuseColor

    def getSpecColor(self, intersect, raytracer):
        tempLight = []
        for i in range(len(self.direction)):
            values = self.direction[i] * -1
            tempLight.append(values)
        
        light_dir = tempLight
        reflect = reflectVector(intersect.normal, light_dir)

        view_dir = ml.subtract( raytracer.camPosition, intersect.point)
        view_dir = ml.normalized(view_dir)

        spec_intensity = self.intensity * max(0,ml.dot(view_dir, reflect)) ** intersect.sceneObj.material.spec
        specColor = [spec_intensity * self.color[0],
                     spec_intensity * self.color[1],
                     spec_intensity * self.color[2]]

        return specColor

    def getShadowIntensity(self, intersect, raytracer):
        tempLight = []
        for i in range(len(self.direction)):
            values = self.direction[i] * -1
            tempLight.append(values)
        
        light_dir = tempLight

        shadow_intensity = 0
        shadow_intersect = raytracer.scene_intersect(intersect.point, light_dir, intersect.sceneObj)
        if shadow_intersect:
            shadow_intensity = 1

        return shadow_intensity


class PointLight(object):
    def __init__(self, point, constant = 1.0, linear = 0.1, quad = 0.05, color = (1,1,1)):
        self.point = point
        self.constant = constant
        self.linear = linear
        self.quad = quad
        self.color = color
        self.lightType = POINT_LIGHT

    def getDiffuseColor(self, intersect, raytracer):
        light_dir = ml.subtract(self.point, intersect.point)
        light_dir = ml.normalized(light_dir)

        attenuation = 1.0
        intensity = ml.dot(intersect.normal, light_dir) * attenuation
        intensity = float(max(0, intensity))            
                                                        
        diffuseColor = [intensity * self.color[0],
                        intensity * self.color[1],
                        intensity * self.color[2]]

        return diffuseColor

    def getSpecColor(self, intersect, raytracer):
        light_dir = ml.subtract(self.point, intersect.point)
        light_dir = ml.normalized(light_dir)

        reflect = reflectVector(intersect.normal, light_dir)

        view_dir = ml.subtract( raytracer.camPosition, intersect.point)
        view_dir = ml.normalized(view_dir)

        attenuation = 1.0

        spec_intensity = attenuation * max(0,ml.dot(view_dir, reflect)) ** intersect.sceneObj.material.spec
        specColor = [spec_intensity * self.color[0],
                     spec_intensity * self.color[1],
                     spec_intensity * self.color[2]]

        return specColor

    def getShadowIntensity(self, intersect, raytracer):
        light_dir = ml.subtract(self.point, intersect.point)
        light_dir = ml.normalized(light_dir)

        shadow_intensity = 0
        shadow_intersect = raytracer.scene_intersect(intersect.point, light_dir, intersect.sceneObj)
        if shadow_intersect:
            shadow_intensity = 1

        return shadow_intensity


class AmbientLight(object):
    def __init__(self, intensity = 0.1, color = (1,1,1)):
        self.intensity = intensity
        self.color = color
        self.lightType = AMBIENT_LIGHT

    def getDiffuseColor(self, intersect, raytracer):
        temp =[]
        for i in range(len(self.color)):
            value = self.color[i] * self.intensity
            temp.append(value)
        return temp

    def getSpecColor(self, intersect, raytracer):
        return [0,0,0]

    def getShadowIntensity(self, intersect, raytracer):
        return 0
