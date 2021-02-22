from abc import ABC, abstractmethod
import re

class CommandHandler:
    _commandsmap = ["add","stop"]
    _currentReceiver = None #static variable

    def __init__(self, receivers : list):
        self.receivers = receivers

    def execute(self, arg):
        #check what to execute -> then do something like this
        search = re.search("^([A-Za-z]+)\s", arg)
        if search != None and search.group() == "add": #get string until whitespace comes
            instance = arg[3:].strip()
            parameters = re.findall("\((.+)\)$", instance) #get strings inside ( ... ) - don't allowe "( ... ) ..."
            if parameters:
                classname = instance.replace("("+parameters[0]+")","")
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


