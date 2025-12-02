from object import Object
from player import Player

# Custom object: a sharp dagger you can pick up
class Dagger(Object):
    def __init__(self):
        super().__init__(
            name="Dagger",
            description="A sharp, blood-stained dagger. Perfect for cutting... something.",
            can_be_gotten=True,
            state="clean",
            visible=True
        )

    def use(self):
        print("You wave the dagger around. It looks dangerous, but nothing happens here by itself.")
        print("Maybe you need to use it ON something...")

# The main room
class Room:
    def __init__(self):
        self.room_num = 8
        self.description = (
            "You step into an enormous, dark chamber — the infamous Double Dungeon.\n"
            "Massive stone statues with glowing red eyes line the walls, staring at you.\n"
            "In the center stands a terrifying altar carved with strange runes.\n"
            "A huge red portal gate looms behind it, sealed shut.\n"
            "You feel an overwhelming pressure... something powerful sleeps here.\n"
            "Obvious exits: up (a ladder back to safety), west, east."
        )

        # Items in the room
        self.objects = []
        self.objects.append(Dagger())

        # Fixed altar (cannot be taken)
        self.altar = Object(
            name="Altar",
            description="An ancient stone altar covered in dried blood and glowing runes.",
            can_be_gotten=False,
            state="inactive",
            visible=True
        )
        self.objects.append(self.altar)

        # Allowed exits (must match map.txt exactly!)
        self.exits = ["up", "west", "east"]

    def enter(self, player: Player):
        print("\033[91m" + "WARNING: You have entered the Double Dungeon! Proceed with caution!" + "\033[0m")
        self.describe_room()

        while True:
            command = input("\n> ").lower().strip()
            parts = command.split(" ", 1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ["go", "move"]:
                direction = arg if arg else input("Which direction? ").lower()
                result = self.move(direction)
                if result:
                    return result

            elif cmd == "look":
                self.look(arg, player)

            elif cmd in ["get", "take"]:
                self.get(arg, player)

            elif cmd in ["drop"]:
                self.drop(arg, player)

            elif cmd == "use":
                self.use_item(arg, player)

            elif cmd in ["cut", "offer", "sacrifice"]:
                self.offer_blood(player)

            elif cmd == "inventory":
                player.show_inventory()

            elif cmd == "stats":
                player.print_stats()

            elif cmd in ["help", "?"]:
                self.show_help()

            elif cmd == "hint":
                self.show_hint(player)

            elif cmd == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"

            else:
                print("I don't understand that. Try 'help' or 'hint'.")

    # Helper functions below
    def describe_room(self):
        print(self.description)
        for obj in self.objects:
            if obj.visible:
                print(f"There is a {obj.name.lower()} here.")

    def move(self, direction):
        dir = direction.lower()
        if dir in ["up", "u", "ladder"]:
            print("You climb back up the ladder to safety... coward.")
            return "up"
        elif dir in ["west", "w"]:
            print("You walk cautiously to the west.")
            return "west"
        elif dir in ["east", "e"]:
            print("You head east into the shadows.")
            return "east"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if not target:
            self.describe_room()
            return

        # Special looks
        if target in ["altar", "stone altar"]:
            print(self.altar.description)
            if self.altar.state == "active":
                print("The runes are glowing bright red! The red gate behind it is now OPEN!")
            return

        if target in ["statues", "eyes", "red eyes"]:
            print("The statues stare at you silently. You feel judged.")
            return

        if target in ["gate", "portal", "red gate", "red portal"]:
            if self.altar.state == "active":
                print("The red gate is wide open! You can now escape... or step into power.")
            else:
                print("The red gate is sealed. It looks like it requires... a blood sacrifice.")
            return

        # Look at items in room or inventory
        item = self.find_item(target) or player.get_item(target)
        if item:
            print(item.description)
            if item.state:
                print(f"It is currently {item.state}.")
        else:
            print("There's nothing like that to look at.")

    def get(self, item_name, player):
        item = self.find_item(item_name)
        if not item:
            print("There's no such thing here.")
            return
        if not item.can_be_gotten:
            print(f"You can't take the {item.name}.")
            return
        if player.has_item(item.name):
            print("You already have it!")
            return

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name}.")

    def drop(self, item_name, player):
        item = player.get_item(item_name)
        if not item:
            print("You don't have that.")
            return
        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")

    def use_item(self, arg, player):
        parts = arg.lower().split(" on ")
        if len(parts) == 2:
            item_name, target = parts
            if target in ["altar", "stone altar"] and "dagger" in item_name:
                self.offer_blood(player)
                return

        # Normal use
        item = player.get_item(arg) or self.find_item(arg)
        if item:
            item.use()
        else:
            print("You can't use that.")

    def offer_blood(self, player):
        dagger = player.get_item("dagger")
        if not dagger:
            print("You need something sharp to cut yourself with...")
            return

        print("\nYou press the dagger to your palm and slice deep...")
        print("Blood drips onto the altar...")
        print("The runes ignite in crimson light!")
        print("THE RED GATE OPENS WITH A BOOM!")
        print("You feel a dark power surging through you...")
        player.health -= 30
        player.score += 100
        player.condition.append("awakened")
        self.altar.state = "active"
        self.description += "\nThe red gate is now wide open!"

    def show_help(self):
        print("Commands: go <direction>, look <thing>, get <item>, drop <item>, use <item>, ")
        print("          cut hand, offer blood, inventory, stats, hint, help, quit")
        print("Visible exits: up, west, east")

    def show_hint(self, player):
        if player.has_item("dagger"):
            print("Hint: In Solo Leveling, only blood opens the true gate... Try cutting your hand!")
        else:
            print("Hint: You need something sharp. Look around!")

    def find_item(self, name):
        for item in self.objects:
            if name.lower() in item.name.lower():
                return item
        return None