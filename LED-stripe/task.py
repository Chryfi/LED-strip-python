from animation.animation_classes import *

class Tasks:

    def __init__(self):
        self._tasks = []

    def addTask(self, task : list):
        if len(task)==2:
            if task[0] == "effect":
                if isinstance(task[1], IAnimation):
                    self._tasks.append(task)
                else:
                    print("wrong object given")
            elif task[0] == "stop":
                self._tasks.append(task)
            else:
                print("task key "+task[0]+" not known")
        else:
            print("task length makes no sense")

    def addTasks(self, tasks : list): #mh?
        for task in tasks:
            self.addTask(task)
    
    #return first task
    def peek(self):
        return self._tasks[0] if self._tasks else None

    #pull first element out of list
    def pop(self):
        return self._tasks.pop(0)
