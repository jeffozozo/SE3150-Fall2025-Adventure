from player import Player
from object import Object
import sys

class Room:
    def __init__(self):
        self.room_num = 22
        self.description = (
            "You step into a small, silent antechamber. The air tastes of finality.\n"
            "A glyph on the floor pulses once and the exits wink out of existence."
        )
        self.exits = []

    def enter(self, player):
        print(self.description)
        # Give the player a choice to end the game or continue
        while True:
            choice = input("The glyph pulses beneath your feet. End the game now? (yes/no) ").strip().lower()
            if choice in ("y", "yes"):
                print("A hidden mechanism triggers beneath your feet. Everything goes black.")
                print("You reached the end. Game over.")
                sys.exit(0)
            elif choice in ("n", "no"):
                print("You step back from the glyph. The chamber settles; you leave to the north.")
                # return 'north' so the main engine can move you back according to the map
                return "north"
            else:
                print("Please answer 'yes' or 'no'.")

    # Minimal stubs to satisfy engine expectations
    def show_inventory(self, player):
        player.show_inventory()

    def quit_game(self, player):
        if input("Are you sure you want to quit? (yes/no) ").lower().startswith('y'):
            print(f"Final Score: {player.score}")
            return "quit"
