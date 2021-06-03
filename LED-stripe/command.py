from abc import ABC, abstractmethod
import re
from animation.animation_classes import *

class CommandHandler:
    _commandsmap = ["add","stop"]
    _currentReceiver = None #static variable

    def __init__(self, receivers : list):
        self.receivers = receivers

    def execute(self, arg):
        #check what to execute -> then do something like this
        search = re.search("^([A-Za-z]+)\s", arg)
        argList = re.findall('(--[A-Zaz]+-)|([A-Za-z0-9-_]+|"[^"]+"|\'[^\']+\')', arg) #find strings seperated by space or strings like "a b" 'a'

        parameters = []
        args = []
        for arg in argList:
            if arg[0] != "":
                parameters.append(arg[0])
            if arg[1] != "":
                args.append(arg[1])
        
        if args:
            if args[0] == "switch":
                if len(args)==2:
                    klass = globals()[args[1]]
                    instance = klass(self.receivers[0].stripe, 150)
                    handler.addAnimation(instance)

        if search != None and search.group() == "add ": #get string until whitespace comes
            instance = arg[3:].strip()
            parameters = re.findall("\((.+)\)$", instance) #get strings inside ( ... ) - don't allowe "( ... ) ..."
            if parameters:
                classname = instance.replace("("+parameters[0]+")","")
                klass = globals()[classname]
                instance = klass(self.receivers[0].stripe, 150)
                self.receivers[0].addAnimation(instance)
                print(classname)
                print(parameters)
            else:
                print("something wrong with the parameters: "+str(parameters))
        elif arg == "pause":
            PauseCommand(self.receivers).execute()
        elif arg == "play":
            PlayCommand(self.receivers).execute()
        elif arg == "ls": #lists receivers that can be commanded
            ListCommand(self.receivers).execute()
        elif arg == "select": #lists receivers that can be commanded
            self._currentReceiver = self.receivers[0] #WIP
        else:
            print("Command not known")

class Command(ABC):

    @abstractmethod
    def execute(self) -> bool:
        pass

class PauseCommand(Command):
    _parametersMap = []

    def __init__(self, receivers : list, args : list = None, parameters : list = None):
        self._receivers = receivers
        self._args = args
        self._parameters = parameters

    def execute(self) -> bool:
        #check if parameters are correct
        #if not throw exception or something
        for receiver in self._receivers:
            if type(receiver).__name__ == 'AnimationHandler':
                receiver.interrupt("message...")
        return True

class PlayCommand(Command):
    _parametersMap = []

    def __init__(self, receivers : list, args : list = None, parameters : list = None):
        self._receivers = receivers
        self._args = args
        self._parameters = parameters

    def execute(self) -> bool:
        #check if parameters are correct
        #if not throw exception or something
        for receiver in self._receivers:
            if type(receiver).__name__ == 'AnimationHandler':
                receiver.restart("message...")
        return True

class ListCommand(Command):
    _parametersMap = []

    def __init__(self, receivers : list, args : list = None, parameters : list = None):
        self._receivers = receivers
        self._args = args
        self._parameters = parameters

    def execute(self) -> bool:
        #check if parameters are correct
        #if not throw exception or something
        for receiver in self._receivers:
            print("Reciever: "+str(receiver))
        return True


