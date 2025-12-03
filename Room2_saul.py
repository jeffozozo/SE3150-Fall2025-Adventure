from object import Object
from player import Player
import sys  

# Room 2 - Saul Aguiar
# Connections: south (Room 1), east (Room 3 - requires mouse form), up (Room 6)
# Features: azul_oro ring for mouse transformation, needle for later use

class AzulOro(Object):
    """A mystical ring that allows transformation into a mouse"""
    
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)
    
    def use(self):
        print("You must 'wear' the ring to use its power.")


class Needle(Object):
    """A sharp needle that could be useful as a weapon"""
    
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)
    
    def use(self):
        print("The needle is sharp. It might be useful for fighting something small...")


class Room:

    def __init__(self):
        self.room_num = 2
        self.description = (
            "You emerge into a dimly lit stone chamber, its walls lined with flickering torches.\n"
            "The air is thick with the smell of aged cheese and the constant skittering of tiny feet.\n"
            "Dozens of rats scatter across the floor, their eyes glinting in the torchlight.\n"
            "Scattered chunks of moldy cheese lie everywhere, clearly the source of the infestation.\n"
            "A narrow passage leads UP toward fresher air, and a wider corridor heads SOUTH.\n"
            "To the EAST, you notice a tiny crack in the wall - far too small for a human to pass through.\n"
        )
        
        self.objects = []
        
        azul_oro = AzulOro(
            "azul_oro", 
            "A beautiful golden ring with a blue sapphire. Ancient runes are etched along its band.", 
            True, 
            "unworn", 
            True
        )
        self.objects.append(azul_oro)
        
        needle = Needle(
            "needle",
            "A long, sturdy needle made of steel. Sharp enough to pierce through leather.",
            True,
            "sharp",
            True
        )
        self.objects.append(needle)
        
        self.exits = ["south", "east", "up"]

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
                next_direction = self.move(other_part, player)
                if next_direction is not None:
                    return next_direction
            
            elif command_base == "use":
                self.use(other_part, player)

            elif command_base == "wear":
                self.wear(other_part, player)

            elif command_base == "remove":
                self.remove(other_part, player)

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
            
            else:
                self.unknown_command()

    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                if obj.visible:
                    print(f"There is a {obj.name} here.")

    def move(self, direction, player):
        """Handle player movement with mouse transformation requirement for east"""
        if direction in ["south", "s"]:
            print("You head south through the wide corridor.")
            return "south"
        
        elif direction in ["up", "u"]:
            print("You climb up toward fresher air.")
            return "up"
        
        elif direction in ["east", "e"]:
            # Check if player is a mouse
            if "mouse" in player.condition:
                print("In your mouse form, you easily squeeze through the tiny crack in the wall.")
                return "east"
            else:
                print("The crack in the wall is far too small for you to fit through.")
                print("You would need to be much smaller... perhaps the size of a mouse?")
                return None
        
        else:
            print("You can't go that way.")
            return None

    def wear(self, item_name, player):
        """Custom command to wear the azul_oro ring"""
        if item_name in ["ring", "azul_oro", "azul oro"]:
            ring = player.get_item("azul_oro")
            if ring is None:
                ring = self.get_item_from_object_list("azul_oro")
                if ring is None:
                    print("You don't have the ring.")
                    return
                else:
                    print("You need to pick up the ring first.")
                    return
            
            if ring.state == "worn":
                print("You're already wearing the ring!")
                return
            
            # Transform into mouse
            ring.state = "worn"
            if "mouse" not in player.condition:
                player.condition.append("mouse")
            
            print("You slip the azul_oro ring onto your finger.")
            print("The blue sapphire begins to glow with an ethereal light!")
            print("Your body tingles and shrinks... you've transformed into a mouse!")
            print("The rats seem much larger now, but they regard you as one of their own.")
            player.score += 10  # Reward for discovering the transformation
        else:
            print("You can't wear that.")

    def remove(self, item_name, player):
        """Custom command to remove the azul_oro ring"""
        if item_name in ["ring", "azul_oro", "azul oro"]:
            ring = player.get_item("azul_oro")
            if ring is None:
                print("You're not wearing the ring.")
                return
            
            if ring.state == "unworn":
                print("You're not wearing the ring.")
                return
            
            # Transform back to human
            ring.state = "unworn"
            if "mouse" in player.condition:
                player.condition.remove("mouse")
            
            print("You remove the azul_oro ring from your finger.")
            print("Your body grows back to its normal size. You're human again!")
        else:
            print("You're not wearing that.")

    def look(self, target, player):
        """Look at objects or room features"""
        if target == "" or target is None:
            self.describe_room()
            return

        # Check for special room features
        if target in ["cheese", "rats", "crack", "wall"]:
            if target == "cheese":
                print("Chunks of moldy cheese are scattered across the floor. The rats seem to love it.")
            elif target == "rats":
                print("Dozens of rats scurry about, squeaking and nibbling on cheese. They seem harmless enough.")
            elif target in ["crack", "wall"]:
                print("There's a tiny crack in the eastern wall. It's barely wide enough for a mouse to squeeze through.")
            return
        
        # Check player inventory first
        item = self.get_item_from_inventory(target, player)
        if item is None:
            item = self.get_item_from_object_list(target)
            if item is None:
                print(f"There is nothing like '{target}' to look at.")
                return

        print(item.description)
        if item.state is not None:
            print(f"The {item.name} is {item.state}.")

    def use(self, item_name, player):
        """Use an item"""
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            item = self.get_item_from_object_list(item_name)
        
        if item is None:
            print("You can't use that.")
            return
        
        item.use()

    def get(self, item_name, player):
        """Pick up an item"""
        # Check if player already has it
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        
        item = self.get_item_from_object_list(item_name)
        if item is None:
            print(f"There is no {item_name} here.")
            return
        
        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        # Add to inventory and remove from room
        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name} and add it to your inventory.")

    def drop(self, item_name, player):
        """Drop an item"""
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            print(f"You don't have the {item_name}.")
            return
        
        # Remove from inventory and add to room
        player.inventory.remove(item)
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
        print("  move/go <direction> - Move in a direction (south, east, up)")
        print("  look [object] - Examine something (or just look around)")
        print("  get/take <object> - Pick up an object")
        print("  drop <object> - Drop an object from your inventory")
        print("  wear <item> - Wear an item (like the ring)")
        print("  remove <item> - Remove a worn item")
        print("  use <item> - Use an item")
        print("  inventory - Show your inventory")
        print("  stats - Show your statistics")
        print("  hint - Get a hint")
        print("  help/? - Show this help message")
        print("  quit - Exit the game")

    def show_hint(self):
        print("\nHint: There's a beautiful ring here that might have magical properties.")
        print("Try wearing it and see what happens! The crack in the wall might become passable...")

    def unknown_command(self):
        print("You can't do that here. Try 'help' for a list of commands or 'hint' for a clue.")

    def get_item_from_inventory(self, item_name, player):
        """Get an item from player's inventory by name"""
        for item in player.inventory:
            if item.name.lower() == item_name.lower().replace(" ", "_"):
                return item
        return None

    def get_item_from_object_list(self, item_name):
        """Get an item from room's object list by name"""
        for item in self.objects:
            if item.name.lower() == item_name.lower().replace(" ", "_"):
                return item
        return None