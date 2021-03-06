from rpi_ws281x import *

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

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def toRGB(color):
    c = lambda: None
    setattr(c, 'r', color >> 16 & 0xff)
    setattr(c, 'g', color >> 8  & 0xff)
    setattr(c, 'b', color    & 0xff)
    return c
        