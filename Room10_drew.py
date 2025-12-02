from object import Object
from player import Player
import sys  # For exiting the game
import pygame


class Room:

    objects = []

    in_box = False

    def __init__(self):
        self.room_num = 10
        self.description = "as you enter the room you see ......."

        self.exits = ["west", "south"]

    def enter(self, player):
        # step 0 - special setup

        # step 1 - Print the room description
        self.describe_room()

        # step 2 - make your own command loop
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            # Do the command - You should make helper functions for each of these in your room as well.
            if command_base in ["move", "go"]:
                next = self.move(other_part)
                if (next != None):
                    return next

            else:
                print("unknown command.")

    # Helper functions

    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["west"]:
            return "west"
        if direction in ["south"]:
            return "south"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if (target == None or target == ""):
            self.describe_room()
            return

        print(target + " is not here or there is nothing interesting about it.")

    # you can use this as well. haha get it? use this...

    def use(self, item_name, player):

        # find where the item is it could be in the inventory or object list of the room.
        item = self.get_item_from_inventory(item_name, player)
        if (item == None):
            item = self.get_item_from_object_list(item_name)

        if (item == None):
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
        if (item == None):
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
        item = self.get_item_from_inventory(item_name, player)
        if (item == None):
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
        if self.in_box:
            print(
                "you have no idea what pushing that button might do. But? won't it be fun to find out?")
        else:
            print("It looks like you could get into that machine. A transport of sorts?")

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
