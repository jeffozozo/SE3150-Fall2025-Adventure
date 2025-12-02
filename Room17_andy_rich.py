from object import Object
from player import Player
import sys 

# Simple base class for people
class Person:
    def __init__(self, name, description):
        self.name = name.lower()
        self.description = description

    def interact(self):
        print(f"{self.name.title()} doesn't have anything to say right now.")

class Wizard(Person):
    def __init__(self):
        super().__init__(
            name="wizard",
            description="An old wizard sitting on a pile of newspapers, watching you carefully.",
        )

        # Wizard questions
        self.questions = [
            ("Who are you?", "I am the last wizard foolish enough to live in this junk pile."),
            ("Why is this room so messy?", "I don't know, why don't you clean it up?"),
            ("What is the WIFI password?", "WizardzRuleWarlocksDrool"),
        ]
        self.asked_count = 0

    def interact(self):
        """Let the player choose up to 3 questions to ask the wizard."""
        if self.asked_count >= 3:
            print("The wizard sighs. 'I've told you all I can for now.'")
            return

        print("\nThe wizard adjusts his glasses and peers at you.")
        print("‘You may ask me up to three questions,’ he says.\n")

        while True:
            if self.asked_count >= 3:
                print("The wizard waves you away gently. 'Enough questions for now.'")
                return

            print("What would you like to ask?")
            for i, (q, _) in enumerate(self.questions, start=1):
                print(f"{i}. {q}")
            print("0. Nevermind")

            choice = input("Choose a question (0-3): ").strip()

            if choice == "0":
                print("The wizard nods and returns to rummaging through the junk.")
                return

            if choice in ["1", "2", "3"]:
                idx = int(choice) - 1
                question_text, answer_text = self.questions[idx]
                print(f"\nYou ask: {question_text}")
                print(f"Wizard: {answer_text}\n")
                self.asked_count += 1
            else:
                print("The wizard squints. 'Try a number between 0 and 3.'")

class Bed(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("The bed looks surprisingly comfy! Take a nap?")


class Weight(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("You lift the weight and flex in the mirror! WOWWWWWW!!!")


class HealthPotion(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("You drink the potion. You feel a sudden surge of strength, except it is emotional strength not physical.")


class Room:

    objects = []
    persons = []

    def __init__(self):
        # Room number is 17
        self.room_num = 17

        self.description = (
            "You squeeze into a cramped, cluttered room.\n"
            "Stacks of boxes, clothes, and random junk tower around you.\n"
            "You wonder if there is anything in here you can use.\n"
        )

        bed = Bed(
            "Bed",
            "A sagging bed buried in junk. It looks like you *might* be able to lie down on it.",
            False, 
            None,
            True,
        )

        weight = Weight(
            "Weight",
            "A single dusty dumbbell. Looks like it hasn't been lifted in years.",
            True,
            None,
            True,
        )

        potion = HealthPotion(
            "Health Potion",
            "A small bottle labeled 'SUPER MEGA HEAL'. The label looks fake.",
            True,  
            None,
            True,
        )

        # Add objects to objects list
        self.objects.append(bed)
        self.objects.append(weight)
        self.objects.append(potion)

        wizard = Wizard()
        self.persons.append(wizard)

        # My exits are south to room 15 and north to room 18
        self.exits = ["south", "north"]

    def enter(self, player):
        """
        Main loop for this room.
        Prints the description once, then waits for commands until the player leaves.
        """
        self.describe_room()

        # Command loop
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            # Handle the basic commands
            if command_base in ["move", "go"]:
                next_direction = self.move(other_part)
                if next_direction is not None:
                    return next_direction

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
                if self.quit_game(player) == "quit":
                    return "quit"

            elif command_base in ["help", "?"]:
                self.show_help()

            elif command_base == "hint":
                self.show_hint()

            elif command_base == "interact":
                self.interact(other_part, player)

            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        """Print the room description and list visible objects."""
        print(self.description)
        if self.objects:
            for obj in self.objects:
                if obj.visible:
                    print(f"There is a {obj.name} here.")

        if self.persons:
            for person in self.persons:
                    print(f"There is a {person.name.title()} is here.")

    def move(self, direction):
        """
        Handle movement out of this room.
        In this room, you can only go south (to room 15) or north (to room 18).
        """
        if direction is None:
            print("You must choose a direction.")
            return None

        direction = direction.lower().strip()

        if direction in ["south", "s"]:
            print("You carefully push through a wall of boxes and junk to the south.")
            return "south"

        elif direction in ["north", "n"]:
            print("You step over a pile of old newspapers and head north.")
            return "north"

        else:
            print("You can't go that way.")
            return None


    def look(self, target, player):
        """
        Handle the 'look' command.
        If no target is given, re-describe the room.
        Otherwise, try to look at an item in the room or inventory.
        """
        if target is None or target == "":
            self.describe_room()
            return

        # Try to find the item in the player's inventory first
        item = self.get_item_from_inventory(target, player)
        if item is None:
            # Then try to find it in the room's objects
            item = self.get_item_from_object_list(target)
            if item is None:
                print("There is nothing like " + target + " to look at.")
                return

        if target == item.name.lower().strip():
            print(item.description)
            if item.state is not None:
                print(f"The {item.name} is {item.state}")
            return

        print("Looking at", target, "doesn't reveal anything new.")
        return

    def use(self, item_name, player):
        """
        Handle the 'use' command.
        We do custom behavior for Bed, Weight, and Health Potion.
        Anything else falls back to that object's own use() method.
        """
        if item_name is None or item_name == "":
            print("Use what?")
            return

        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            item = self.get_item_from_object_list(item_name)

        if item is None:
            print("You can't use that.")
            return

        name = item.name.lower()

        if name == "bed":
            # give the player +5 health
            item.use()
            player.health += 5
            print("You take a quick nap and feel a bit better.")
            print(f"Your health is now {player.health}.")
            return

        if name == "weight":
            # give the player +5 score
            item.use()
            player.score += 5
            print("You do a few curls. Impressive form.")
            print(f"Your score increases to {player.score}.")
            return

        if name in ["health potion", "potion"]:
            # does nothing
            item.use()
            print("You wait for a surge of energy... but nothing changes.")
            print(f"Your health is still {player.health}.")
            return

        item.use()

    def get(self, item_name, player):
        """
        Handle picking up an item from the room and putting it in the player's inventory.
        """
        if item_name is None or item_name == "":
            print("Get what?")
            return

        # Check if the player already has the item
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return

        item = self.get_item_from_object_list(item_name)
        if item is None:
            print(f"{item_name} is not here.")
            return

        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        # Move the object into the player's inventory
        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")

    def drop(self, item_name, player):
        """
        Handle dropping an item from the player's inventory into the room.
        """
        if item_name is None or item_name == "":
            print("Drop what?")
            return

        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            print(f"You don't have the {item_name}.")
            return

        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")

    def interact(self, target, player):
        """
        Handle the 'interact' command.
        This is for talking to characters (like the wizard) in the room.
        """
        # If the player just typed 'interact' with no name
        if target is None or target == "":
            print("Interact with who? Maybe try 'interact wizard'.")
            return

        target = target.lower().strip()

        person = self.get_person_by_name(target)

        if person is None:
            print(f"You don't see anyone called '{target}' to interact with.")
            return

        person.interact()


    def show_inventory(self, player):
        """Show the player's inventory."""
        player.show_inventory()

    def show_stats(self, player):
        """Show the player's stats (health, score, etc.)."""
        player.print_stats()

    def quit_game(self, player):
        """Ask the player if they really want to quit."""
        if input("Are you sure you want to quit? (yes/no) ").lower().startswith("y"):
            print(f"Final Score: {player.score}")
            sys.exit(0)

    def show_help(self):
        """Print the list of available commands in this room."""
        print("Available commands: move, go, look, get, take, drop, use, inventory, stats, quit, help, hint, interact <person>")

    def show_hint(self):
        """Give the player a small hint about this room."""
        print("Try using some of the items... you might find something useful!")

    def unknown_command(self):
        """Fallback when the player types something we don't understand."""
        print("You can't do that here. Try something else or type 'help' for options or 'hint' for a clue.")

    def get_item_from_inventory(self, item_name, player):
        """Find an item by name in the player's inventory."""
        for item in player.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None

    def get_item_from_object_list(self, item_name):
        """Find an item by name in this room's object list."""
        for item in self.objects:
            if item.name.lower() == item_name.lower():
                return item
        return None
    
    def get_person_by_name(self, name):
        """Find a person in this room by name."""
        for person in self.persons:
            if person.name == name.lower():
                return person
        return None
