from object import Object
from player import Player
import sys

class Room:
    
    def __init__(self):
        self.room_num = 11
        self.description = (
            "You find yourself in a dark room. "
        )
        self.exits = ["north", "south"]

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
            print("")
            return "north"
        else:
            print("You can't go that way.")
            return None