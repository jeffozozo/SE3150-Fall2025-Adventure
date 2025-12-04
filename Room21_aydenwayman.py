from object import Object
from player import Player
import sys  # For exiting the game
import random


class Room:

    GRID_SIZE = 11
    ENTRY_CENTER = (5, 5)
    EXIT_NORTH = (0, 5)
    EXIT_WEST = (5, 0)
    EXIT_SOUTH = (10, 5)
    MILLENIUM_EYE_POS = (8, 8)
    SHUFFLER_POSITIONS = [(2, 2), (9, 3)]
    DUMMY_POSITIONS = [(3, 7), (6, 4), (1, 9), (10, 10), (7, 2), (4,5), (2,8), (8,2), (9,9), (0,10)]
    DUMMY_DATA = {
        "rubber chicken": "A rubber chicken with a missing beak.",
        "cracked snow globe": "A cracked snow globe filled with sand.",
        "faded photograph":"A faded photograph of a llama in a tuxedo.",
        "bent spoon": "A bent spoon engraved with 'Property of Room 21'.",
        "squeaky banana": "A squeaky toy shaped like a banana.",
        "broken compass": "A broken compass that always points up.",
        "sock puppet": "A sock puppet with googly eyes.",
        "mouse hat": "A tiny top hat for a mouse.",
        "mysterious key": "A mysterious key that doesn't fit any lock.",
        "glittery rock": "A glittery rock that smells faintly of cheese."
    }
    objects = []

    def __init__(self):
        self.room_num = 21
        self.description = (
            "You step into a vast, pitch-dark chamber."
            "As the door slams shut, you feel a chill run down your spine."
            "The room is a perfect 11x11 square, and you sense mysterious objects scattered about."
            "The only visible exits are a door to the west,"
            "engraved with 'The Eye of Ra',"
            "a passage to the north,"
            "engraved with 'Error',"
            "and a hushed portal to the south, its lintel bearing a faded Eye symbol."
        )
        self.exits = ["west", "north", "south"]


    # this gets called when the player enters the room.

    def reset_room(self, player=None):
        # Place objects in random positions (allow multiple objects per square)
        self.player_pos = [self.ENTRY_CENTER[0], self.ENTRY_CENTER[1]]
        all_squares = [(r, c) for r in range(self.GRID_SIZE) for c in range(self.GRID_SIZE)]

        # Randomize millenium eye position (not on player start)
        self.millenium_eye_pos = random.choice([sq for sq in all_squares if sq != tuple(self.player_pos)])

        # Randomize shuffler positions (two of them)
        self.shuffler_positions = []
        for _ in range(2):
            self.shuffler_positions.append(random.choice(all_squares))

        # self.dummy_positions = [random.choice(all_squares) for _ in range(6)]

        if player and player.has_item("Millenium Eye"):
            self.millenium_eye_taken = True
            self.has_millenium_eye = True
        else:
            self.millenium_eye_taken = False
            self.has_millenium_eye = False
        # prefer checking player.inventory for ownership, but keep this flag for compatibility
        self.shuffler_triggered = [False, False]

        # Objects in the room are Object instances stored in self.objects (like the example rooms)
        # We'll attach a dynamic .pos attribute to each Object to track its grid location.
        self.objects = []

        # create Millenium Eye as an Object instance
        eye_desc = "A golden, ancient artifact shaped like an eye. It pulses with ominous energy."
        eye_obj = Object("Millenium Eye", eye_desc, True, None, True)
        setattr(eye_obj, 'pos', self.millenium_eye_pos)
        self.objects.append(eye_obj)

        # create dummy Object instances
        for key in self.DUMMY_DATA:
            desc = self.DUMMY_DATA[key]
            dummy = Object(key, desc, True, None, True)
            self.objects.append(dummy)

        # for i, pos in enumerate(self.dummy_positions):
        #     desc = self.DUMMY_DESCRIPTIONS[i % len(self.DUMMY_DESCRIPTIONS)]
        #     dummy = Object(f"dummy_{i+1}", desc, True, None, True)
        #     setattr(dummy, 'pos', pos)
        #     self.objects.append(dummy)

        # Place a mine somewhere safe (not on player start)
        mine_candidates = [sq for sq in all_squares if sq != tuple(self.player_pos)]
        self.mine_pos = random.choice(mine_candidates)

        for i in self.objects:
            if not hasattr(i, 'pos'):
                i.pos = random.choice(all_squares)

    def enter(self, player):
        self.reset_room(player)
        print(self.description)
        self.print_position_and_objects()
        hint_streak = 0
        last_command = None
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]
            other_part = parts[1] if len(parts) > 1 else ""

            if command_base == "hint":
                if last_command == "hint":
                    hint_streak += 1
                else:
                    hint_streak = 1
                if hint_streak == 3:
                    print(f"Super hint: The Millenium Eye can be found at grid square {self.millenium_eye_pos}.")
                else:
                    self.show_hint()
            else:
                hint_streak = 0
                if command_base in ["move", "go"]:
                    next = self.move(other_part, player)
                    if next:
                        return next
                elif command_base == "look":
                    self.print_position_and_objects()
                elif command_base in ["get", "take"]:
                    self.get(other_part, player)
                elif command_base == "inventory":
                    self.show_inventory(player)
                elif command_base == "stats":
                    self.show_stats(player)
                elif command_base == "quit":
                    if self.quit_game(player) == "quit":
                        return "quit"
                elif command_base in ["help", "?"]:
                    self.show_help()
                else:
                    self.unknown_command()
            last_command = command_base

    def print_position_and_objects(self):
        print(f"You are now at position {self.player_pos} in the grid.")
        pos = tuple(self.player_pos)
        # list Object instances that are located at the current square
        objs_here = [o for o in self.objects if getattr(o, 'pos', None) == pos]
        if objs_here:
            print("You see here:")
            for obj in objs_here:
                print(f"  - {obj.name}: {obj.description}")
        else:
            print("There are no objects in this square.")
        # Door descriptions
        if self.player_pos == list(self.EXIT_NORTH):
            print("The north door is here, engraved with 'Error'.")
        if self.player_pos == list(self.EXIT_WEST):
            print("The west door is here, engraved with 'The Eye of Ra'.")
        if self.player_pos == list(self.EXIT_SOUTH):
            print("The south door is here, bearing a faded Eye symbol.")

    # Helper functions
    def describe_room(self):
        print(self.description)
        pos = tuple(self.player_pos)
        # describe object instances at current position
        objs_here = [o for o in self.objects if getattr(o, 'pos', None) == pos]
        for obj in objs_here:
            if obj.name.lower() == "millenium eye" and not self.millenium_eye_taken:
                print("You see the Millenium Eye here: " + obj.description)
            elif getattr(obj, 'name', '').lower().startswith('dummy'):
                print("There is a dummy object here: " + obj.description)
        # describe shuffler presence if applicable
        try:
            if pos in self.shuffler_positions:
                idx = [i for i, p in enumerate(self.shuffler_positions) if p == pos][0]
                if not self.shuffler_triggered[idx]:
                    print("You feel a strange presence here.")
        except Exception:
            pass
        if self.player_pos == list(self.EXIT_NORTH):
            print("The north door is here, engraved with 'Error'.")
        if self.player_pos == list(self.EXIT_WEST):
            print("The west door is here, engraved with 'The Eye of Ra'.")
        if self.player_pos == list(self.EXIT_SOUTH):
            print("The south door is here, bearing a faded Eye symbol.")

    def move(self, direction, player):
        dir_map = {"north": (-1, 0), "n": (-1, 0), "south": (1, 0), "s": (1, 0), "east": (0, 1), "e": (0, 1), "west": (0, -1), "w": (0, -1)}
        if direction not in dir_map:
            print("Invalid direction. Use north, south, east, or west.")
            return None
        # Check for exits BEFORE bounds
        if self.player_pos == list(self.EXIT_WEST) and direction in ["west", "w"]:
            # Exit condition: require Millenium Eye in player's inventory
            if player.has_item("Millenium Eye"):
                print("The Millenium Eye pulses painfully in your skull. The west door swings open!")
                return "west"
            else:
                print("The west door is locked. Only the Millenium Eye can open it.")
                return None
        # South exit behaves like the west door: requires the Millenium Eye
        if self.player_pos == list(self.EXIT_SOUTH) and direction in ["south", "s"]:
            if player.has_item("Millenium Eye"):
                print("The Millenium Eye pulses painfully in your skull. The south door creaks open!")
                return "south"
            else:
                print("The south door is locked. Only the Millenium Eye can open it.")
                return None
        if self.player_pos == list(self.EXIT_NORTH) and direction in ["north", "n"]:
            code = input("The north door is locked. Enter password: ").strip()
            if code == "404":
                print("The door clicks open. You may proceed north.")
                return "north"
            else:
                print("Incorrect password. The door remains shut.")
                return None
        # Normal movement
        new_pos = [self.player_pos[0] + dir_map[direction][0], self.player_pos[1] + dir_map[direction][1]]
        # Check bounds
        if not (0 <= new_pos[0] < self.GRID_SIZE and 0 <= new_pos[1] < self.GRID_SIZE):
            print("You bump into an invisible wall. The room is only 11x11 squares.")
            return None
        self.player_pos = new_pos
        pos = tuple(self.player_pos)
        # Mine check (mine is stored as a positional primitive)
        if pos == getattr(self, 'mine_pos', None):
            print("You step on a mine! It explodes with a deafening blast. Game over.")
            sys.exit(0)
        # Check for shuffler
        if pos in self.shuffler_positions:
            idx = [i for i, p in enumerate(self.shuffler_positions) if p == pos][0]
            if not self.shuffler_triggered[idx]:
                self.shuffle_objects(idx)
        self.print_position_and_objects()
        return None


    def look(self, target, player):
        if not target:
            self.describe_room()
            return
        pos = tuple(self.player_pos)
        if target == "north door":
            print("The north door is engraved with 'Error'. It seems to require a password.")
            return
        if target == "west door":
            print("The west door is engraved with 'The Eye of Ra'. It seems to require a special object.")
            return
        if target == "south door":
            print("The south door bears a faded Eye symbol. It seems to require a special object.")
            return
        
        # inspect objects at current position
        objs_here = [o for o in self.objects if getattr(o, 'pos', None) == pos]
        if objs_here:
            for obj in objs_here:
                if obj.name.lower() == "millenium eye" and not self.millenium_eye_taken:
                    print("You see the Millenium Eye: " + obj.description)
                    return
                elif getattr(obj, 'name', '').lower().startswith('dummy'):
                    print("A dummy object: " + obj.description)
                    return
        # shuffler sight description
        if pos in self.shuffler_positions:
            try:
                idx = [i for i, p in enumerate(self.shuffler_positions) if p == pos][0]
                if not self.shuffler_triggered[idx]:
                    print("A swirling mist makes you dizzy. You can't focus on anything here.")
                    return
            except Exception:
                print("A swirling mist makes you dizzy. You can't focus on anything here.")
                return
        print(f"You look at {target}, but find nothing of interest.")
    

    # you can use this as well. haha get it? use this...
    def use(self, item_name, player):
        if item_name.lower() == "millenium eye" and self.has_millenium_eye:
            print("You try to use the Millenium Eye, but it's already painfully embedded in your skull. You see visions of ancient pharaohs judging your every move.")
            return
        print("You can't use that here.")

    

    def get(self, item_name, player):
        pos = tuple(self.player_pos)
        # check inventory first
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return

        # find object in this square
        obj = None
        for o in list(self.objects):
            if getattr(o, 'pos', None) == pos:
                # match by exact name or by simple keywords
                if o.name.lower() == item_name.lower() or item_name.lower() in o.name.lower() or (item_name.lower() == 'dummy' and o.name.lower().startswith('dummy')):
                    obj = o
                    break

        if obj is None:
            print("There is nothing here to get.")
            return

        if not obj.can_be_gotten:
            print(f"The {obj.name} cannot be taken.")
            return

        # special handling for the Millenium Eye
        if obj.name.lower() == 'millenium eye':
            print("You reach for the Millenium Eye. It leaps into your hand, then burrows into your skull with excruciating pain! You are now the proud (and suffering) owner of the Millenium Eye.")
            self.has_millenium_eye = True
            self.millenium_eye_taken = True

        # add to player inventory and remove from room
        try:
            player.inventory.append(obj)
            self.objects.remove(obj)
            print(f"You take the {obj.name} and add it to your inventory.")
        except Exception:
            # fallback: if append fails, just remove from room and set flags
            if obj.name.lower() == 'millenium eye':
                self.has_millenium_eye = True
                self.millenium_eye_taken = True
            if obj in self.objects:
                self.objects.remove(obj)
        return
    


    def drop(self, item_name, player):
        if item_name.lower() == "millenium eye" and self.has_millenium_eye:
            print("You try to drop the Millenium Eye, but it is permanently fused to your skull. Ouch!")
            return
        print("You don't have that item to drop.")

    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()
        if self.has_millenium_eye:
            print("You have the Millenium Eye painfully embedded in your skull.")

    def quit_game(self, player):
        if input("Are you sure you want to quit? (yes/no) ").lower().startswith('y'):
            print(f"Final Score: {player.score}")
            return "quit"

    def show_help(self):
        print("Available commands: move <direction>, look, get <object>, inventory, stats, quit, help, hint")
        print("Directions: north, south, east, west")
        print("Try to find a way out. The doors have mysterious engravings.")

    def show_hint(self):
        print("Hint: The Millenium Eye is the key to the west door and the south door. The north door needs a password. Some objects may not be what they seem.")

    def unknown_command(self):
        print("You can't do that here. Try something else or type 'help' for options or 'hint' for a clue.")

    # Inventory/object lookup helpers (conform to example rooms)
    def get_item_from_inventory(self, item_name, player):
        for item in player.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None

    def get_item_from_object_list(self, item_name):
        # return an object instance in the room matching the name (only if in the same square)
        pos = tuple(self.player_pos)
        for item in self.objects:
            if getattr(item, 'pos', None) == pos and item.name.lower() == item_name.lower():
                return item
        # fallback: allow matching 'dummy' keyword to any dummy in the square
        if item_name.lower() == 'dummy':
            for item in self.objects:
                if getattr(item, 'pos', None) == pos and item.name.lower().startswith('dummy'):
                    return item
        return None
    def shuffle_objects(self, idx):
        import random
        print("As you step into the swirling mist, the room spins violently! You lose all sense of direction. When the world stops spinning, everything seems to have moved.")
        # Shuffle positions for all Object instances (eye + dummies) and optionally move the mine
        all_positions = [(r, c) for r in range(self.GRID_SIZE) for c in range(self.GRID_SIZE) if (r, c) != tuple(self.player_pos)]
        random.shuffle(all_positions)

        # reassign positions for objects
        for i, obj in enumerate(self.objects):
            # give each object a new position from the shuffled pool
            new_pos = all_positions[i % len(all_positions)]
            setattr(obj, 'pos', new_pos)
            if obj.name.lower() == 'millenium eye':
                self.millenium_eye_pos = new_pos

        # move mine to one of the remaining positions (if any)
        mine_candidates = [p for p in all_positions[len(self.objects):] if p != tuple(self.player_pos)]
        if mine_candidates:
            self.mine_pos = mine_candidates[0]

        # optionally move shufflers (keep them distinct and not on the player)
        shuff_pos_candidates = [p for p in all_positions if p != tuple(self.player_pos) and p not in self.shuffler_positions]
        if len(shuff_pos_candidates) >= len(self.shuffler_positions):
            for i in range(len(self.shuffler_positions)):
                self.shuffler_positions[i] = shuff_pos_candidates[i]

        self.shuffler_triggered[idx] = True
    
