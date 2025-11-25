from object import Object
from player import Player
import sys
import random
import time


# Fake Key object - red herring
class FakeKey(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("You try to use the rusty key on the door, but it doesn't fit! It's the wrong key!")


# Real Key object - unlocks the door
class RealKey(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("This is the correct key! Use it to unlock the door.")


# Grandfather Clock object
class GrandfatherClock(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("The grandfather clock ticks steadily. You need to examine it more closely.")


# Fake Keypad object - red herring
class FakeKeypad(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("You press some buttons on the keypad, but nothing happens. It seems to be a decoy!")


# Door object
class Door(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("The door is locked. You need a key to unlock it.")


class Room:
    objects = []

    def __init__(self):
        self.room_num = 16
        self.description = (
            "You enter an elegant Victorian study with dark mahogany walls and plush carpeting.\n"
            "A massive grandfather clock stands against the north wall, its pendulum swinging rhythmically.\n"
            "To the west, an ornate wooden door blocks your exit. Next to the door is a modern-looking keypad.\n"
            "On a small table near the door, you notice a rusty old key.\n"
            "The air feels thick with mystery and the ticking of the clock echoes through the room.\n"
        )
        
        # Create objects
        fake_key = FakeKey("rusty_key", "A rusty, worn key that looks ancient. Could this unlock the door?", True, None, True)
        real_key = RealKey("key_16_west", "A gleaming brass key with intricate engravings. This looks important!", True, None, False)
        clock = GrandfatherClock("clock", "An imposing grandfather clock made of dark wood with brass fixtures. It ticks loudly.", False, "locked", True)
        keypad = FakeKeypad("keypad", "A modern electronic keypad mounted on the wall. It has numbered buttons.", False, None, True)
        door = Door("door", "A heavy wooden door with brass fittings. It's locked tight.", False, "locked", True)
        
        self.objects.append(fake_key)
        self.objects.append(real_key)
        self.objects.append(clock)
        self.objects.append(keypad)
        self.objects.append(door)
        
        # Track if clock is unlocked
        self.clock_unlocked = False
        self.door_unlocked = False
        
        # Exits
        self.exits = ["west"]



    def enter(self, player):
        # Print the room description
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

            # Process commands
            if command_base in ["move", "go"]:
                next_room = self.move(other_part, player)
                if next_room is not None:
                    return next_room
            
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
                self.show_hint(player)
            
            elif command_base == "examine":
                self.examine(other_part, player)
            
            elif command_base == "unlock":
                self.unlock(other_part, player)
            
            elif command_base == "solve":
                if other_part in ["clock", "puzzle"]:
                    self.solve_clock_puzzle(player)
                else:
                    print("What do you want to solve?")
            
            elif command_base == "enter" and other_part == "code":
                self.try_keypad()
            
            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        print(self.description)
        visible_objects = [obj for obj in self.objects if obj.visible]
        if visible_objects:
            print("\nYou can see:")
            for obj in visible_objects:
                print(f"  - A {obj.name}")

    def move(self, direction, player):
        if direction in ["west", "w", "door"]:
            if self.door_unlocked:
                print("You unlock the door with the brass key and step through to the west!")
                player.score += 50  # Reward for solving the puzzle
                return "west"
            else:
                print("The door is locked. You need to find the correct key to unlock it.")
                return None
        else:
            print("You can't go that way. The only exit is west through the door.")
            return None

    def look(self, target, player):
        if target == "" or target is None:
            self.describe_room()
            return

        # Check specific room features
        if target in ["room", "around"]:
            self.describe_room()
            return
        
        if target in ["clock", "grandfather_clock", "grandfather clock"]:
            clock = self.get_item_from_object_list("clock")
            if clock and clock.state == "locked":
                print("The grandfather clock is magnificent. Its face shows intricate Roman numerals.")
                print("There's a small compartment on the front that appears to be locked.")
                print("Perhaps you need to solve a puzzle to open it...")
            elif clock and clock.state == "unlocked":
                print("The clock's compartment is now open, revealing where the brass key was hidden.")
            return
        
        if target in ["keypad", "pad"]:
            print("The keypad has buttons numbered 0-9. It looks high-tech but somehow out of place in this Victorian study.")
            return
        
        if target == "door":
            print("A heavy wooden door with a brass lock. You'll need a key to open it.")
            return

        # Check if the object is in the room or in the player's inventory
        item = self.get_item_from_inventory(target, player)
        if item is None:
            item = self.get_item_from_object_list(target)
            if item is None:
                print(f"There is nothing like {target} to look at.")
                return

        print(item.description)
        if item.state is not None:
            print(f"The {item.name} is {item.state}")

    def examine(self, target, player):
        """More detailed examination than look"""
        if target in ["clock", "grandfather_clock", "grandfather clock"]:
            clock = self.get_item_from_object_list("clock")
            if clock and clock.state == "locked":
                print("You examine the grandfather clock closely.")
                print("There's a small locked compartment near the base of the clock face.")
                print("A brass plate reads: 'Only the quick-minded may unlock this secret.'")
                print("Type 'solve clock' to attempt the puzzle.")
            elif clock and clock.state == "unlocked":
                print("The compartment is open and empty now.")
            return
        else:
            # Default to look behavior
            self.look(target, player)

    def solve_clock_puzzle(self, player):
        """Mental math puzzle with timer"""
        clock = self.get_item_from_object_list("clock")
        if not clock:
            return
        
        if clock.state == "unlocked":
            print("You've already solved the clock puzzle!")
            return
        
        print("\n" + "="*60)
        print("THE GRANDFATHER CLOCK PUZZLE")
        print("="*60)
        print("The clock begins to chime! A voice echoes:")
        print("'Answer these mathematical riddles quickly, or remain locked forever!'")
        print("\nYou have 30 seconds to answer 3 questions correctly!")
        print("="*60 + "\n")
        
        time.sleep(2)
        
        # Generate 3 random math problems
        questions = self.generate_math_questions()
        correct_answers = 0
        
        start_time = time.time()
        time_limit = 30
        
        for i, (question, answer) in enumerate(questions, 1):
            elapsed = time.time() - start_time
            remaining = time_limit - elapsed
            
            if remaining <= 0:
                print(f"\n⏰ TIME'S UP! You ran out of time!")
                print("The clock's compartment remains locked.")
                return
            
            print(f"\nQuestion {i}/3 (Time remaining: {remaining:.1f}s)")
            print(question)
            
            try:
                user_answer = input("> ").strip()
                if user_answer == str(answer):
                    correct_answers += 1
                    print("✓ Correct!")
                else:
                    print(f"✗ Wrong! The answer was {answer}")
            except:
                print("✗ Invalid input!")
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*60)
        if correct_answers == 3 and elapsed <= time_limit:
            print(f"🎉 SUCCESS! You answered all questions correctly in {elapsed:.1f} seconds!")
            print("="*60)
            print("\nThe grandfather clock chimes triumphantly!")
            print("The small compartment clicks open, revealing a gleaming brass key inside!")
            
            # Unlock the clock and make the real key visible/gettable
            clock.state = "unlocked"
            real_key = self.get_item_from_object_list("key_16_west")
            if real_key:
                real_key.visible = True
                print("You can now 'get key_16_west' to take the brass key!")
            
            player.score += 30  # Reward for solving puzzle
            self.clock_unlocked = True
        else:
            print(f"You got {correct_answers}/3 correct.")
            print("The clock's compartment remains locked. Try again!")
            print("="*60)

    def generate_math_questions(self):
        """Generate 3 random math questions"""
        questions = []
        
        # Question 1: Addition
        a, b = random.randint(10, 50), random.randint(10, 50)
        questions.append((f"What is {a} + {b}?", a + b))
        
        # Question 2: Subtraction
        a, b = random.randint(50, 100), random.randint(10, 40)
        questions.append((f"What is {a} - {b}?", a - b))
        
        # Question 3: Multiplication
        a, b = random.randint(5, 15), random.randint(2, 9)
        questions.append((f"What is {a} × {b}?", a * b))
        
        return questions

    def try_keypad(self):
        """Try to use the keypad (it's a fake)"""
        print("\nYou approach the keypad and try entering various codes...")
        print("Nothing happens. The keypad appears to be non-functional.")
        print("Perhaps it's just a decoy to distract you from the real puzzle!")

    def unlock(self, target, player):
        """Try to unlock something"""
        if target in ["door", "west door"]:
            # Check if player has the real key
            if player.has_item("key_16_west"):
                print("You insert the brass key into the door's lock...")
                print("*Click* The door unlocks!")
                self.door_unlocked = True
                door = self.get_item_from_object_list("door")
                if door:
                    door.state = "unlocked"
            elif player.has_item("rusty_key"):
                print("You try the rusty key in the lock, but it doesn't fit at all!")
                print("This must be the wrong key.")
            else:
                print("You don't have a key to unlock the door with.")
        else:
            print(f"You can't unlock {target}.")

    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            item = self.get_item_from_object_list(item_name)
        
        if item is None:
            print("You can't use that.")
            return
        
        # Special handling for using keys
        if item_name in ["key_16_west", "rusty_key"]:
            self.unlock("door", player)
        else:
            item.use()

    def get(self, item_name, player):
        # Check if the player already has the item
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        
        item = self.get_item_from_object_list(item_name)
        if item is None:
            print(f"{item_name} is not here.")
            return
        
        if not item.visible:
            print(f"You don't see any {item_name} here.")
            return
        
        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        # Add the object to the player's inventory and remove it from the room
        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            print(f"You don't have the {item_name}.")
            return
        
        # Remove the item from inventory and put it in the object list
        player.inventory.remove(item)
        item.visible = True
        self.objects.append(item)
        print(f"You drop the {item.name}.") 

    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()

    def quit_game(self, player):
        if input("Are you sure you want to quit? (yes/no) ").lower().startswith('y'):
            print(f"Final Score: {player.score}")
            return "quit"

    def show_help(self):
        print("\nAvailable commands:")
        print("  move/go <direction> - Move in a direction (west)")
        print("  look [item] - Look at the room or an item")
        print("  examine <item> - Examine something more closely")
        print("  get/take <item> - Pick up an item")
        print("  drop <item> - Drop an item from inventory")
        print("  use <item> - Use an item")
        print("  unlock <item> - Try to unlock something")
        print("  solve clock - Attempt the grandfather clock puzzle")
        print("  inventory - Show your inventory")
        print("  stats - Show your stats")
        print("  hint - Get a hint")
        print("  help/? - Show this help message")
        print("  quit - Quit the game")

    def show_hint(self, player):
        if not self.clock_unlocked:
            print("\nHint: The grandfather clock seems important. Try examining it closely.")
            print("The keypad and rusty key might just be distractions...")
        elif self.clock_unlocked and not player.has_item("key_16_west"):
            print("\nHint: You've unlocked the clock! Don't forget to get the brass key inside.")
        elif player.has_item("key_16_west") and not self.door_unlocked:
            print("\nHint: You have the brass key. Try using it to unlock the door!")
        else:
            print("\nHint: You're ready to go west through the door!")

    def unknown_command(self):
        print("You can't do that here. Try 'help' for a list of commands or 'hint' for a clue.")

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
    
