from object import Object
from player import Player
import sys  # For exiting the game



class Room:

    objects = []

    def __init__(self):
        self.room_num = 0
        self.description = ("The room is pitch dark.\n")
                
        #this is how you declare your exits. It doesn't matter what room they attach to, I'll worry about that in the global level. 
        self.exits = ["west","north"]


    # this gets called when the player enters the room.
    def enter(self, player):

        # step 0 - any fancy setup - this room is dark unless you have a lamp and it is on.

        if player.has_item("lamp"):
            lamp = player.get_item("lamp")
            if lamp.state == "on":
                self.description = ("The room is square with a small table in the corner. There is a door to the west and narrow passage to the north.")


        # step 1 - Print the room description
        self.describe_room()

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

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["west", "w"]:
            print("You head through the door to the west.")
            return "west"
        elif direction in ["north", "n","passage"]:
            print("You head through the door to the north.")
            return "north"
        else:

            print("You can't go that way.")
            return None


    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return


        # special handling for this room, if the player has the lamp and it is off...
        if player.has_item("lamp"):
            if player.get_item("lamp").state == "off":
                print("The room is pitch dark - you can't see anything.")
                return
        else:
            print("You don't have a lamp and the room is pitch dark.")
            return


        #special case the table
        if target == "table":
            print("There is a word scratched into the surface of the table. It says: 'excelcior' ")
            return
    
        # Check if the object is in the room object list or in the player's inventory and print its description and status.
        # the table could have been an object if we wanted it to be - then it would be like the lamp. In this case we chose
        # not to make the table an object and it was handled special case above. 
        # this code is pretty generic can could probably be used without much modification in your room.
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

        # custom lamp handling for the room.
        if item.name.lower() == "lamp" :
            if item.state == "off":
                self.description = "The room is pitch dark.\n"
            else:
                self.description = "The room is square with a small table in the corner. There is a door to the west and narrow passage to the north."

    

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
        print("The desk looks interesting.")

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
    
