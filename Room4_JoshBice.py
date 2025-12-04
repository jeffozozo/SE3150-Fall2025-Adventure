from object import Object
from player import Player


class LightningSkull(Object):
    def __init__(self):
        super().__init__(
            name="skull",
            description="A darkened skull humming with faint blue electricity.",
            can_be_gotten=True,
            state=None,
            visible=True
        )

    def use(self):
        print("You don't really know what this does.")

class Room:

    def __init__(self):
        self.room_num = 4

        self.description = (
            "A vast chamber of dense vegetation spreads around you. Vines hang like curtains.\n"
            "In the center is a clearing dominated by a titanic tree whose blue leaves pulse\n"
            "with flickering arcs of light.\n"
            "Before it, you see a skeleton with a black sword. It seems to be attacking a squirrel.\n"
            "Somehow you seem to know that the Skeleton is named DJ, and the squirrel is named Jeff.\n"
        )

        self.skeleton_defeated = False

        self.objects = []

        self.exits = ["up", "west"]

    def enter(self, player):

        if "vine_snapped" in player.condition:
            print("You drop from above and crash painfully into the vegetation!")
            player.health -= 2
            print("(-2 health)")
        else:
            print("You slide down a thick vine into the glowing forest chamber.")
            print("A foot from the ground, the vine snaps!")
            print("You fall the last few feet, stumbling a little as you hit the ground")
            print("Somehow you know you won't be going back that way...")
            player.condition.append("vine_snapped")

        self.describe_room()

        while True:
            raw = input("> ").lower().strip()
            parts = raw.split(" ", 1)
            command = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            if command in ["move", "go"]:
                next = self.move(arg, player)
                if next is not None:
                    return next

            elif command == "look":
                self.look(arg, player)

            elif command in ["get", "take"]:
                self.get(arg, player)

            elif command in ["drop", "put"]:
                self.drop(arg, player)

            elif command == "use":
                self.use(arg, player)

            elif command == "inventory":
                player.show_inventory()

            elif command == "stats":
                player.print_stats()

            elif command in ["help", "?"]:
                self.show_help()

            elif command == "hint":
                self.show_hint()

            elif command == "quit":
                if self.quit_game(player) == "quit":
                    return "quit"

            else:
                self.unknown_command()


    def describe_room(self):
        print(self.description)

        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

        print("Exits: up, west")


    def move(self, direction, player):

        if direction == "up":
            if "vine_snapped" in player.condition:
                print("There is no vine left to climb. The path upward is gone.")
                return None
            return "up"

        if direction == "west":
            print("A black metal door looms here, leaking heavy fog.")
            print("You push through the swirling haze...")
            if "lock_tree" not in player.condition:
                player.condition.append("lock_tree")
            return "west"

        print("You can't go that way.")
        return None


    def look(self, target, player):
        target = target.lower().strip()

        if target == "" or target is None:
            self.describe_room()
            return

        if target in ["tree", "squirrel", "jeff", "dj", "skeleton"]:
            self.trigger_fight_scene(player)
            return

        if target in ["door", "west door"]:
            print("A tall black metal door. Heavy fog pours from its seams.")
            return

        item = self.get_item_from_inventory(target, player)
        if not item:
            item = self.get_item_from_object_list(target)

        if item:
            print(item.description)
            return

        print(f"There is nothing like '{target}' to look at.")


    def trigger_fight_scene(self, player):

        if "worthy" not in player.condition and "not_worthy" not in player.condition:
            player.condition.append("not_worthy")

        if not self.skeleton_defeated:
            print(
                "You step closer. Jeff the squirrel struggles desperately.\n"
                "DJ the skeleton raises a bony hand for a finishing blow.\n"
                "Do you PUNCH the skeleton or SLIDE away unnoticed?"
            )
            choice = input("> ").lower().strip()

            if "punch" in choice:
                print("You strike DJ with all your strength!")
                print("The skeleton explodes apart and his bones begin to turn to dust.")
                print("Only a single skull remains, blackened and pulsing with lightning.")

                self.skeleton_defeated = True

                player.health -= 3
                print("The punch hurt your hand a little (-3 health)")

                if "not_worthy" in player.condition:
                    player.condition.remove("not_worthy")
                if "worthy" not in player.condition:
                    player.condition.append("worthy")

                skull = LightningSkull()
                self.objects.append(skull)

                print("\nThe colossal tree stirs. Wooden eyes blink open.")
                print("\"You have saved the children of the un'it t'est forest. You are worthy.\"")

            else:
                print("You quietly retreat, pretending you saw nothing.")

        else:
            print("The remains of DJ lie scattered. The giant tree watches peacefully.")


    def get(self, item_name, player):
        name = item_name.lower().strip()

        if player.has_item(name):
            print(f"You already have the {name}.")
            return

        item = self.get_item_from_object_list(name)
        if not item:
            print(f"There is no {name} here.")
            return

        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You pick up the {item.name}.")

    def drop(self, item_name, player):
        name = item_name.lower().strip()
        item = self.get_item_from_inventory(name, player)

        if not item:
            print(f"You don't have a {name}.")
            return

        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")

    def use(self, item_name, player):
        name = item_name.lower().strip()
        item = self.get_item_from_inventory(name, player)
        if not item:
            item = self.get_item_from_object_list(name)
        if not item:
            print("You can't use that.")
            return
        item.use()


    def show_help(self):
        print("Commands: move/go, look, get/take, drop, use, inventory, stats, quit, hint, help")

    def show_hint(self):
        print("Jeff may need your help… the tree is watching.")

    def quit_game(self, player):
        if input("Are you sure you want to quit? (y/n) ").lower().startswith("y"):
            print(f"Final Score: {player.score}")
            return "quit"

    def unknown_command(self):
        print("You can't do that here.")

    def get_item_from_inventory(self, name, player):
        for item in player.inventory:
            if item.name.lower() == name:
                return item
        return None

    def get_item_from_object_list(self, name):
        for item in self.objects:
            if item.name.lower() == name:
                return item
        return None
