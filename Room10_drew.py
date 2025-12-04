from object import Object
from player import Player
import sys


class Room:
    objects = []
    in_box = False

    def __init__(self):
        self.room_num = 10
        self.description = (
            "In the center of the room is a large treasure chest with an unusual keyhole.\n"
            "At the base of the south door there is a poor baby nyan cat trying to get through.\n"
            "In the corner of the room, you see a mass of darkness rumbling softly.\n"
            "From the darkness, a pair of glowing red eyes stare at you.\n"
        )

        self.exits = ["west", "south"]

        self.darkness = Object(
            "mass of darkness", "A mass of pure darkness", False, True, True)
        self.objects.append(self.darkness)

        self.baby_cat = Object(
            "Baby Cat", "a baby nyan cat", True, True, True)
        self.objects.append(self.baby_cat)

        self.quest_accepted = False
        self.chest_opened = False

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
                if (next != None):
                    return next

            elif command_base == "use":
                self.use(other_part, player)

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
                if (self.quit_game(player) == "quit"):
                    return "quit"

            else:
                print("unknown command.")

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

        if "darkness" in target and self.darkness in self.objects:
            print("\033[31m")
            if not self.quest_accepted:
                print(
                    "You there.\n"
                    "You want to the endless treasures inside of that chest?\n"
                    "I require acorns.\n"
                    "Bring me a bag of them and I just might give you the key."
                )
                self.quest_accepted = True
            else:
                print(
                    "What are you waiting for?\n"
                    "Bring me a bag of acorns.\n"
                    "Its best if you hurry, you are starting to look pretty tasty..."
                )
            print("\033[0m")
            return

        if "cat" in target and self.baby_cat in self.objects:
            print("\033[35m")
            print("Pwease hewp me! I needs to go home, home, home!!!")
            print("\033[0m")
            return

        print(target + " is not here or there is nothing interesting about it.")

    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if (item == None):
            item = self.get_item_from_object_list(item_name)

        if (item and "bag of acorns" in item.name.lower()):
            print(
                "You give the bag of acorns to the mysterious creature.\n"
                "The darkness fades away to reveal a lone squirrel sitting on a stool.\n\n"
                "\033[31mThank you! I really needed this. Here is your reward!\n\n\033[0m"
                "He hands you a small key made of sticks before running off with his acorns.\n"
                "It looks like he was just hungry!"
            )
            player.inventory.append(
                Object("stick key", "a small key made of sticks", True, True, True))
            player.inventory.remove(item)
            self.objects.remove(self.darkness)
            return

        if (item and "stick key" in item.name.lower()):
            if (not self.chest_opened):
                print(
                    "You insert the key into the chest, and it fits perfectly.  The chest opens to reveal 100 points!")
                player.score += 100
                pass

        if (item and "baby cat" in item.name.lower()):
            print("nya!")
            return

        if (item == None):
            print("you can't use that.")
            return

        item.use()

    def get(self, item_name, player):
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

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")
        return

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if (item == None):
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
