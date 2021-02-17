from typing import List

class IObserver:
    pass

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