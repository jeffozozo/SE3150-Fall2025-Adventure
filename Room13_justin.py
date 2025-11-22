from object import Object
from player import Player
import sys  # For exiting the game


class vial(Object):

    def __init__(self, name, description, can_be_gotten, state, visible, is_poison):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)
        
        # Hidden boolean decides if poison or health potion
        self._is_poison = is_poison

    def use(self, player=None):
        # Vial contents will only have an effect if the player
        # is passed in as a parameter
        if player:
            if self.state == "full":
                self.name = "empty vial"

                # change the state and description of vial
                self.state = "empty"
                self.description = "A clear empty vial"
                print(f"You drink the contents of the {self.name}.")
                
                # Case where the vial contains poison
                if self._is_poison:
                    print("The taste is mildly refreshing... for a moment")
                    # Player's health is halved
                    player.health = player.health // 2
                    
                    # Players condition is marked as "weakened"
                    if "healthy" in player.condition:
                        player.condition.remove("healthy")
                    if "weakened" not in player.condition:
                        player.condition.append("weakened")
                   
                    print("You begin to struggle to breathe. Your vision gets blurry.")
                    print("Despite not being able to see you know that mysterious man is smiling.")
                    print("Your health has been halved.")
                    print(f"Current Health: {player.health}")

                # Case where the vial contains health potion
                else:
                    print("The taste is quite bitter.")
                    print("Despite the initial burn, you begin to feel a rush of energy.")
                    
                    # restores player health
                    player.health = 100

                    # restores player condition
                    if "weakened" in player.condition:
                        player.condition.remove("weakened")
                    if "healthy" not in player.condition:
                        player.condition.append("healthy")

            else:
                self.state = "empty"
                print(f"The vial is empty.")
        
        # If player isn't passed in as a parameter the potion will
        # have no effect
        else:
            print("the vial is not drinkable at the moment")
            print("Maybe try returning to the room where you found it.")

class Room:

    objects = []

    def __init__(self):
        self.room_num = 13
        self.description = ("You find yourself in a small, damp chamber. \nThe stone walls weep moisture, and the air is heavy and still.\nIn the far corner, sits a Mystery Man in a dark, hooded cloak.\nHe sits at a worn, stone table, seemingly waiting. \nThe only way out is a ladder going Up and a dark pit leading Down.")
        # other room setup - add the lamp and set up the exits.
        vial1 = vial("Left Vial", "A vial filled with a dark red liquid", False, "full", False, False)
        vial2 = vial("Right Vial", "A clear vial that shimmers faintly", False, "full", False, True)
        self.objects.append(vial1)
        self.objects.append(vial2)
        
        #this is how you declare your exits. It doesn't matter what room the attach to, I'll worry about that in the global level. 
        self.exits = ["down", "up"]
        self.vials_offered = False


    def enter(self, player):

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
            
            elif command_base == "drink":
                self.drink(other_part,player)

            elif command_base in ["refuse", "leave"]:
                if self.vials_offered:
                    self.refuse()
                else:    
                    self.unknown_command()

            elif command_base in ["drop", "put"]:
                self.drop(other_part, player)

            elif command_base == "inventory":
                self.show_inventory(player)

            elif command_base == "talk":
                self.mystery_man_dialogue()

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
                if obj.visible:
                    print(f"There is a {obj.name}")

    def mystery_man_dialogue (self):
        if self.vials_offered:
            print("The mysterious man nods. He seems to have nothing more to say.")
            return
        print("You approach the mysterious man.")
        print("He slowly lifts his head, his eyes burning through the shadows.\nHis face is obscured by his hood.")

        print("He produces two small vials, one in his left hand, one in his right.")
       
        self.vials_offered = True
        
        # Make vials visible
        left_vial = self.get_item_from_object_list("left vial")
        right_vial = self.get_item_from_object_list("right vial")
        left_vial.visible = True
        right_vial.visible = True
        print('"I have prepared a choice for you, traveler," he rasps, his voice like grinding stone.')
        print('"In one vial, a poison. In the other, a health potion that will restore you completely."')
        print('"You may drink **one** now and keep the other, or you may choose to leave them **both** behind."')
        print('\nWhich do you choose?')
        print('Drink the vial from his Left hand.')
        print('Drink the vial from his Right hand.')
        print('Refuse the offer and leave them.')
        return

    def refuse(self):
        print("You refuse the deal. The mysterious man shrugs and put the vials inside his cloak.")
        left_vial = self.get_item_from_object_list("left vial")
        right_vial = self.get_item_from_object_list("right vial")
        
        # Set vials to not visible 
        left_vial.visible = False
        right_vial.visible = False
        
        #By setting this to False the player can go through
        #the interaction again to change their choice
        self.vials_offered = False

    def drink(self,target, player):
        if target in ["left", "left vial","Poison Vial","poison vial"]:
            
            # Player drinks left vial
            left_vial = self.get_item_from_inventory(target,player) 
            if left_vial == None:
                left_vial = self.get_item_from_object_list(target)
            if left_vial == None or not left_vial.visible:
                print(f"Unable to drink {target}")
                return
            left_vial.use(player)
            
            # Right vial is marked gettable
            right_vial = self.get_item_from_inventory("right vial",player)
            if right_vial == None:
                right_vial = self.get_item_from_object_list("empty vial")
                #if the vial is empty it is marked gettable
                if right_vial:
                    right_vial.can_be_gotten = True
                    return

            if right_vial == None:
                right_vial = self.get_item_from_object_list("right vial")
            if right_vial == None:
                print(f"Unable to find {target}")
                return
            right_vial.can_be_gotten = True
            right_vial.name = "Poison Vial"

        if target in ["right", "right vial","health potion"]:
            
            # Player drink right vial
            right_vial = self.get_item_from_inventory(target,player)
            if right_vial == None:
                right_vial = self.get_item_from_object_list(target)
            if right_vial == None or not right_vial.visible:
                print(f"Unable to drink {target}")    
                return
            right_vial.use(player)

            # Left vial is marked gettable 
            left_vial = self.get_item_from_inventory("left vial",player) 
            if left_vial == None:
                left_vial = self.get_item_from_object_list("empty vial")
                
                #if the vial is empty it is marked gettable
                if left_vial:
                    left_vial.can_be_gotten = True
                    return

            if left_vial == None:
                left_vial = self.get_item_from_object_list("left vial")
            if left_vial == None:
                print(f"Unable to find {target}")
                return
            left_vial.can_be_gotten = True
            left_vial.name = "Health Potion"
        
        return

    def move(self, direction):
        if direction in ["down", "d" ]:
            print("You take a leap of faith into the dark pit.")
            return "down"
        # 
        elif direction in ["Up" ,"u"]:
            print("You climb up the ladder.")
            return "up"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return
        if target == "vial" and self.vials_offered:
            print("which vial would you like to look at?")
            print(" the **right vial** or the **left vial**?")
        if target == "table":
            print("A small square table with two chairs on opposing ends")
            return
        if target in ["man","mystery man", "dude"]:
            if self.vials_offered:
                print("The mysterious man nods. He seems to have nothing more to say.")
            else:
                print("A mysterious man in a dark robe sits in the corner staring at you.")
            return
        
        # Check if the object is in the room or in the player's inventory and print it description and status. You can use this code exactly.
        item = self.get_item_from_inventory(target,player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None or not item.visible:
                print("There is nothing like " + target + " to look at.")
                return
        if target == item.name.lower().strip():
            print(item.description) 
    
    # you can use this as well. haha get it? use this...
    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)
            if not item.visible:
                item = None

        #this room only allows you to use the objects in the list or inventory. That is not a global constraint however and you can add whatever use functions you like.
        if(item == None):
            print("you can't use that.")
            return
        
        item.use(player)
        

    # this code could also probably be used verbatim
    def get(self, item_name, player):

        # Check if the player already has the item in their inventory
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        
        item = self.get_item_from_object_list(item_name)
        if(item == None or not item.visible):
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
        if self.vials_offered:
            print("Available commands: move, go, look, get, take, refuse, drink, drop, inventory, talk, stats, quit, help")
            return
        else:
            print("Available commands: move, go, look, get, take, drop, inventory, talk, stats, quit, help")

    def show_hint(self):
        if not self.vials_offered:
            print("Maybe try talking to the mysterious man.")
            return
        print("The choice is yours.")

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
    
