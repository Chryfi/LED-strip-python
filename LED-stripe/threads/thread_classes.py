import threading
from observer_pattern.observer_classes import *
import traceback
from command import CommandHandler

class ConsoleThread(threading.Thread, Observerable):

    def __init__(self, threadID, name, group = None):
        super().__init__(group, threadID, name)
        self.observers = []
        #setup inherited variables
        self.threadID = threadID
        self.name = name
        self.group = None

    def run(self):
        try:
            while True:
                try:
                    inputstr = input()
                    self.notify(inputstr)
                    commander = CommandHandler(self.observers)
                    commander.execute(inputstr)
                except EOFError as e:
                    print(e)
        except KeyboardInterrupt:
            print("KeyboardInterrupting "+str(self)+"\n")
        except Exception as e:
            track = traceback.format_exc()
            print("Exception in Thread "+str(self)+" Exception: "+str(e)+"\n Stack trace:\n"+track)
        
    
    def __str__(self):
        return __class__.__name__+" \"%s\" < ThreadID %s, started %s %s >" % (self.name, self.threadID, "daemon" if self.daemon == True else "", self.ident)

        
        
"""class PulseThread(threading.Thread, Observerable):
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
                    rgbCycle = RainbowCycle(None,20)
                    #o.addAnimation(Pulse(random.randint(0,299),o.stripe, 8, -1, rgbCycle))
                time.sleep(0.25)
                
        except Exception as e:
            print("Exception in Thread "+str(self)+" Exception: "+str(e))
        except KeyboardInterrupt:
            print("KeyboardInterrupting "+str(self)+"\n")
    
    def __str__(self):
        return __class__.__name__+" \"%s\" < ThreadID %s, started %s %s >" % (self.name, self.threadID, "daemon" if self.daemon == True else "", self.ident)"""
