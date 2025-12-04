from object import Object
from player import Player
import sys  # For exiting the game

class Book(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # Using the book places it on the shelf or removes it
        if self.state == "off":
            self.state = "on"
            print(f"You carefully place the book back onto the empty shelf.")
            print(f"You hear a soft click as the book slides into place...")
        else:
            self.state = "off"
            print(f"You remove the book from the shelf.")
            print(f"The passage seems to seal itself once more.")

class Room:

    objects = []

    def __init__(self):
        self.room_num = 18
        self.description = self.description = (
        "The room is lit like an old library. The lights are soft and warm, creating a mystic, almost enchanted atmosphere.\n"
        "Bookshelves line the walls to the south and east, filled with old books and artifacts.\n"
        "I notice several empty spaces among them...\n"
        "Scattered across the floor are various books that must have fallen from the shelves.\n"
    )


        # other room setup - add the lamp and set up the exits.
        book = Book("Book", "An old, dusty book with a leather cover.", True, "off", True)
        self.objects.append(book)
        
        #this is how you declare your exits. It doesn't matter what room the attach to, I'll worry about that in the global level. 
        self.exits = ["south", "east"]



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
        # Check for book in both room and player inventory
        book = self.get_item_from_object_list("book")
        if book is None:
            book = self.get_item_from_inventory("book", player)
        
        book_placed = book is not None and book.state == "on"
        
        if direction in ["south", "s"]:
            if book_placed:
                print(
                    "You walk to the south bookshelf near where you placed your book.\n"
                    "A hidden passage has opened behind it. You step through the passage."
                )
                return "south"
            else:
                print("The south bookshelf blocks your way. Perhaps something needs to be done first...")
                return None
        elif direction in ["east", "e"]:
            if book_placed:
                print(
                    "You walk to the east bookshelf close to where you placed your book.\n"
                    "A secret door has revealed itself. You enter the door."
                )
                return "east"
            else:
                print("The east bookshelf is just a wall of books. You can't go that way.")
                return None
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        if target == "bookshelf" or target == "shelf":
            print("The bookshelf is filled with old books, but light seems to glint off an empty space where a book should be.")
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
                if item.state == "on":
                    print(f"The {item.name} is placed on the shelf.")
                else:
                    print(f"The {item.name} is not on the shelf.")
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
        print("Available commands: move, go, look, get, take, drop, inventory, stats, quit, help, hint")

    def show_hint(self):
        print("I wonder if the book on the floor has anything to do with those empty spaces on the shelves...")

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
    
