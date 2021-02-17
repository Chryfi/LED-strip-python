from threading import Event
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame as pg
from pygame.locals import *
import math

from threads.thread_classes import * #imports all other stuff too.. maybe stupid structure?


	
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
    
    #handler.addAnimation(RainbowCycle(stripe,5))
    
    try:
        while True:
            handler.update()
    except KeyboardInterrupt:
        print("KeyboardInterrupting main Thread\n")




class AnimationHandler(IObserver):
    interrupted = False
    clear = False
    exit = Event()
    _animations = []
    isShutDown = False

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
        elif arg == "shutdown":
            self.shutdown(str(o))
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

    def shutdown(self, arg):
        print("Shutdown by %s" % arg)
        self.isShutDown = True
    
    def update(self, wait_ms=20):
        counter = 0
        while True and self.interrupted == False:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            
            if self.isShutDown == True:
                self.fadeOut(5)
            else:
                for animation in self._animations:
                    animation.update()
                    if animation.isDead() == True:
                        self._animations.remove(animation)
            
            self.stripe.show()
            self.render()
            self.exit.wait(wait_ms/1000.0)
            if counter == 5:
                counter = 0
                rgbCycle = RainbowCycle(None,20)
                self.addAnimation(Pulse(random.randint(0,299),self.stripe, 8, -1, rgbCycle))
            counter = counter + 1

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
        
    def fadeOut(self, speed):
        for pos in range(self.stripe.numPixels()):
            r = self.stripe.getPixelColorRGB(pos).r - speed
                
            if r < 0:
                r = 0
                    
            g = self.stripe.getPixelColorRGB(pos).g - speed
                
            if g < 0:
                g = 0
                    
            b = self.stripe.getPixelColorRGB(pos).b - speed
                
            if b < 0:
                b = 0
                    
            self.stripe.setPixelColor(pos, Color(r,g,b))









if __name__ == '__main__':
    main() 
	
	
