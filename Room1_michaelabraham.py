from object import Object
from player import Player
import sys  # For exiting the game
import mikesminigame


# Electric Guitar object - when used, allows player to transcend to the upper room
class ElectricGuitar(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # The guitar's use is handled specially in the Room's use method
        # This method is called but the actual logic is in Room.use()
        pass


# Shred Knowledge object - required to use the guitar
class ShredKnowledge(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # Shred knowledge is consumed when using the guitar
        pass


# Mystic Bubbler object - when used, gives Shred Knowledge
class MysticBubbler(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # The bubbler's use is handled specially in the Room's use method
        pass


class Room:

    def __init__(self):
        self.objects = []  # Instance variable to prevent test pollution
        self.room_num = 1
        self.bubbler_learned = False  # Track if player learned how to use the bubbler from Doug
        self.bubbler_attempted = False  # Track if player has tried to use the bubbler
        self.description = (
            "You find yourself in a dimly lit chamber with stone walls covered in ancient runes.\n"
            "The air hums with a strange energy, and you notice three distinct pathways:\n"
            "A heavy wooden door to the east, a narrow passageway to the north, and above you,\n"
            "a mysterious opening in the ceiling that seems to shimmer with ethereal light.\n"
            "In the center of the room, propped against a stone pedestal, stands an electric guitar\n"
            "that seems to pulse with otherworldly power. Its strings glimmer faintly, as if calling\n"
            "out to be played.\n"
            "In the corner, Doug the a mystical creature lounges like he's been here for centuries, occasionally\n"
            "glancing your way with a knowing look.\n"
            "A low, cushioned couch slumps against the wall beside a glass vessel humming softly\n"
            "with trapped herbal vapors. The mist inside twists into fleeting shapes, as if the room\n"
            "itself is exhaling.\n"
        )
        # Add the electric guitar to the room (fixed in place)
        guitar = ElectricGuitar(
            "Electric Guitar", 
            "A sleek electric guitar with a polished black finish. The strings shimmer with an otherworldly glow, "
            "and strange symbols are etched along the neck. It seems to resonate with the very essence of the dungeon. "
            "The guitar appears to be magically anchored to the pedestal and cannot be moved.",
            False,  # cannot be picked up - fixed in place
            "ready",  # state
            True  # visible
        )
        self.objects.append(guitar)
        
        # Add the Mystic Bubbler to the room
        bubbler = MysticBubbler(
            "Mystic Bubbler",
            "An arcane water-pipe of glass and ancient design. Herbal vapors swirl within, creating patterns\n"
            "that seem to shift between worlds. The vessel hums with a low, resonant frequency, as if it\n"
            "contains knowledge older than the dungeon itself.",
            False,  # cannot be picked up - fixed in place
            "active",  # state
            True  # visible
        )
        self.objects.append(bubbler)
        
        # Declare the exits as specified in map.txt
        self.exits = ["east", "north", "up"]

    def enter(self, player):
        # Step 1 - Print the room description
        self.describe_room()

        # Step 2 - Command loop
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            # Handle commands
            if command_base in ["move", "go"]:
                next = self.move(other_part, player)
                if next != None:
                    return next
            
            elif command_base == "use":
                next = self.use(other_part, player)
                if next != None:
                    return next

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

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                if obj.visible:
                    print(f"There is a {obj.name} here.")

    def move(self, direction, player):
        if direction in ["east", "e"]:
            print("You push open the heavy wooden door and step through to the east.")
            return "east"
        elif direction in ["north", "n"]:
            # Check if player has the key to unlock the north door
            if not player.has_item("key_16_west"):
                print("The narrow passageway to the north is locked. You need a key to open it.")
                print("You notice a keyhole that looks like it might match a key from room 16.")
                return None
            print("You unlock the door with the key and head through the narrow passageway to the north.")
            return "north"
        elif direction in ["up", "u", "ceiling"]:
            print("You look up at the shimmering opening, but you can't quite reach it from here.")
            print("Perhaps there's another way to get up there...")
            return None
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if target == None or target == "":
            self.describe_room()
            return

        # Special handling for room features
        if target in ["rune", "runes", "wall", "walls"]:
            print("The runes carved into the walls seem to pulse with energy. They appear to be ancient symbols "
                  "of power, though their exact meaning eludes you.")
            return
        
        if target in ["pedestal", "stone pedestal"]:
            print("A simple stone pedestal stands in the center of the room. It appears to be where the guitar "
                  "was meant to rest.")
            return

        if target in ["door", "east door", "wooden door"]:
            print("A heavy wooden door with iron reinforcements. It looks sturdy and well-maintained.")
            return

        if target in ["passage", "passageway", "north passage", "north door", "door north"]:
            print("A narrow passageway leads north, but it's locked. You notice a keyhole that")
            print("looks like it might match a key from room 16.")
            return

        if target in ["opening", "ceiling", "up", "shimmer"]:
            print("An opening in the ceiling shimmers with ethereal light. It seems to be some kind of portal "
                  "or magical gateway, but it's too high to reach normally.")
            return

        if target in ["doug", "dog"]:
            print("Doug lounges in the corner like he's been here for centuries. He has a relaxed, ancient\n"
                  "presence—wise but slightly absurd. He occasionally gives you a knowing glance, as if\n"
                  "he understands more about this place than anyone should.")
            return

        if target in ["couch", "cushioned couch"]:
            print("A low, cushioned couch slumps against the wall beside the Mystic Bubbler. It looks\n"
                  "comfortable but worn, as if it has been here for a very long time. The fabric seems to\n"
                  "hold the memory of countless moments of rest and contemplation.")
            return

        # Check if the object is in the room or in the player's inventory
        item = self.get_item_from_inventory(target, player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None:
                print("There is nothing like " + target + " to look at.")
                return

        if target.lower() in item.name.lower():
            print(item.description)
            if item.state != None:
                print(f"The {item.name} is {item.state}.")
            return

        print("Looking at " + target + " reveals nothing.")
        return

    def use(self, item_name, player):
        # Special handling for Doug (not an object, but can be "used" to pet or ask for wisdom)
        if item_name.lower() in ["doug", "dog"]:
            # If player has attempted the bubbler, offer two options
            if self.bubbler_attempted:
                print("\nWhat would you like to do?")
                print("1. Pet Doug")
                print("2. Ask for wisdom with the ancient peace pipe")
                choice = input("Enter 1 or 2: ").strip()
                
                if choice == "1":
                    # Just normal petting - no tutorial
                    print("You pet Doug gently. He wags his tail")
                    print("Doug seems content with your company.")
                elif choice == "2":
                    print("\nYou ask Doug for wisdom with the ancient peace pipe.")
                    print("Doug opens one eye, gives you a knowing look, and slowly gets up.")
                    print("He stumbles over to the Mystic Bubbler with purpose.")
                    print("Doug takes a massive hit from the mystic pipe, the vapors swirling around him")
                    print("as he inhales deeply. He holds it, and picks up the guitar")
                    print("He sheads the cleanest, nastiest riff you've ever heard.")
                    print("The notes echo through the room, each one perfectly placed.")
                    print("A single tear falls from your eye.")
                    print("For a moment, you feel something awaken within you—something ancient and powerful.")
                    print("\nDoug exhales the a beutiful swearing smoke cloud and it fills the room as he lets the last note ring")
                    print("\nWhen the smoke clears he's in his corner taking nap")
                    print("\nYou feel like you've learned something profound")
                    print("quite sure what it is yet.")
                    print("But you definitely understand how to use the Mystic Bubbler now!")
                    self.bubbler_learned = True
                else:
                    print("Invalid choice.")
            else:
                # Before attempting bubbler, just offer to pet
                response = input("Do you want to pet Doug? (yes/no): ").lower().strip()
                if response.startswith('y'):
                    print("You pet Doug gently. He wags his tail and gives you a knowing nod.")
                    print("Doug seems chill with you")
                else:
                    print("SMH")
            return None
        
        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            item = self.get_item_from_object_list(item_name)
        
        if item == None:
            print("You can't use that.")
            return None

        # Special handling for the Mystic Bubbler
        if item.name.lower() == "mystic bubbler" or item_name.lower() in ["bubbler", "mystic bubbler", "vessel", "mystic pipe"]:
            # Check if player has learned how to use it from Doug
            if not self.bubbler_learned:
                self.bubbler_attempted = True  # Mark that player has tried to use it
                print("\nYou approach the Mystic Bubbler and try to figure out how to use it.")
                print("You examine the glass vessel humming with herbal vapors, but the vapors just swirl mysteriously.")
                print("You can't quite figure out the right way to interact with this arcane device.")
                print("Maybe you should look around for someone who might know how to use it...")
                return None
            
            # Check if player already has Shred Knowledge
            if player.has_item("Shred Knowledge"):
                print("You already possess Shred Knowledge. The vapors swirl but offer nothing new.")
                return None
            
            print("\nYou approach the Mystic Bubbler. The herbal vapors swirl faster as you draw near.")
            print("Following Doug's example, you take a deep hit from the mystic pipe.")
            print("The vapors coil into your lungs, then into your mind.")
            print("Runes flicker at the edge of your vision.")
            print("Suddenly, you understand—riffs older than the dungeon itself flood your consciousness.")
            print("You now know how to shred.")
            
            # Create and add Shred Knowledge to inventory
            shred_knowledge = ShredKnowledge(
                "Shred Knowledge",
                "Ancient shredding lore, riffs older than the dungeon itself. Gained from the Mystic Bubbler's vapors.",
                True,  # can be picked up (it's in inventory)
                "active",  # state
                True  # visible
            )
            player.inventory.append(shred_knowledge)
            print("Shred Knowledge has been added to your inventory.")
            print("You feel lighter, calmer, and oddly energized.")
            return None

        # Special handling for the electric guitar
        if item.name.lower() == "electric guitar" or item_name.lower() in ["guitar", "electric guitar"]:
            # Check if player has Shred Knowledge
            shred_knowledge = self.get_item_from_inventory("Shred Knowledge", player)
            if shred_knowledge == None:
                print("\nYou pick up the electric guitar, but as your fingers touch the strings, nothing happens.")
                print("The guitar seems to require some kind of knowledge or understanding to play.")
                print("Perhaps you need to learn how to shred first...")
                return None
            
            print("\nYou pick up the electric guitar. As your fingers touch the strings, they begin to vibrate ")
            print("with an otherworldly resonance.")
            print("The Shred Knowledge flows through you, and you feel ready to play.")
            print("The runes on the walls start to glow brighter, responding to the guitar's power.")
            print("The room hums. Reality feels thin.")
            
            response = input("Do you want to shred? (yes/no): ").lower().strip()
            
            if response.startswith('y'):
                print("\nYou strike a chord, and the sound that emerges is unlike anything you've ever heard.")
                print("The notes seem to tear through reality itself. The runes pulse with light,")
                print("and you feel yourself being pulled into a musical dimension...")
                print("\n" + "="*50)
                print("Time to shred! Let's see if you can transcend!")
                print("="*50 + "\n")
                
                # Call the guitar hero minigame
                result = mikesminigame.main()
                
                # Check if player transcended in the minigame
                if result == "transcend":
                    print("\n" + "="*50)
                    print("The music fades, and you return to the room.")
                    print("The Shred Knowledge has been consumed in the act of shredding—")
                    print("a one-time attunement, now spent.")
                    print("The runes blaze with light, and you feel your body being pulled upward.")
                    print("The guitar's power lifts you through the shimmering opening in the ceiling.")
                    print("You have transcended!")
                    print("="*50 + "\n")
                    
                    # Remove Shred Knowledge from inventory (it was consumed)
                    player.inventory.remove(shred_knowledge)
                    
                    # Return "up" to exit the room upward (to room 6)
                    return "up"
                else:
                    # Player didn't transcend, just finished the game normally
                    print("\n" + "="*50)
                    print("The music fades, and you return to the room.")
                    print("You played well, just not cosmically well yet.")
                    print("The room calms down. The runes return to their normal glow.")
                    print("The guitar invites you to try again later.")
                    print("="*50 + "\n")
                    return None
            else:
                print("You decide not to play. The guitar's power fades, and the runes return to their normal glow.")
                return None
        
        # For other items, call their use method
        item.use()
        return None

    def get(self, item_name, player):
        # Check if the player already has the item in their inventory
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        
        item = self.get_item_from_object_list(item_name)
        if item == None:
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
        if item == None:
            print(f"You don't have the {item_name}.")
            return
        
        # Remove the item from the inventory and put it in the object list
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
            player.print_stats()
            return "quit"
        return None

    def show_help(self):
        print("Available commands:")
        print("  move/go <direction> - Move in a direction (east, north, up)")
        print("  look [item] - Look at the room or a specific item")
        print("  get/take <item> - Pick up an item")
        print("  drop <item> - Drop an item from your inventory")
        print("  use <item> - Use an item (you can also use Doug to pet him)")
        print("  inventory - Show your inventory")
        print("  stats - Show your statistics")
        print("  hint - Get a hint about this room")
        print("  help/? - Show this help message")
        print("  quit - Quit the game")
        print("\nVisible exits: east, north, up")

    def show_hint(self):
        print("The electric guitar in the center of the room seems to have special properties.")
        print("Try using it—you might discover a way to reach that shimmering opening above you.")
        print("But first, you might need to gain some knowledge...")
        print("Someone in the room seems to know how to use that mystical vessel.")
    

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

