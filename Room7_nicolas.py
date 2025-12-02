from object import Object
from player import Player

class RustyCoin(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        if self.state == "rusty":
            print("You rub the coin between your fingers. Some rust flakes away revealing a faint symbol.")
            self.state = "clean"
        else:
            print("You flip the coin. It spins in the air and lands with a soft *clink*.")

class Room:

    def __init__(self):
        self.room_num = 7
        self.description = (
            "You step into a narrow stone chamber. The air is cool and carries a faint metallic scent.\n"
            "Moisture drips from cracks in the ceiling, creating tiny echoing splashes.\n"
            "A small square opening in the floor reveals a ladder leading down into a dim blue glow.\n"
            "Something glints near a loose stone by the wall."
        )
        coin = RustyCoin(
            "coin",
            "A small, rusty coin engraved with a swirling pattern. It feels old and oddly heavy.",
            True,
            "rusty",
            True
        )
        self.objects = [coin]
        self.exits = ["down"]

    def enter(self, player):
        print("A cold draft follows you as you enter the cramped stone chamber.")
        self.describe_room()

        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]
            other_part = parts[1] if len(parts) > 1 else ""

            if command_base in ["move", "go"]:
                result = self.move(other_part)
                if result:
                    return result
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
                self.show_hint()
            else:
                self.unknown_command()

    def describe_room(self):
        print(self.description)
        for obj in self.objects:
            if obj.visible:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["down", "d"]:
            print("You grip the cold rungs of the ladder and begin your descent...")
            return "down"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if not target:
            self.describe_room()
            return
        if target == "ladder":
            print("A narrow ladder leads downward to a faintly glowing space.")
            return
        item = self.get_item_from_inventory(target, player)
        if item is None:
            item = self.get_item_from_object_list(target)
            if item is None:
                print(f"There is nothing like '{target}' here to look at.")
                return
        print(item.description)
        if item.state:
            print(f"The {item.name} is currently {item.state}.")

    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            item = self.get_item_from_object_list(item_name)
        if item is None:
            print("You can't use that.")
            return
        item.use()

    def get(self, item_name, player):
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        item = self.get_item_from_object_list(item_name)
        if item is None:
            print(f"{item_name} is not here.")
            return
        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return
        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You pick up the {item.name}.")

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            print(f"You don't have the {item_name}.")
            return
        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")

    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()

    def quit_game(self, player):
        confirm = input("Are you sure? (y/n) ").lower()
        if confirm.startswith("y"):
            print(f"Final Score: {player.score}")
            return "quit"

    def show_help(self):
        print("Commands: move/go, look, get/take, drop, inventory, stats, quit, help, hint")

    def show_hint(self):
        print("The ladder seems to be the only path forward. That coin… it might matter later.")

    def unknown_command(self):
        print("You can't do that here.")

    def get_item_from_inventory(self, item_name, player):
        return player.get_item(item_name)

    def get_item_from_object_list(self, item_name):
        for item in self.objects:
            if item.name.lower() == item_name.lower():
                return item
        return None
