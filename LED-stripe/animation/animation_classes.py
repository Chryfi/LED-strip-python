from utility import *
from led_class_template import *
import numpy as np
import time

class IAnimation:

    def __init__(self, stripe : Adafruit_NeoPixel):
        self.stripe = stripe
        self._dead = False

    def update():
        pass

    def reset(self):
        pass

    def clone(self):
        pass

    def isDead(self):
        return self._dead
        
        
class RainbowCycle(IAnimation):
    rate = None
    state = 0
    age = 0
    dt = 0.5

    def __init__(self, stripe : Adafruit_NeoPixel, rate = 1):
        super().__init__(stripe)
        self.rate = rate

    def update(self):
        for pos in range(self.stripe.numPixels()):
            self.stripe.setPixelColor(pos, wheel((int(pos * 256 / self.stripe.numPixels()) + self.state) & 255))
        self.updateState()
        self.age = self.age + 1*self.dt

    def updateState(self):
        self.state = self.state + self.rate
        if self.state > 256:
            self.state = 0

class Pulse(IAnimation):
    middlePos = None
    leftPos = None
    rightPos = None
    curve = 1
    velocity = None # 1 pixel/ 1 sec
    acceleration = None
    age = 0
    dt = None
    deathAge = -1
    copy = None
    rgbCycle = None

    def __init__(self, middlePos, stripe : Adafruit_NeoPixel, velocity = 3, acceleration = -0.5, rgbCycle:RainbowCycle = None, makeCopy = True):
        super().__init__(stripe)
        self.middlePos = middlePos
        self.leftPos = middlePos
        self.rightPos = middlePos
        self.velocity = velocity
        self.acceleration = acceleration
        self.dt = 0.5 #timestep
        self.rgbCycle = rgbCycle
        if makeCopy == True:
            self.copy = self.clone()
    
    def update(self):
        self.leftPos = round(self.leftPos - self.velocity*self.dt)
        self.rightPos = round(self.rightPos + self.velocity*self.dt)

        if(self.leftPos<0):
            self.leftPos = 0

        if(self.rightPos>299):
            self.rightPos = 299

        self.velocity = self.velocity + self.acceleration*self.dt

        if self.velocity < 0:
            self.velocity = 0

        #apply curve - fade from middle to edge
        for pos in range(self.middlePos, self.leftPos-1, -1):
            self.curve = np.exp(-self.age*(pos-self.leftPos)/35)

            if self.rgbCycle == None:
                self.stripe.setPixelColor(pos, wheel((int((pos) * 256 / self.stripe.numPixels())) & 255))
            else:
                self.stripe.setPixelColor(pos, wheel((int((pos) * 256 / self.stripe.numPixels())+self.rgbCycle.state) & 255))

            self.stripe.setPixelColorRGB(pos, round(self.stripe.getPixelColorRGB(pos).r*self.curve), round(self.stripe.getPixelColorRGB(pos).g*self.curve), round(self.stripe.getPixelColorRGB(pos).b*self.curve))

        #apply curve - fade from middle to edge
        for pos in range(self.middlePos, self.rightPos+1, 1):
            self.curve = np.exp(-self.age*(self.rightPos-pos)/35)
            
            if self.rgbCycle == None:
                self.stripe.setPixelColor(pos, wheel((int((pos) * 256 / self.stripe.numPixels())) & 255))
            else:
                self.stripe.setPixelColor(pos, wheel((int((pos) * 256 / self.stripe.numPixels())+self.rgbCycle.state) & 255))

            self.stripe.setPixelColorRGB(pos, round(self.stripe.getPixelColorRGB(pos).r*self.curve), round(self.stripe.getPixelColorRGB(pos).g*self.curve), round(self.stripe.getPixelColorRGB(pos).b*self.curve))
        
        self.curve = np.exp(-self.age/30)
        self.stripe.setPixelColorRGB(self.leftPos, round(self.stripe.getPixelColorRGB(self.leftPos).r*self.curve), round(self.stripe.getPixelColorRGB(self.leftPos).g*self.curve), round(self.stripe.getPixelColorRGB(self.leftPos).b*self.curve))

        self.stripe.setPixelColorRGB(self.rightPos, round(self.stripe.getPixelColorRGB(self.rightPos).r*self.curve), round(self.stripe.getPixelColorRGB(self.rightPos).g*self.curve), round(self.stripe.getPixelColorRGB(self.rightPos).b*self.curve))
            

        #fade pulse out
        if self.velocity < -self.acceleration*5:
            if self.deathAge == -1:
                self.deathAge = self.age

            for pos in range(self.leftPos, self.rightPos+1, 1):
                self.curve = np.exp((self.deathAge-self.age)/2)
                self.stripe.setPixelColorRGB(pos, round(self.stripe.getPixelColorRGB(pos).r*self.curve), round(self.stripe.getPixelColorRGB(pos).g*self.curve), round(self.stripe.getPixelColorRGB(pos).b*self.curve))
            
        if self.stripe.getPixelColorRGB(self.leftPos).r == 0 and self.stripe.getPixelColorRGB(self.leftPos).g == 0 and self.stripe.getPixelColorRGB(self.leftPos).b == 0:
            self._dead = True
            
        if self.rgbCycle != None:
            self.rgbCycle.updateState()
            
        self.age = self.age + 1*self.dt

    def reset(self):
        self.leftPos = self.copy.leftPos
        self.rightPos = self.copy.rightPos
        self.curve = self.copy.curve
        self.velocity = self.copy.velocity
        self.age = self.copy.age
        self.deathAge = self.copy.deathAge
        self._dead = self.copy._dead
        self.rgbCycle = self.copy.rgbCycle

    def clone(self):
        c = Pulse(self.middlePos, self.stripe, self.velocity, self.acceleration, self.rgbCycle, False)
        c.leftPos = self.leftPos
        c.rightPos = self.rightPos
        c.curve = self.curve
        c.velocity = self.velocity
        c.age = self.age
        c.deathAge = self.deathAge
        c._dead = self._dead
        return c