from threading import Event
import sys
if "render" in sys.argv:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GLU import *
    import pygame as pg
    from pygame.locals import *
import math

from animation.animation_classes import *
from threads.thread_classes import *

# LED strip configuration:
LED_COUNT      = 300      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
#LED_STRIP = ws.WS2812_STRIP
LED_Middle = 136
	
def main():
    stripe = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)#, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    stripe.begin()
    handler = AnimationHandler(stripe)
    console =  ConsoleThread(1, "console-Thread")

    console.daemon=True

    console.addObserver(handler)
    console.start()

    #pulseThread =  PulseThread(1, "pulse-Thread")

    #pulseThread.daemon=True

    #pulseThread.addObserver(handler)
    #pulseThread.start()
    if "render" in sys.argv:
        pg.init()
        display = (1920,100)

        pg.display.set_mode(display, DOUBLEBUF|OPENGL)
        glMatrixMode(GL_PROJECTION)
        glOrtho(0,pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),0,-1,1) #setup orthographic matrix - (0,0) at top left (1200,800) at bottom right

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    
    handler.addAnimation(RainbowCycle(stripe,5))
    try:
        while True:
            handler.update()
    except KeyboardInterrupt:
        fade_out = Fade(stripe, -0.7)
        while fade_out.isDead() == False:
            fade_out.update()
            if "render" in sys.argv:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        quit()
            stripe.show()
            
        print("KeyboardInterrupting main Thread\n")




class AnimationHandler(IObserver):
    interrupted = False
    clear = False
    exit = Event()
    _animations = []
    isShutDown = False

    def __init__(self, stripe : PixelStrip):
        self.stripe = stripe

    def addAnimation(self, animation : IAnimation):
        self._animations.append(animation)

    def notify(self, o : Observerable, arg):
        if arg == "stop":
            self.interrupt(str(o))
        elif arg == "restart":
            self.restart(str(o))
        elif arg == "clear":
            self.clearStripe()
            self.interrupt(str(o))
            self.clear = True
        elif arg == "shutdown":
            self.shutdown(str(o))
        elif arg == "start":
            self.start(str(o))
        else:
            print("StripeAnimation Error: argument '"+arg+"' given by "+str(o)+" not known!")

    def restart(self, arg):
        if self.interrupted == True and self.isShutDown == False:
            self.interrupted = False
            print("Restarted by %s" % arg)
            self.exit.clear() #clear so waiting works again
        elif self.interrupted == False:
            print("Already started!")
        elif self.isShutDown == True:
            print("AnimationHandler is shutdown - type start!")

    def interrupt(self, arg):
        if self.isShutDown == False and self.interrupted == False:
            self.interrupted = True
            print("Interrupted by %s" % arg)
            self.exit.set() #interrupts waiting
            self.exit.clear() #sets flag of event to false again
        elif self.isShutDown == True:
            print("AnimationHandler is shutdown!")
        elif self.interrupted == True:
            print("Already interrupted!")

    def shutdown(self, arg):
        print("Shutdown by %s" % arg)
        self.isShutDown = True
        self._animations[:] = [] #clear animations
        self.clearStripe()


    def start(self, arg):
        print("Started by %s" % arg)
        self.isShutDown = False
    
    def update(self, wait_ms=20):
        counter = 0
        while True and self.interrupted == False:
            if "render" in sys.argv:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        quit()
            
            for animation in self._animations:
                animation.update()
                if animation.isDead() == True:
                    self._animations.remove(animation)

            self.stripe.show()
            self.exit.wait(wait_ms/1000.0)

            """if counter == 5:
                counter = 0
                rgbCycle = RainbowCycle(None,0.2)
                self.addAnimation(Pulse(random.randint(0,299),self.stripe, 8, -1, rgbCycle))
            counter = counter + 1"""

        if self.clear == True:
            for animation in self._animations:
                animation.reset()
            self.restart(str(self))
            self.clear = False

    def clearStripe(self):
        for pos in range(self.stripe.numPixels()):
            self.stripe.setPixelColor(pos, Color(0,0,0) & 255)










if __name__ == '__main__':
    main() 
	
	
