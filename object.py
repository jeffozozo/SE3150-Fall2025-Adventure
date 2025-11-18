from abc import ABC, abstractmethod

class Object(ABC):
    def __init__(self, name, description, can_be_gotten, state, visible):
        self.name = name
        self.description = description
        self.can_be_gotten = can_be_gotten
        self.state = state
        self.visible = visible

    def print_description(self):
        print(self.description)

    # this is the overloaded object.use command. If you make a new object, you have to implement this. 
    def use(self):
        pass

