from utility import *
from rpi_ws281x import *
import numpy as np
import time
import random

class IAnimation:

    def __init__(self, stripe : PixelStrip):
        self.stripe = stripe
        self._dead = False

    def update():
        pass

    def reset(self): #probably stupid - may be deprecated soon
        pass

    def clone(self):
        pass

    def isDead(self):
        return self._dead
        
        
class RainbowCycle(IAnimation):
    rate = None
    state = 0
    age = 0
    dt = None

    def __init__(self, stripe : PixelStrip, rate = 1):
        super().__init__(stripe)
        self.rate = rate
        self.dt = 0.5

    def update(self):
        for pos in range(self.stripe.numPixels()):
            self.stripe.setPixelColor(pos, wheel((int(pos * 256 / self.stripe.numPixels()) + self.state) & 255))
        self.updateState()
        self.age = self.age + self.dt

    def updateState(self):
        self.state = round(self.state + self.rate)
        if self.state > 256:
            self.state = 0

class PulseFade(IAnimation):
    velocity = None
    state = 0
    age = 0
    dt = None
    endBrightness = None
    startBrightness = None

    def __init__(self, stripe : PixelStrip, velocity, startBrightness = 255, endBrightness = 0):
        super().__init__(stripe)
        self.velocity = round(velocity)
        self.dt = 0.5
        if velocity<0:
            self.startBrightness = max(startBrightness,endBrightness)
            self.endBrightness = min(startBrightness,endBrightness)
        else: #what about velocity==0 case ?
            self.startBrightness = min(startBrightness,endBrightness)
            self.endBrightness = max(startBrightness,endBrightness)

        self.currentBrightness = self.startBrightness
        self.stripe.setBrightness(clamp(round(self.startBrightness), 0, 255))

    def update(self):
        self.currentBrightness = clamp(round(self.currentBrightness+self.velocity), min(self.endBrightness, self.startBrightness), max(self.endBrightness, self.startBrightness))

        self.stripe.setBrightness(self.currentBrightness)

        if self.velocity<0 and self.currentBrightness <= min(self.endBrightness, self.startBrightness):
            self.velocity = -self.velocity

        if self.velocity>0 and self.currentBrightness >= max(self.endBrightness, self.startBrightness):
            self.velocity = -self.velocity
        self.age = self.age + self.dt

        
class Nightsky(IAnimation):
    _stars = []
    age = 0
    dt = None
    rate = None
    velocity = None
    endBrightness = None
    startBrightness = None

    def __init__(self, stripe : PixelStrip, velocity, rate, startBrightness = 0, endBrightness = 255):
        super().__init__(stripe)
        self.velocity = round(velocity)
        self.rate = round(rate)
        self.dt = 0.5
        self.startBrightness = min(startBrightness,endBrightness)
        self.endBrightness = max(startBrightness,endBrightness)

    def update(self):
        if (self.age/self.dt)%self.rate == 0:
            rand = round(random.randrange(0,self.stripe.numPixels()-1))
            #while any(star.position == rand for star in self._stars): #can turn out performance heavy
            #    rand = round(random.randrange(0,self.stripe.numPixels()-1))
            if not any(star.position == rand for star in self._stars):
                self._stars.append(Star(self.stripe, round(random.randrange(0,self.stripe.numPixels()-1)), self.velocity, self.startBrightness, self.endBrightness))
        for star in self._stars:
            star.update()
            if star.isDead():
                self._stars.remove(star)
        self.age = self.age + self.dt

class Star(IAnimation):
    age = 0
    dt = None
    endBrightness = None
    startBrightness = None
    currentBrightness = None
    velocity = None
    position = None

    def __init__(self, stripe : PixelStrip, position, velocity, startBrightness = 0, endBrightness = 255):
        super().__init__(stripe)
        self.velocity = abs(round(velocity))
        self.dt = 0.5
        self.position = position
        self.startBrightness = min(startBrightness,endBrightness)
        self.endBrightness = max(startBrightness,endBrightness)
        self.currentBrightness = self.startBrightness


    def update(self):
        self.currentBrightness = clamp(round(self.currentBrightness+self.velocity), 0, max(self.endBrightness, self.startBrightness))
        brightFactor = self.currentBrightness/255
        self.stripe.setPixelColorRGB(self.position, round(255*brightFactor), round(255*brightFactor), round(255*brightFactor))

        if self.velocity>0 and self.currentBrightness >= self.endBrightness:
            self.velocity = -self.velocity

        if self.velocity<0 and self.currentBrightness <= self.startBrightness:
            if self.startBrightness != 0 and self.currentBrightness >= 0:
                if round(self.velocity) != 0:
                    self.velocity = self.velocity*0.98
            else:
                self._dead = True
        
        self.age = self.age + self.dt

class Fade(IAnimation):
    velocity = None
    useBrightness = None
    age = 0
    dt = None
    endBrightness = None
    startBrightness = None
    currentBrightness = None

    def __init__(self, stripe : PixelStrip, velocity, useBrightness = False, startBrightness = 255, endBrightness = 0):
        super().__init__(stripe)
        self.velocity = round(velocity)
        self.dt = 0.5
        self.useBrightness = useBrightness

        if velocity<0:
            self.startBrightness = max(startBrightness,endBrightness)
            self.endBrightness = min(startBrightness,endBrightness)
        else: #what about velocity==0 case ?
            self.startBrightness = min(startBrightness,endBrightness)
            self.endBrightness = max(startBrightness,endBrightness)

        self.currentBrightness = self.startBrightness
        self.stripe.setBrightness(clamp(round(self.startBrightness), 0, 255))

    def update(self):
        die = True

        if self.useBrightness == True:
            self.currentBrightness = clamp(round(self.currentBrightness+self.velocity), min(self.endBrightness, self.startBrightness), max(self.endBrightness, self.startBrightness))

            self.stripe.setBrightness(self.currentBrightness)

            if self.velocity<0 and self.currentBrightness > self.endBrightness:
                die = False

            if self.velocity>0 and self.currentBrightness < self.endBrightness:
                die = False
        else:
            for pos in range(self.stripe.numPixels()):

                r = clamp(round(self.stripe.getPixelColorRGB(pos).r + self.velocity), 0, 255)
                g = clamp(round(self.stripe.getPixelColorRGB(pos).g + self.velocity), 0, 255)
                b = clamp(round(self.stripe.getPixelColorRGB(pos).b + self.velocity), 0, 255)

                #r = math.floor(min(255,self.stripe.getPixelColorRGB(pos).r *(1+ self.velocity*self.dt)))
                #g = math.floor(min(255,self.stripe.getPixelColorRGB(pos).g *(1+ self.velocity*self.dt)))
                #b = math.floor(min(255,self.stripe.getPixelColorRGB(pos).b *(1+ self.velocity*self.dt)))

                if ( r != 0 or g != 0 or b != 0 ) and self.velocity<0:
                    die = False
                
                if ( r != 255 or g != 255 or b != 255 ) and self.velocity>0:
                    die = False

                self.stripe.setPixelColorRGB(pos, r, g, b)

        if die == True:
            self._dead = True

        self.age = self.age + self.dt
        

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

    def __init__(self, stripe : PixelStrip, middlePos, velocity = 3, acceleration = -0.5, rgbCycle: RainbowCycle = None, makeCopy = True):
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
        self.leftPos = clamp(round(self.leftPos - self.velocity*self.dt), 0, self.stripe.numPixels()-1)
        self.rightPos = clamp(round(self.rightPos + self.velocity*self.dt), 0, self.stripe.numPixels()-1)

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
        if self.velocity < -self.acceleration*0.5:
            if self.deathAge == -1:
                self.deathAge = self.age

            for pos in range(self.leftPos, self.rightPos+1, 1):
                self.curve = np.exp((self.deathAge-self.age)/2)
                self.stripe.setPixelColorRGB(pos, round(self.stripe.getPixelColorRGB(pos).r*self.curve), round(self.stripe.getPixelColorRGB(pos).g*self.curve), round(self.stripe.getPixelColorRGB(pos).b*self.curve))
            
        if self.stripe.getPixelColorRGB(self.leftPos).r == 0 and self.stripe.getPixelColorRGB(self.leftPos).g == 0 and self.stripe.getPixelColorRGB(self.leftPos).b == 0:
            self._dead = True
            
        if self.rgbCycle != None:
            self.rgbCycle.updateState()
            
        self.age = self.age + self.dt

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