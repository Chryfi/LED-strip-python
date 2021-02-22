from threading import Event
import sys
if "render" in sys.argv:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GLU import *
    import pygame as pg
    from pygame.locals import *
import math
import importlib.util

ws_spec = importlib.util.find_spec("ws") #for the real led rpi_ws281 library
module_ws_found = ws_spec is not None

from task import *
from animation.animation_classes import *
from threads.thread_classes import *
from command import *

# LED strip configuration:
LED_COUNT      = 300      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
if module_ws_found == True:
    LED_STRIP = ws.WS2812_STRIP
LED_Middle = 136

def main():
    if module_ws_found == True:
        stripe = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    else:
        stripe = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
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

    
    handler.addAnimation(Fade(stripe, 2, True, 0, 255))
    
    colorInterface = ColorInterface(stripe.numPixels())  
    handler.addAnimation(RainbowPulse(stripe, 0.5, colorInterface))
    handler.addAnimation(Nightsky(stripe,6,2, 0, 255, colorInterface))
    #handler.addAnimation(PulseFade(stripe,6, 255, 100))

    #colorInterface2 = ColorInterface(stripe.numPixels())
    #handler.addAnimation(RainbowCycle(stripe, 25, colorInterface2))
    #handler.tasks.addTask(["effect", Pulse(stripe, 149,11, -0.25, 0.0075, colorInterface2)])
    
    try:
        while True:
            handler.update()
    except KeyboardInterrupt:
        #fade_out = Fade(stripe, -2, True,0,stripe.getBrightness())
        #fade_in = Fade(stripe, 10, True,0,120)
        #fade_outend = Fade(stripe, -1, True,130,0)
        #handler.tasks.addTasks([["effect", fade_out], ["effect", fade_in], ["effect", fade_outend], ["stop", None]])
        colorInterface3 = ColorInterface(stripe.numPixels(), Color(0, 255,255))
        #handler.addAnimation(RainbowPulse(stripe, 25, colorInterface3))
        handler.tasks.addTasks([["effect", Pulse(stripe, 149,13.5, -0.5, 0.005, colorInterface3)], ["stop", None]])

        handler.update()

        print("\nKeyboardInterrupting main Thread\nByeBye")




class AnimationHandler(IObserver):

    def __init__(self, stripe : PixelStrip):
        self.interrupted = False
        self.clear = False
        self.isShutDown = False
        self.exit = Event()
        self.stripe = stripe
        self._animations = []
        self.tasks = Tasks()

    def addAnimation(self, animation : IAnimation):
        self._animations.append(animation)

    def notify(self, o : Observerable, arg):
        print("StripeAnimation got notified by "+str(o)+" with the arguments "+str(arg))

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
        colorInterface4 = ColorInterface(self.stripe.numPixels())
        #self.addAnimation(RainbowCycle(self.stripe, 10, colorInterface4))
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
            

            current_task = self.tasks.peek()
            if current_task != None:
                if current_task[0] == "effect":
                    current_task[1].update()
                    if current_task[1].isDead() == True:
                        self.tasks.pop()
                elif current_task[0] == "stop":
                    self.tasks.pop()
                    break
                
            self.stripe.show()
            self.exit.wait(wait_ms/1000.0)

            #if counter%15==0:
                #self.addAnimation(Pulse(self.stripe, random.randint(120,299),4, -0.275, 0.035, colorInterface4))
            counter = counter + 1

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
