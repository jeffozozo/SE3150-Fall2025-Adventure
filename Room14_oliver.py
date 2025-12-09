from object import Object
from player import Player
import sys
import time
import threading
import os

def timed_input(prompt, timeout=10):
    """
    Captures user input with a visual timeout progress bar.
    The bar is displayed on the line ABOVE the input prompt to avoid 
    overwriting the user's text.
    """
    
    # Enable VT100/ANSI support on Windows 10+ (hack mostly for Windows CMD)
    if os.name == 'nt':
        os.system('')

    user_input = []
    
    def get_user_input():
        try:
            # Input is blocking, so we run it in this thread.
            # We use an empty prompt here because we print the prompt manually below.
            data = input()
            user_input.append(data)
        except EOFError:
            pass

    # 1. Print an empty line for the Progress Bar to occupy
    print() 
    
    # 2. Print the Prompt on the next line (end='' ensures no extra newline yet)
    print(prompt, end=' ', flush=True)
    
    # Start the input thread
    input_thread = threading.Thread(target=get_user_input)
    input_thread.daemon = True
    input_thread.start()

    start_time = time.time()
    
    bar_length = 30
    fill_char = '█'
    empty_char = '-'

    # ANSI Escape Codes
    # \033[s : Save cursor position
    # \033[1A: Move cursor UP 1 line
    # \r     : Move to start of line
    # \033[u : Restore cursor position
    
    while input_thread.is_alive():
        elapsed = time.time() - start_time
        remaining = timeout - elapsed

        if remaining <= 0:
            break

        percent_remaining = max(0, remaining / timeout)
        filled_length = int(bar_length * percent_remaining)
        bar = fill_char * filled_length + empty_char * (bar_length - filled_length)
        
        # We update the line ABOVE the input, then restore the cursor 
        # so typing isn't interrupted.
        sys.stdout.write(f"\033[s\033[1A\rTime Left: |{bar}| {remaining:.1f}s \033[u")
        sys.stdout.flush()
        
        time.sleep(0.1)

    if user_input:
        # User pressed enter
        sys.stdout.write('\n') # Move past the input line
        return user_input[0]
    else:
        # Time ran out
        # Move cursor to bottom to avoid messing up terminal history
        sys.stdout.write('\n\nTime is up!\n')
        return None

def printwait(text):
    print(text, end=" ")
    input("[PRESS ENTER TO CONTINUE]")

class LifeBuoy(Object):
    def __init__(self):
        super().__init__("Life Buoy", "Lets you float in water.", True, None, True)
    def use(self):
        print("The life buoy can't be used here.")

class Room:
    objects = []
    def __init__(self):
        self.room_num = 14
        self.description = ("You're in an obstacle course in the sea! The only way out is to go north through it.\nYou will need to be fast with your answers.\nYou wonder why there is an entire ocean contained solely within this room.")
        self.exits = ["north"]

    # this gets called when the player enters the room.
    def enter(self, player):
        # step 1 - Print the room description
        self.describe_room()

        item = self.get_item_from_inventory("life buoy",player)
        if item:
            print("You have a life buoy. You can skip the obstacle course with it. Go north and use it when prompted to use it.")

        # step 2 - make your own command loop - watch carefully about how to parse commands:
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            if command_base in ["move", "go"]:
                next = self.move(other_part, player)
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

    def move(self, direction, player):
        if direction in ["north", "n"]:
            item = self.get_item_from_inventory("life buoy",player)
            if item:
                print("")
                if input("You have a life buoy. Do you want to use it? (this will not consume the item) (y/N) ").lower().startswith('y'):
                    print("You put on the life buoy, and skipped the obstacle course.")
                    return "north"
                
            print("You jump over to a box, which doesn't feel stable.")
            printwait("You come across a set of barrels.")
            answer = timed_input("What is the 7th letter in this sentence?",10)
            answer : str
            if answer == None:
                print("You ran out of time and the box collapsed.")
                printwait("Thankfully, you didn't drown, but you lost 10 health.")
                
                self.damage_player(player, 10)
            elif answer and answer.lower() == "t":
                printwait("You jumped over to a barrel.")
            else:
                print("You jumped over to a barrel, but it collapsed!")
                printwait("Thankfully, you didn't drown, but you lost 10 health.")
                self.damage_player(player, 10)
            answer = timed_input("There's a seagull above you that's about to attack you! Hurry, dodge with 'a'!", 2)
            if answer and answer.lower() == 'a':
                printwait("You dodged out of the way.")
            else:
                print("Ouch! -10 Health.")
                self.damage_player(player, 10)
                print("You also suffer emotional damage.")
                if "Emotionally Damaged" not in player.condition:
                    player.condition.append("Emotionally Damaged")
            printwait("Suddenly, a math textbook appears! It has 1000HP and 1000PG (pages).")
            answer = timed_input("It asks you: What is missing here? sin(x) = ___(pi/2 - x)")
            if answer and answer.lower() in ["cos", "cosine"]:
                printwait("You told it the correct answer and then threw it in the sea.")
            else:
                if answer:
                    print("You told it the wrong answer, and tried to throw it in the sea.")
                else:
                    print("You didn't care what the answer was, and tried to throw it in the sea.")
                printwait("But it gave you a papercut! -99999999 Health!")
                printwait("...It might've just been -1 health, but it didn't feel like that.")
                # imagine if you died to this
                self.damage_player(player, 1)
            
            if not player.has_item("life buoy"):
                print("You found a lifebuoy!")
                player.inventory.append(LifeBuoy())
            print("You continued on to the north and finally reached the shore.")
            print("The shore had a building near it. You entered the building.")
            return "north"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == ""):
            self.describe_room()
            return
    
        # Check if the object is in the room object list or in the player's inventory and print its description and status.
        # the table could have been an object if we wanted it to be - then it would be like the lamp. In this case we chose
        # not to make the table an object and it was handled special case above. 
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
        
        # This room only allows you to use the objects in the list or inventory
        if(item == None):
            print("you can't use that.")
            return
        
        if item.name.lower() == "life buoy" :
            print("You need to use the life buoy when prompted while going north.")
            return
        item.use()

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
    
    def damage_player(self, player, amount):
        player.health -= amount
        if not player.is_alive():
            print("You have perished in the dungeon! Game over. Your score is:", player.score)
            sys.exit(0)

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
        print("Available commands: move, go, look, get, take, drop, inventory, stats, quit, help, hint")

    def show_hint(self):
        print("Move north to proceed. The phrase 'tacos' might help when answering questions.")

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
    