from utility import *
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