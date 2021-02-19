from rpi_ws281x import *
import re

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

def commandInterpreter(command : str): #complicated way - easy way would be using an array and to assume it has the correct order...
    semicolons = command.split(";")
    for command in semicolons:
        if re.findall("^([A-Za-z]+)\s", command)[0] == "add": #get string until whitespace comes
            instance = command[3:].strip()
            parameters = re.findall("\((.+)\)$", instance) #get strings inside ( ... ) - don't allowe "( ... ) ..."
            if parameters:
                classname = instance.replace("("+parameters[0]+")","")
                print(classname)
                print(parameters)
            else:
                print("something wrong with the parameters: "+str(parameters))
        else:
            print("beginning of command not known "+str(re.findall("^[A-Za-z]+\s?", command)))
        