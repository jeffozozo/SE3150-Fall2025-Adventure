from object import Object
from player import Player
import sys  # For exiting the game
import time
import select

#  west,2 -  through a mousedooor (saul's object) azul_oro and a needle to fight a cockroach to go back 
#  down,4 - josh: going down the vine and it snaps set a condition 
#  south,21 - ayden hint at code 404

class Mirror(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print(f'''                                                                                                                                                                                                    
 ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                    
█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                   
█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                   
███████    ███    ████    ███████████████████████████████████████████████████████████████████████████████████████████████████████████                   
███████    ███    ████    ███████████████████████████████████████████████████████████████████████████████████████████████████████████                   
█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                   
█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                   
█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                   
███                                                                                                                         ███   ███                   
███                                                                                                                         ███   ███                   
███                                                                                                                         ███   ███                   
███                                                                                                                         ███   ███                   
███               /$$   /$$             /$$           /$$$$$$$$                                  /$$                        ███   ███
███               | $$$ | $$            | $$          | $$_____/                                 | $$                       ███   ███
███               | $$$$| $$  /$$$$$$  /$$$$$$        | $$     /$$$$$$  /$$   /$$ /$$$$$$$   /$$$$$$$                       ███   ███
███               | $$ $$ $$ /$$__  $$|_  $$_/        | $$$$$ /$$__  $$| $$  | $$| $$__  $$ /$$__  $$                       ███   ███
███               | $$  $$$$| $$  \ $$  | $$          | $$__/| $$  \ $$| $$  | $$| $$  \ $$| $$  | $$                       ███   ███
███               | $$\  $$$| $$  | $$  | $$ /$$      | $$   | $$  | $$| $$  | $$| $$  | $$| $$  | $$                       ███   ███
███               | $$ \  $$|  $$$$$$/  |  $$$$/      | $$   |  $$$$$$/|  $$$$$$/| $$  | $$|  $$$$$$$                       █████████
███               |__/  \__/ \______/    \___/        |__/    \______/  \______/ |__/  |__/ \_______/                       █████████
███                                                                                                                         █████████                   
███                                                                                                                         █████████          
███                                                                                                                         █████████          
███                                                                                                                         █████████          
███                                                                                                                         █████████                   
███                                                                                                                         ███   ███                   
███                                                                                                                         ███   ███                   
 ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████            
                                                                                                                                                                        
            ''')
        print(f"\n\nTurn away, but the mirror won’t forget you… and you shouldn’t forget it.")


class Room:

    objects = []

    def __init__(self):
        self.room_num = 0
        self.description = (
            "Bathed in a soft pink glow, the room feels warm and dreamlike, its walls shimmering like rose quartz.\n" 
            "At its center stands an ornate mirror framed in gold, said to hold more than just reflections."
        )
        self.mirror = Mirror("Mirror", "The mirror’s surface shimmers faintly, as though hiding something beneath.", False, "gaze", True)
        self.objects.append(self.mirror)
        
        #my exits
        self.exits = ["down", "west", "south"]



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
                next = self.move(other_part, player)
                if(next != None):
                    return next
            
            elif command_base == "use":
                self.use(other_part,player)

            elif command_base == "look":
                self.look(other_part, player)

            elif command_base in ["drop", "put"]:
                self.drop(other_part, player)

            elif command_base == "inventory":
                self.show_inventory(player)

            elif command_base == "stats":
                self.show_stats(player)
            elif command_base == "exits":
                print(self.exits)

            elif command_base == "quit":
                if(self.quit_game(player) == "quit"):
                    return "quit"
                

            elif command_base in ["help", "?"]:
                self.show_help()
            
            elif command_base == "hint":
                self.show_hint(player)
            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction, player):
        if direction in ["down", "d", "vine"]:
            player.condition.append("vine_snapped")
            print("You found a vine behind the curtain!")
            time.sleep(1)
            print("...")
            time.sleep(1)
            print("HURRY! PRESS <ENTER> WITHIN 4 SECONDS TO BREAK YOUR FALL!")
            i, _, _ = select.select([sys.stdin], [], [], 4)
            if i:
                sys.stdin.readline()  # player reacted in time
                print("You catch the vine just in time!")
            else:
                player.health -= 10
                print("You hit the ground hard!")
            return "down"
        elif direction in ["west","w"]:
            if "slayed_cucaracha" not in player.condition:
                print("A pest stands in your way. ")
                return None
            if "mouse" in player.condition:
                print("Through the cracks you go")
                return "west"
            else:
                print("The crack in the wall is far too small for you to fit through.")
                print("You would need to be much smaller... perhaps the size of a mouse?")
                return None
        elif direction in ["south", "s"]:
            return "south"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            print("\nYou notice:")
            print("- A curtain hiding something that might be going DOWN")
            print("- A small crack in the wall to the WEST. I think a cockroach lives there.")
            print("- A doorway leading SOUTH")
            return
        if target in ["cockroach", "cucaracha"]:
            print("Where's pest control when you need it? It's ruining my aesthetic. I need something sharp to take care of it.")
            return
        if target in ["down", "vine", "curtain"]:
            print("A thick vine hides behind a curtain, leading down into shadows.")
            return
        elif target in ["west", "crack", "wall"]:
            print("A narrow crack runs down the western wall. Too small for a person... but maybe not for a mouse?")
            if "slayed_cucaracha" not in player.condition:
                print("A large cockroach guards the crack.")
            return
        elif target in ["south", "doorway"]:
            print("A simple doorway leads south to another chamber.")
            return
        item = self.get_item_from_inventory(target,player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None:
                print("There is nothing like " + target + " to look at.")
                return
        if item == self.mirror:
            item.use()
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
        if item in ["Dagger", "Needle", "Mjolnir"]:
            print("Goodjob Amig@! The mousedoor is no longer gaurded by la cucaracha! La cucaracha! \nYa no puede caminar. porque no tiene...porque no tiene... patas para caminar. ")
            player.condition.append("slayed_cucaracha")
        #this room only allows you to use the objects in the list or inventory. That is not a global constraint however and you can add whatever use functions you like.
        if(item == None):
            print("you can't use that.")
            return
        
        item.use()
        
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
        print("Available commands: move, go, look, use, drop, inventory, stats, exits, quit, help, hint")

    def show_hint(self, player):
        print(
            """Try looking at the mirror more closely...
            There's a vine hidden behind a curtain that leads down.
            That crack in the wall looks too small... unless you were smaller?
            Take a LOOK at these exits: down, west, south.
            """)
        if "slayed_cucaracha" not in player.condition:
            print("A cockroach blocks the western passage. You'll need something sharp.")
        elif "mouse" not in player.condition:
            print("The western crack is too small. Perhaps the mirror holds secrets about transformation?")
        else:
            print("You seem ready to explore. Try the available exits: west, down, south")

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
    
