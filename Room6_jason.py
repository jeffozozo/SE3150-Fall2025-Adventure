from object import Object
from player import Player
import sys  # For exiting the game
import time


# this is how you create a new object. You inherit from class Object and override the 'use' function. 
class Lamp(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # the lamp toggles when you 'use' it. 
        if self.state == "off":
            self.state = "on"
            print(f"The lamp is now on.")
        else:
            self.state = "off"
            print(f"The lamp is now is now off.")


class Farmer(Object):
    def __init__(self, name, description, can_be_gotten, state, visible, player : "Player", countdown, alarmed = True):
        self.alarmed = alarmed 
        self.countdown = countdown  
        self.current_countdown = countdown 
        self.countdown_has_started = False
        self.player_handle = player
        super().__init__(name, description, can_be_gotten, state, visible)
    def start_countdown(self):
        if self.countdown_has_started:
            return
        self.countdown_has_started = True
        while self.countdown_has_started:
            for i in range(self.current_countdown, 0, -1):
                print(i)
                time.sleep(1)
            
            print("BANG!")
            self.player_handle.health = 0
    def use(self):
        if self.alarmed:
            print("""
                  Now don't come any closer ya hear?
                  I'm gonna give ya to the count of 5 to explain yaself.
                  """)
            self.start_countdown()
        else:
            print("")


class Room:

    objects = []

    def __init__(self):
        self.room_num = 0
        self.has_entered_previously = False
        self.is_in_hole = False
        self.time_to_react = 5
        self.location = "desert"
        self.farmer = None
        self.description = (
            """
            Suddenly, you're in a desert, blinded by the hot afternoon sun
            You come to your senses, and notice there's a man holding a strange contraption right in front of you.
            He speaks, 
            "Where in the hell didja come from!?"
            He seems very alarmed, and jerks the contraption to face you.
            "Nowh don't move a finga, you's gonna explain where ya came from."
            He moves his finger onto a section of the contraption.
            You instinctively flick your arms up.
            "Noh funny tricks from ya, or the vulchahs are gonna have themselfes a snack"

            You need to find a way out of this situation.

            There is a reality-breaking door behind you, which seems to link back to the dungeon you came from.
            
            There also seems to be a loose patch of dirt in front of you, potentially covering a hole beneath.
            """
        )


        # other room setup - add the lamp and set up the exits.

        #this is how you declare your exits. It doesn't matter what room the attach to, I'll worry about that in the global level. 
        self.exits = ["up", "down", "east"]



    def enter(self, player):

        # step 1 - Print the room description
        self.describe_room()
        self.farmer = Farmer("Farmer", "A scared farmer with a very intimidating device", False, "Cautious", True, player, self.time_to_react)
        if self.has_entered_previously:
            self.time_to_react = 3
            self.description = (
                """
                The man snaps back to face you, remembering his previous encounter
                "There you are snake, stand still an' git it between the eyes"
                You have mere moments to react.
                """
            )
            self.farmer.state = "Alarmed"
            self.farmer.start_countdown()
        self.objects.append(self.farmer)

        # step 2 - make your own command loop - watch carefully about how to parse commands:
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            #Do the command - You should make helper functions for each of these in your room as well.
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
            
            if not player.is_alive():
                break #may be a redundant check but idk how the engine interacts with the player dying

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.location == "desert":
            self.description = (
                """
                You're in a desert, with an alarmed farmer in front of you, a dimension door behind you, and loose dirt in front of you
                """
            ) #This may break stuff, but it's supposed to change the description after entering the room
        else:
            self.description = (
                """
                You're in a dark dusty hole, with a portal above you and a deep hole below you
                """
            )
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["down", "d"]: #add any other commands that might go down
            if self.location == "desert":
                print("You break through the dirt, and find yourself in a dark, dusty hole")
                self.location = "hole"
                if self.farmer:
                    self.farmer.countdown_has_started = False
                return None
            print("You go deeper into the hole as it beckons you forward")
            self.has_entered_previously = True
            if self.farmer:
                self.farmer.countdown_has_started = False
            return "down"
        elif direction in ["up", "u"] and self.location == "hole":
            print("you go up into the strange portal and are transported elsewhere")
            self.has_entered_previously = True
            if self.farmer:
                self.farmer.countdown_has_started = False
            return "up"
        elif direction in ["east", "e"]:
            print("you go back to whence you came")
            self.has_entered_previously = True
            if self.farmer:
                self.farmer.countdown_has_started = False
            return "east"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        if target == "farmer" and self.farmer:
            print("The farmer doesn't react very kindly to being inspected")
            self.farmer.start_countdown()
            return
        
        # Check if the object is in the room or in the player's inventory and print it description and status. You can use this code exactly.
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
    
    # you can use this as well. haha get it? use this...
    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)
        
        #this room only allows you to use the objects in the list or inventory. That is not a global constraint however and you can add whatever use functions you like.
        if(item == None):
            print("you can't use that.")
            return
        
        item.use()
        

    # this code could also probably be used verbatim
    def get(self, item_name, player):

        # Check if the player already has the item in their inventory
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

        # Add the object to the player's inventory and remove it from the room
        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")
        return
    
    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            print(f"You don't have the {item_name}.")
            return
        
        # remove the item from the inventory and put it in the object list
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
        print("This is the starting room. You probably ought to get the lamp and go down the well.")

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
    
