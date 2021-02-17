from __future__ import annotations
from threading import Event
from typing import List
import threading
import time
import logging
import numpy as np
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame as pg
from pygame.locals import *
import math


def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue
	
def main():
    stripe = Adafruit_NeoPixel()
    handler = AnimationHandler(stripe)
    console =  ConsoleThread(1, "console-Thread")

    console.daemon=True

    console.addObserver(handler)
    console.start()

    pulseThread =  PulseThread(1, "pulse-Thread")

    pulseThread.daemon=True

    pulseThread.addObserver(handler)
    pulseThread.start()
    
    pg.init()
    display = (1920,100)

    pg.display.set_mode(display, DOUBLEBUF|OPENGL)
    glMatrixMode(GL_PROJECTION)
    glOrtho(0,pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),0,-1,1) #setup orthographic matrix - (0,0) at top left (1200,800) at bottom right

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    
    #handler.addAnimation(RainbowCycle(stripe,13))
    
    try:
        while True:
            handler.update()
    except KeyboardInterrupt:
        print("KeyboardInterrupting main Thread\n")


class Observerable:
    #classes extending from observable need to declare observers list

    def notify(self, arg):
        for observer in self.observers:
            observer.notify(self, arg)
    
    def addObserver(self, observer : IObserver):
        self.observers.append(observer)
    
    def removeObserver(self, observer : IObserver):
        if len(self.observers) != 0:
            self.observers.remove(observer)

class IObserver:
    
    def update(self, o : Observerable, arg):
        pass


class ConsoleThread(threading.Thread, Observerable):
    observers = []

    def __init__(self, threadID, name, group = None):
        super().__init__(group, threadID, name)

        #setup inherited variables
        self.threadID = threadID
        self.name = name
        self.group = None

    def run(self):
        try:
            while True:
                inputstr = input()
                self.notify(inputstr) #note: self.__class__ needed because python has static like variable inheritance - no real OOP
        except Exception as e:
            print("Exception in Thread "+str(self)+" Exception: "+str(e))
        except KeyboardInterrupt:
            print("KeyboardInterrupting "+str(self)+"\n")
    
    def __str__(self):
        return __class__.__name__+" \"%s\" < ThreadID %s, started %s %s >" % (self.name, self.threadID, "daemon" if self.daemon == True else "", self.ident)

class PulseThread(threading.Thread, Observerable):
    observers = []
    
    def __init__(self, threadID, name, group = None):
        super().__init__(group, threadID, name)

        #setup inherited variables
        self.threadID = threadID
        self.name = name
        self.group = None

    def run(self):
        try:
            while True:
                for o in self.observers:
                    rgbCycle = RainbowCycle(None,5)
                    o.addAnimation(Pulse(random.randint(0,299),o.stripe, 8, -1, rgbCycle))
                time.sleep(0.25)
                
        except Exception as e:
            print("Exception in Thread "+str(self)+" Exception: "+str(e))
        except KeyboardInterrupt:
            print("KeyboardInterrupting "+str(self)+"\n")
    
    def __str__(self):
        return __class__.__name__+" \"%s\" < ThreadID %s, started %s %s >" % (self.name, self.threadID, "daemon" if self.daemon == True else "", self.ident)


class IAnimation:

    def __init__(self, stripe : Adafruit_NeoPixel):
        self.__class__.stripe = stripe
        self.__class__._dead = False

    def update():
        pass

    def reset(self):
        pass

    def clone(self):
        pass

    def isDead(self):
        return self._dead

class AnimationHandler(IObserver):
    interrupted = False
    clear = False
    exit = Event()
    _animations = []

    def __init__(self, stripe : Adafruit_NeoPixel):
        self.stripe = stripe

    def addAnimation(self, animation : IAnimation):
        self._animations.append(animation)

    def notify(self, o : Observerable, arg):
        if arg == "stop":
            self.interrupt(str(o))
        elif arg == "restart":
            if self.interrupted == True:
                self.restart(str(o))
            else:
                print("Already started!")
        elif arg == "clear":
            self.clearStripe()
            self.interrupt(str(o))
            self.clear = True
        else:
            print("StripeAnimation Error: argument '"+arg+"' given by "+str(o)+" not known!")

    def restart(self, arg):
        self.interrupted = False
        print("Restarted by %s" % arg)
        self.exit.clear() #clear so waiting works again

    def interrupt(self, arg):
        self.interrupted = True
        print("Interrupted by %s" % arg)
        self.exit.set() #interrupts waiting
        self.exit.clear() #sets flag of event to false again
    
    def update(self, wait_ms=20):
        while True and self.interrupted == False:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            
            for animation in self._animations:
                animation.update()
                if animation.isDead() == True:
                    self._animations.remove(animation)
            
            self.stripe.show()
            self.render()
            self.exit.wait(wait_ms/1000.0)

        if self.clear == True:
            for animation in self._animations:
                animation.reset()
            self.restart(str(self))
            self.clear = False

    def render(self):
        size = 5
        offset = math.floor((pg.display.get_surface().get_width())/(self.stripe.numPixels()))
        glPointSize(size)
        glBegin(GL_POINTS)
        glColor(255, 10, 130)
        pos = size
        for i in range(self.stripe.numPixels()):
            glColor3f(self.stripe.getPixelColorRGB(i).r/255, self.stripe.getPixelColorRGB(i).g/255, self.stripe.getPixelColorRGB(i).b/255)
            glVertex2i(int(pos), int(pg.display.get_surface().get_height()/2))
            pos = pos+offset
        glEnd()
        pg.display.flip()
        pg.time.wait(10)

    def clearStripe(self):
        for pos in range(self.stripe.numPixels()):
            self.stripe.setPixelColor(pos, Color(0,0,0))
        self.stripe.show()



def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)    


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

    def clone(self) -> Pulse:
        c = Pulse(self.middlePos, self.stripe, self.velocity, self.acceleration, self.rgbCycle, False)
        c.leftPos = self.leftPos
        c.rightPos = self.rightPos
        c.curve = self.curve
        c.velocity = self.velocity
        c.age = self.age
        c.deathAge = self.deathAge
        c._dead = self._dead
        return c











#THAT IS ONLY TEMPORARY BECAUSE I DONT HAVE LED LOL
class Adafruit_NeoPixel:
    _led_data = []
    _num = 300

    def __init__(self):
        for pos in range(self._num):
            self._led_data.append(0)


    def setPixelColor(self, n, color):
        self._led_data[n] = color

    def show(self):
	    pass
	
    def numPixels(self):
        return self._num
		
		
    def getPixelColorRGB(self, n):
        c = lambda: None
        setattr(c, 'r', self._led_data[n] >> 16 & 0xff)
        setattr(c, 'g', self._led_data[n] >> 8  & 0xff)
        setattr(c, 'b', self._led_data[n]    & 0xff)
        return c
    
    def setPixelColorRGB(self, n, red, green, blue, white=0):
        self.setPixelColor(n, Color(red, green, blue, white))
    
    def getPixelColor(self, n):
        return self._led_data[n]


if __name__ == '__main__':
    main() 
	
	
