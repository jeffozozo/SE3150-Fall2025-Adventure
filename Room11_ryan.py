from object import Object
from player import Player
import sys

class Cat(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)
    
    def use(self):
        print(f"My little baby is missing! Please help me find her!")

class Room:
    objects = []
    def __init__(self):
        self.room_num = 11
        self.description = (
            "You enter the room and find yourself temporarily blinded.\n"
            "It takes a minute to recover, you look up and are surrounded by some tiny cats.\n"
            "The room is bright, you already have a headache from all the bright colors.\n"
            'One of the tiny cats tells you "WE ARE MISSING A BABY".\n'
        )
        self.exits = ["north", "south"]
        cat = Cat("Cat", "A rainbow cat", False, "worried", True)
        self.objects.append(cat)

    def enter(self, player):
        self.describe_room()

        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            if command_base in ["move", "go"]:
                next = self.move(other_part)
                if(next != None):
                    return next
            
            elif command_base == "use":
                self.use(other_part,player)

            elif command_base == "look":
                self.look(other_part, player)

            elif command_base in ["get", "take"]:
                self.get(other_part, player)

            elif command_base in ["drop", "put"]:
                self.drop(other_part, player)

            elif command_base == "inventory":
                self.show_inventory(player)

            elif command_base == "stats":
                self.show_stats(player)

            elif command_base == "quit":
                if(self.quit_game(player) == "quit"):
                    return "quit"
                

            elif command_base in ["help", "?"]:
                self.show_help()
            
            elif command_base == "hint":
                self.show_hint()
            else:
                self.unknown_command()
            
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")
    
    def move(self, direction):
        if direction in ["north", "n"]:
            print("You open the creepy door and walk through.")
            return "north"
        elif direction in ["south", "s"]:
            print("You open the strangely soft door and walk through.")
            return "south"
        else:
            print("You can't go that way.")
            return None
    
    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        if(target == "cat"):
            print("You can barely make out any details, but the cat seems to have the body of a poptart, and looks strangely pixelated.....")
            return
        
        item = self.get_item_from_inventory(target,player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None:
                print("There is nothing like " + target + " to look at.")
                return
            
        if target == item.name.lower().strip():
            print(item.description) 
            if(item.state != None): 
                print(f"The {item.name} is {item.state}")                   
            return
            
        print("looking at", target, "reveals nothing.")
        return
    
    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)
        
        if(item.name == "Baby Cat"):
            player.inventory.remove(item)
            print("You give the baby cat to the worried cat. The crowd cheers and thanks you. They give you a bag full of acorns.")
            acornBag = Object("bag of acorns", "A sack filled with baby acorns", True, "chill", False)
            self.objects.append(acornBag)
            self.get("bag of acorns", player)
        if(item == None):
            print("you can't use that.")
            return
        
        item.use()
    
    def get(self, item_name, player):

        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        
        item = self.get_item_from_object_list(item_name)
        if(item == None):
            print(f"{item_name} is not here.")
            return
        
        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")
        return
    
    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            print(f"You don't have the {item_name}.")
            return
        
        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")
        return 
    
    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()

    def quit_game(self, player):
        if input("Are you sure you want to quit? (yes/no) ").lower().startswith('y'):
            print(f"Final Score: {player.score}")
            return "quit"

    def show_help(self):
        print("Available commands: move, go, look, get, take, drop, inventory, stats, quit, help")

    def show_hint(self):
        print("You should probably talk(use) to a cat.")

    def unknown_command(self):
        print("You can't do that here. Try something else or type 'help' for options or 'hint' for a clue.")

    def get_item_from_inventory(self, item_name, player):
        for item in player.inventory:
            if item.name.lower() == item_name.lower():  
                return item
        return None    
    
    def get_item_from_object_list(self, item_name):
        for item in self.objects:
            if item.name.lower() == item_name.lower():
                return item
        return None