from object import Object
from player import Player
import sys  # For exiting the game


class Potion(Object):
    def __init__(self, name, description, can_be_gotten, state, visible, player : "Player | None"):
        self.player_handle = player
        self.health_increase = 15
        super().__init__(name, description, can_be_gotten, state, visible)
    def use(self):
        print("You drink the potion, it has a sweet flavor to it and leaves you feeling rejuvenated")
        print(f"You gained {self.health_increase} health")
        if self.player_handle:
            self.player_handle.health += self.health_increase
class Chest(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)
        self.sealed = True
        self.riddling_begun = False
    def use(self):
        print("The chest awaits your answers to its riddles, type \"begin\" to start and \"stop\" to stop\n once you stop however, the chest may be sealed forever")


class Room:
    objects = []

    def __init__(self):
        self.room_num = 0
        self.questions_answered = 0
        self.location = "room"
        self.has_entered_previously = False
        self.has_riddled_previously = False
        self.riddling_attempts = 5
        self.questions_answered = 0        
        self.chest = Chest("Chest", "A small wooden chest, it's locked", False, "locked", True)
        self.reward: "Potion" = Potion(
                    "Potion",
                    "A potion with a red liquid in it",
                    False,
                    "",
                    False,
                    None
                )
            
        self.objects.append(self.chest)
        self.answers = [
            ["dragon", "a dragon", "wyrm", "a wyrm"], 
            ["a golem", "golem"], 
            ["a portal", "portal", "a gate", "gate", "dimension door"]
        ]
        self.questions = [
            "I guard my treasure day and night,\nScales like armor, breath of blight.\nBrave the fire if you dare\nWhat creature waits within its lair?", 
            "Born from stone, yet I walk as men.\nStrike me down, I rise again.\nSilent sentinel, carved with grace\nWhat stands watch in an ancient place?", 
            "I vanish in sunlight, appear in the gloam,\nA pathway to danger or to a new home.\nStep through my shimmer, your fate may unfold\nWhat am I, woven of magic untold?"
        ]
        self.description = (
            "You find yourself in a well-illuminated room with a small wooden chest in the center\n"
            "A note on the chest reads \"Answer me these questions three, and rewards I will bestow upon ye\"\n"
            "There is a corridor to your east, a flight of stairs leading up, and a flight of stairs leading down"
        )



        # other room setup - add the lamp and set up the exits.

        #this is how you declare your exits. It doesn't matter what room the attach to, I'll worry about that in the global level. 
        self.exits = ["up", "down", "east"]



    def enter(self, player):

        # step 1 - Print the room description
        if self.has_entered_previously == True:
            self.description = (
                "The light that filled this room has been snuffed out, and the chest is gone"
            )
            self.objects = []
        self.describe_room()
        self.reward.player_handle = player
        if self.objects:
            self.objects[0].player_handle = player
        

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
            elif command_base == "begin" and self.chest:
                if self.has_riddled_previously:
                    print("The chest is not accepting new answers")
                else:
                    self.chest.riddling_begun = True
                    print(self.questions[0])
                
            elif command_base in ["help", "?"]:
                self.show_help()
            
            elif command_base == "hint":
                self.show_hint()
            elif self.chest and self.chest.riddling_begun:
                self.do_riddling((command_base + " " + other_part).strip(), player)
            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["down", "d"]: #add any oYou're in a darkther commands that might go down
            print("You descend down the stairs")
            self.has_entered_previously = True
            self.chest = None
            return "down"
        elif direction in ["up", "u"]:
            print("You ascend up the stairs")
            self.has_entered_previously = True
            self.chest = None
            return "up"
        elif direction in ["east", "e"]:
            print("you go back through the corridor")
            self.has_entered_previously = True
            self.chest = None
            return "east"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == ""):
            self.describe_room()
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
        print("Answer the chest's riddles, but answer carefully for you have limited attempts")

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
    
    def give_minor_reward(self, player):
        if self.chest:
            self.chest.riddling_begun = False
        print("However, as you turn away in defeat, it shifts open and within there lies a strange potion")
        player.inventory.append(self.reward)
        player.score += 20
        print("Congratulations, you received a healing potion")
        self.has_riddled_previously = True

    def give_major_reward(self, player):
        hp_added = 50
        if self.chest:
            self.chest.riddling_begun = False
        print("The chest opens to reveal a holy orb within it, as you grasp it you find yourself feeling stronger")
        print(f"You gained {hp_added} health")
        player.health += hp_added
        player.score += 50

    def do_riddling(self, cmd, player):
        if cmd == "stop":
            if self.chest:
                self.chest.riddling_begun = False
            print("You shout into the room, and the note on the chest disappears")
            if self.questions_answered == 3:
                self.give_major_reward(player)
            elif self.questions_answered == 2:
                self.give_minor_reward(player)
            else:
                print("The chest locks tight, it seems your chance to get the valuables locked within is gone")
            self.has_riddled_previously = True
            return 
        if cmd in self.answers[self.questions_answered]:
            self.questions_answered += 1
            if self.questions_answered > len(self.answers) - 1 and self.chest:
                self.give_major_reward(player)
                self.has_riddled_previously = True
                return
            print("The chest glows in response, it seems your answer was correct")
            print(self.questions[self.questions_answered])
        else:
            self.riddling_attempts -= 1
            if self.riddling_attempts <= 0:
                print("The chest locks tight, it seems to be disappointed in you")
                if self.questions_answered == 2:
                    self.give_minor_reward(player)
                self.has_riddled_previously = True
                return
            print("The chest does not react, perhaps answer more astutely next time")
            print(f"You have {self.riddling_attempts} attempts left")



    
