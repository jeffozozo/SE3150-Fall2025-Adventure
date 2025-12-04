from object import Object
from player import Player
import sys
import random
import os
import time

class Room:

    objects = []

    def __init__(self):
        self.room_num = 0
        self.description = ("The room illuminates with bright neon lights, there are several zombie like figures playing games.\nA smoke fills the room with a foul smell, there is a sign on the wall 'Welcome to Dungeon Casino'.\nThere are 2 games not occupied: 'BloodJack' and 'ScoreSlots'.")
        self.exits = ["south","north", "west"]


    # this gets called when the player enters the room.
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
            elif command_base == "play":
                self.play(other_part, player)
            else:
                self.unknown_command()

    # Helper functions
    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                print(f"There is a {obj.name} here.")

    def move(self, direction):
        if direction in ["south", "s"]:
            print("You take the south exit out of the casino.")
            return "south"
        elif direction in ["north", "n"]:
            print("A janitor closet lays to the north, you pass through the door.")
            return "north"
        elif direction in ["west", "w"]:
            print("You head west into a doorway that says 'Double Dungeon'")
            return "west"
        else:
            print("You can't go that way.")
            return None


    def look(self, target, player):
        if(target == None or target == "" ):
            self.describe_room()
            return

        if target == "bloodjack":
            print("There is a game table called 'Blood Jack'")
            return

        if target == "scoreslots":
            print("There is a slot machine titled 'Score Slots'")
            return

        item = self.get_item_from_inventory(target,player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None:
                print("There is nothing like " + target + " to look at.")
                return


    # you can use this as well. haha get it? use this...
    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)

        if(item == None):
            print("you can't use that.")
            return

        item.use()


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
        print("Available commands: move, go, look, get, take, drop, inventory, stats, quit, help, play")

    def show_hint(self):
        print("Try playing the games 'BloodJack' or 'ScoreSlots', the command 'play <game_name>' will begin a game")

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

    def play(self, game, player):
        if game.lower() == "bloodjack" :
            BloodJack(player)
            return
        elif game.lower() == "scoreslots" :
            ScoreSlots(player)
            return
        else:
            print("Not an available game, try 'BloodJack' or 'ScoreSlots'")
            return


'''
WARNING - The code below was 'borrowed' 🤡 from an open source project with cli games,
then heavily vibe coded to match how i imagined it. The code can be confusing at times and
reviewing it would be tedious.

Enter at your own risk,
Good luck!
'''

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def BloodJack(player):

    def clear_screen():
        os.system('clear' if os.name != 'nt' else 'cls')

    clear_screen()
    print(f"{RED}{BOLD}\n=== BLOOD JACK ==={RESET}")
    print(f"{YELLOW}Welcome to Blood Jack! You wager your health to play.{RESET}")
    print(f"{CYAN}Commands: wager, deal, exit{RESET}")
    print(f"{WHITE}Use 'wager' to set your bet (minimum 5), or 'deal' to play with minimum bet.{RESET}")

    current_wager = 5
    player_hand = []
    dealer_hand = []
    in_game = False

    def calculate_hand_value(hand):
        value = 0
        aces = 0
        for card in hand:
            if card in ['J', 'Q', 'K']:
                value += 10
            elif card == 'A':
                aces += 1
                value += 11
            else:
                value += card

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def deal_card():
        cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
        return random.choice(cards)

    def card_to_string(card):
        if card == 10:
            return "10"
        else:
            return str(card).rjust(2)

    def display_card(card, hidden=False):
        if hidden:
            return [
                f"{MAGENTA}┌─────┐{RESET}",
                f"{MAGENTA}│ ??? │{RESET}",
                f"{MAGENTA}│ ??? │{RESET}",
                f"{MAGENTA}│ ??? │{RESET}",
                f"{MAGENTA}└─────┘{RESET}"
            ]

        card_str = card_to_string(card)
        color = YELLOW if card in ['A', 'J', 'Q', 'K'] else WHITE
        return [
            f"{color}┌─────┐{RESET}",
            f"{color}│ {card_str}  │{RESET}",
            f"{color}│     │{RESET}",
            f"{color}│  {card_str} │{RESET}",
            f"{color}└─────┘{RESET}"
        ]

    def display_hands(show_dealer_full=False):
        player_value = calculate_hand_value(player_hand)
        value_color = GREEN if player_value == 21 else RED if player_value > 21 else CYAN
        print(f"\n{BLUE}Your hand {value_color}(Value: {player_value}){RESET}:")

        card_displays = [display_card(card) for card in player_hand]
        for line_idx in range(5):
            print("  " + " ".join(card[line_idx] for card in card_displays))

        if show_dealer_full:
            dealer_value = calculate_hand_value(dealer_hand)
            value_color = GREEN if dealer_value == 21 else RED if dealer_value > 21 else CYAN
            print(f"\n{BLUE}Dealer hand {value_color}(Value: {dealer_value}){RESET}:")
            card_displays = [display_card(card) for card in dealer_hand]
        else:
            print(f"\n{BLUE}Dealer hand:{RESET}")
            card_displays = [display_card(dealer_hand[0])] + [display_card(None, hidden=True) for _ in dealer_hand[1:]]

        for line_idx in range(5):
            print("  " + " ".join(card[line_idx] for card in card_displays))

    while True:
        if in_game:
            command = input(f"\n{CYAN}[hit/stand] > {RESET}").lower().strip()
        else:
            command = input(f"\n{CYAN}[wager/deal/exit] > {RESET}").lower().strip()

        if command == "exit":
            clear_screen()
            print(f"{YELLOW}You leave the Blood Jack table.{RESET}")
            return

        elif command == "wager" and not in_game:
            clear_screen()
            print(f"{RED}{BOLD}\n=== BLOOD JACK ==={RESET}")
            print(f"{GREEN}Your current health: {player.health}{RESET}")
            wager_input = input(f"{YELLOW}How much health do you want to wager? (or 'all' to bet everything, press Enter for minimum bet of 5): {RESET}").strip().lower()

            if wager_input == "":
                current_wager = 5
                if current_wager > player.health:
                    print(f"{RED}You don't have enough health for the minimum bet! (Current health: {player.health}){RESET}")
                    continue
                print(f"{CYAN}Wager set to {current_wager} health. Type 'deal' to start!{RESET}")
            elif wager_input == "all":
                if player.health <= 0:
                    print(f"{RED}You have no health to wager!{RESET}")
                    continue
                current_wager = player.health
                print(f"{MAGENTA}{BOLD}You've bet it all! Wagering {current_wager} health. Type 'deal' to start!{RESET}")
            else:
                try:
                    current_wager = int(wager_input)
                    if current_wager < 5:
                        print(f"{RED}Minimum bet is 5 health!{RESET}")
                        continue
                    if current_wager > player.health:
                        print(f"{RED}You don't have that much health! (Current health: {player.health}){RESET}")
                        continue
                    print(f"{CYAN}Wager set to {current_wager} health. Type 'deal' to start!{RESET}")
                except ValueError:
                    print(f"{RED}Invalid wager amount!{RESET}")
                    continue

        elif command == "deal" and not in_game:
            if player.health < current_wager:
                print(f"{RED}You don't have enough health for this wager! (Current: {player.health}, Wager: {current_wager}){RESET}")
                continue

            clear_screen()
            print(f"{RED}{BOLD}\n=== BLOOD JACK ==={RESET}")
            print(f"{YELLOW}Wager: {current_wager} health{RESET}")
            player.health -= current_wager
            print(f"{GREEN}Remaining health: {player.health}{RESET}")
            player_hand = [deal_card(), deal_card()]
            dealer_hand = [deal_card(), deal_card()]
            in_game = True

            display_hands(False)

            if calculate_hand_value(player_hand) == 21:
                print(f"{GREEN}{BOLD}BLACKJACK! You win!{RESET}")
                winnings = current_wager * 2
                player.health += winnings
                print(f"{GREEN}You won {winnings} health! Current health: {player.health}{RESET}")
                in_game = False
                current_wager = 5

        elif command == "hit" and in_game:
            clear_screen()
            print(f"{RED}{BOLD}\n=== BLOOD JACK ==={RESET}")
            print(f"{YELLOW}Wager: {current_wager} health{RESET}")
            print(f"{GREEN}Current health: {player.health}{RESET}")
            player_hand.append(deal_card())
            print(f"{CYAN}You hit!{RESET}")
            display_hands(False)

            player_value = calculate_hand_value(player_hand)
            if player_value > 21:
                print(f"{RED}{BOLD}BUST! You went over 21 with {player_value}.{RESET}")
                print(f"{RED}You lost {current_wager} health. Current health: {player.health}{RESET}")
                in_game = False
                current_wager = 5
            elif player_value == 21:
                print(f"{GREEN}You have 21! Standing automatically.{RESET}")
                command = "stand"

        if command == "stand" and in_game:
            clear_screen()
            print(f"{RED}{BOLD}\n=== BLOOD JACK ==={RESET}")
            print(f"{YELLOW}Wager: {current_wager} health{RESET}")
            print(f"{GREEN}Current health: {player.health}{RESET}")

            print(f"\n{BLUE}Dealer reveals their hand...{RESET}")
            display_hands(True)

            while calculate_hand_value(dealer_hand) < 17:
                input(f"\n{CYAN}Press Enter to see dealer hit...{RESET}")
                dealer_hand.append(deal_card())
                clear_screen()
                print(f"{RED}{BOLD}\n=== BLOOD JACK ==={RESET}")
                print(f"{YELLOW}Wager: {current_wager} health{RESET}")
                print(f"{GREEN}Current health: {player.health}{RESET}")
                print(f"\n{BLUE}Dealer hits!{RESET}")
                display_hands(True)

            dealer_value = calculate_hand_value(dealer_hand)
            player_value = calculate_hand_value(player_hand)

            print(f"\n{BOLD}Final - Your hand: {player_value}, Dealer hand: {dealer_value}{RESET}")

            if dealer_value > 21:
                print(f"{GREEN}{BOLD}Dealer busts! You win!{RESET}")
                winnings = current_wager * 2
                player.health += winnings
                print(f"{GREEN}You won {winnings} health! Current health: {player.health}{RESET}")
            elif dealer_value > player_value:
                print(f"{RED}{BOLD}Dealer wins!{RESET}")
                print(f"{RED}You lost {current_wager} health. Current health: {player.health}{RESET}")
            elif player_value > dealer_value:
                print(f"{GREEN}{BOLD}You win!{RESET}")
                winnings = current_wager * 2
                player.health += winnings
                print(f"{GREEN}You won {winnings} health! Current health: {player.health}{RESET}")
            else:
                print(f"{YELLOW}It's a tie! Your wager is returned.{RESET}")
                player.health += current_wager

            in_game = False
            current_wager = 5

        elif command not in ["wager", "deal", "hit", "stand", "exit"]:
            if in_game:
                print(f"{RED}Invalid command. Use: hit, stand{RESET}")
            else:
                print(f"{RED}Invalid command. Use: wager, deal, exit{RESET}")

def ScoreSlots(player):

    def clear_screen():
        os.system('clear' if os.name != 'nt' else 'cls')

    clear_screen()
    print(f"{MAGENTA}{BOLD}\n=== SCORE SLOTS ==={RESET}")
    print(f"{YELLOW}Welcome to Score Slots! You wager your score to play.{RESET}")
    print(f"{CYAN}Commands: wager, spin, exit{RESET}")
    print(f"{WHITE}Symbols:{RESET}")
    print(f"  {BLUE}O{RESET} = small hit")
    print(f"  {GREEN}W{RESET} = big hit")
    print(f"  {RED}L{RESET} = lose points")
    print(f"  {YELLOW}7{RESET} = jackpot")
    print(f"{CYAN}TIP: Press Enter to keep spinning with the same wager!{RESET}")

    current_wager = 1
    ready_to_spin = False
    is_spinning = False

    def colorize_symbol(symbol):
        if symbol == 'X':
            return f"{WHITE}{BOLD}{symbol}{RESET}"
        elif symbol == 'O':
            return f"{BLUE}{BOLD}{symbol}{RESET}"
        elif symbol == 'W':
            return f"{GREEN}{BOLD}{symbol}{RESET}"
        elif symbol == '7':
            return f"{YELLOW}{BOLD}{symbol}{RESET}"
        elif symbol == 'L':
            return f"{RED}{BOLD}{symbol}{RESET}"
        return symbol

    def display_slot_machine(reels):
        print(f"\n{CYAN}┌─────┬─────┬─────┬─────┬─────┐{RESET}")
        for row in range(3):
            symbols = [colorize_symbol(reels[col][row]) for col in range(5)]
            line = f"{CYAN}│{RESET}  " + f"  {CYAN}│{RESET}  ".join(symbols) + f"  {CYAN}│{RESET}"
            print(line)
            if row < 2:
                print(f"{CYAN}├─────┼─────┼─────┼─────┼─────┤{RESET}")
        print(f"{CYAN}└─────┴─────┴─────┴─────┴─────┘{RESET}")

    def spin_reels():
        weighted_symbols = ['O'] * 4 + ['W'] * 3 + ['7'] * 2 + ['L'] * 1

        reels = []
        for col in range(5):
            reel = [random.choice(weighted_symbols) for _ in range(3)]
            reels.append(reel)
        return reels

    def animate_spin(final_reels):
        weighted_symbols = ['O'] * 9 + ['W'] * 5 + ['7'] * 2 + ['L'] * 4

        for i in range(8):
            clear_screen()
            temp_reels = []
            for col in range(5):
                reel = [random.choice(weighted_symbols) for _ in range(3)]
                temp_reels.append(reel)

            print(f"{MAGENTA}{BOLD}\n=== SCORE SLOTS ==={RESET}")
            print(f"\n{BOLD}Spinning...{RESET}")
            display_slot_machine(temp_reels)
            time.sleep(0.08)

        for i in range(3):
            clear_screen()
            temp_reels = []
            for col in range(5):
                reel = [random.choice(weighted_symbols) for _ in range(3)]
                temp_reels.append(reel)

            print(f"{MAGENTA}{BOLD}\n=== SCORE SLOTS ==={RESET}")
            print(f"\n{BOLD}Spinning...{RESET}")
            display_slot_machine(temp_reels)
            time.sleep(0.15)

        clear_screen()
        print(f"{MAGENTA}{BOLD}\n=== SCORE SLOTS ==={RESET}")
        print(f"\n{BOLD}Final Result:{RESET}")
        display_slot_machine(final_reels)

    def get_symbol_color(symbol):
        """Get the color code for a symbol"""
        if symbol == 'X':
            return WHITE
        elif symbol == 'O':
            return BLUE
        elif symbol == 'W':
            return GREEN
        elif symbol == '7':
            return YELLOW
        elif symbol == 'L':
            return RED
        return WHITE

    def draw_winning_line(reels, positions, symbol):
        """Draw the slot machine with the winning line highlighted"""
        color = get_symbol_color(symbol)
        print(f"\n{CYAN}┌─────┬─────┬─────┬─────┬─────┐{RESET}")

        for row in range(3):
            symbols_line = f"{CYAN}│{RESET}"
            for col in range(5):
                sym = colorize_symbol(reels[col][row])
                if (col, row) in positions:
                    symbols_line += f"  {color}{BOLD}[{reels[col][row]}]{RESET}  {CYAN}│{RESET}"
                else:
                    symbols_line += f"  {sym}  {CYAN}│{RESET}"
            print(symbols_line)
            if row < 2:
                print(f"{CYAN}├─────┼─────┼─────┼─────┼─────┤{RESET}")
        print(f"{CYAN}└─────┴─────┴─────┴─────┴─────┘{RESET}")

    def _display_line(reels, payout_type, amount_str):
        """Helper function to display a single line"""
        if 'Row 1' in payout_type:
            line = f"{CYAN}|{RESET}  " + "--".join([colorize_symbol(reels[col][0]) for col in range(5)]) + f"  {CYAN}|{RESET}"
            print(f"{line}  Row 1: {amount_str}")
        elif 'Row 2' in payout_type:
            line = f"{CYAN}|{RESET}  " + "--".join([colorize_symbol(reels[col][1]) for col in range(5)]) + f"  {CYAN}|{RESET}"
            print(f"{line}  Row 2: {amount_str}")
        elif 'Row 3' in payout_type:
            line = f"{CYAN}|{RESET}  " + "--".join([colorize_symbol(reels[col][2]) for col in range(5)]) + f"  {CYAN}|{RESET}"
            print(f"{line}  Row 3: {amount_str}")
        elif 'Diagonal \\' in payout_type:
            symbols = [reels[0][0], reels[1][0], reels[2][1], reels[3][2], reels[4][2]]
            line = f"{CYAN}\\{RESET}  " + "--".join([colorize_symbol(s) for s in symbols]) + f"  {CYAN}\\{RESET}"
            print(f"{line}  Diagonal \\: {amount_str}")
        elif 'Diagonal /' in payout_type:
            symbols = [reels[4][0], reels[3][0], reels[2][1], reels[1][2], reels[0][2]]
            line = f"{CYAN}/{RESET}  " + "--".join([colorize_symbol(s) for s in symbols]) + f"  {CYAN}/{RESET}"
            print(f"{line}  Diagonal /: {amount_str}")
        elif 'V Pattern' in payout_type:
            symbols = [reels[0][0], reels[1][1], reels[2][2], reels[3][1], reels[4][0]]
            line = f"{CYAN}V{RESET}  " + "--".join([colorize_symbol(s) for s in symbols]) + f"  {CYAN}V{RESET}"
            print(f"{line}  V Pattern: {amount_str}")
        elif 'Inverted V' in payout_type:
            symbols = [reels[0][2], reels[1][1], reels[2][0], reels[3][1], reels[4][2]]
            line = f"{CYAN}^{RESET}  " + "--".join([colorize_symbol(s) for s in symbols]) + f"  {CYAN}^{RESET}"
            print(f"{line}  Inverted V: {amount_str}")
        elif 'MEGA JACKPOT' in payout_type or 'MEGA LOSS' in payout_type or 'ALL' in payout_type:
            symbol = reels[0][0]
            print(f"{colorize_symbol(symbol)} {colorize_symbol(symbol)} {colorize_symbol(symbol)} {colorize_symbol(symbol)} {colorize_symbol(symbol)}  (ALL 15!)  {amount_str}")

    def display_text_based_lines(reels, payouts):
        if not payouts:
            return

        winning_payouts = [(payout_type, amount) for payout_type, amount in payouts if amount > 0]
        losing_payouts = [(payout_type, amount) for payout_type, amount in payouts if amount < 0]

        if winning_payouts:
            print(f"\n{GREEN}{BOLD}Winning Lines:{RESET}")
            for payout_type, amount in winning_payouts:
                amount_str = f"{GREEN}+{amount} points{RESET}"
                _display_line(reels, payout_type, amount_str)

        if losing_payouts:
            print(f"\n{RED}{BOLD}L's in the chat:{RESET}")
            for payout_type, amount in losing_payouts:
                if payout_type == 'L':
                    print(f"{RED}L = {amount} points{RESET}")
                elif payout_type == 'Double L':
                    print(f"{RED}Double L = {amount} points{RESET}")
                elif payout_type == 'Triple L':
                    print(f"{RED}Triple L = {amount} points{RESET}")
                elif payout_type == 'Quadruple L':
                    print(f"{RED}Quadruple L = {amount} points{RESET}")
                elif payout_type == 'BIG L':
                    print(f"{RED}BIG L = {amount} points (LOSE EVERYTHING!){RESET}")
                else:
                    amount_str = f"{RED}{amount} points{RESET}"
                    _display_line(reels, payout_type, amount_str)

    def calculate_payout(reels, wager, current_score):
        payouts = []
        winning_lines = []

        all_symbols = [reels[col][row] for col in range(5) for row in range(3)]
        if len(set(all_symbols)) == 1:
            symbol = all_symbols[0]
            positions = [(col, row) for col in range(5) for row in range(3)]
            if symbol == '7':
                payouts.append(('MEGA JACKPOT - ALL 7s!!!', wager * 10000))
                winning_lines.append((positions, symbol))
            elif symbol == 'W':
                payouts.append(('MEGA JACKPOT - ALL Ws!!!', wager * 1000))
                winning_lines.append((positions, symbol))
            elif symbol == 'O':
                payouts.append(('MEGA JACKPOT - ALL Os!!!', wager * 500))
                winning_lines.append((positions, symbol))
            return payouts, winning_lines

        for row in range(3):
            symbols = [reels[col][row] for col in range(5)]
            max_consecutive_ls = 0
            current_consecutive = 0

            for symbol in symbols:
                if symbol == 'L':
                    current_consecutive += 1
                    max_consecutive_ls = max(max_consecutive_ls, current_consecutive)
                else:
                    current_consecutive = 0

            if max_consecutive_ls >= 5:
                payouts.append(('BIG L', -(current_score + wager)))
            elif max_consecutive_ls == 4:
                payouts.append(('Quadruple L', -wager * 10))
            elif max_consecutive_ls == 3:
                payouts.append(('Triple L', -wager * 5))
            elif max_consecutive_ls == 2:
                payouts.append(('Double L', int(-wager * 2.5)))
            elif max_consecutive_ls == 1:
                payouts.append(('L', -wager))

            symbol = symbols[0]
            if symbol == 'L':
                continue

            if symbols[0] == symbols[1] == symbols[2] == symbols[3] == symbols[4]:
                positions = [(col, row) for col in range(5)]
                if symbol == '7':
                    payouts.append((f'Row {row+1}: Five 7s', wager * 500))
                    winning_lines.append((positions, symbol))
                elif symbol == 'W':
                    payouts.append((f'Row {row+1}: Five Ws', wager * 100))
                    winning_lines.append((positions, symbol))
                elif symbol == 'O':
                    payouts.append((f'Row {row+1}: Five Os', wager * 25))
                    winning_lines.append((positions, symbol))
            elif symbols[0] == symbols[1] == symbols[2] == symbols[3]:
                positions = [(col, row) for col in range(4)]
                if symbol == '7':
                    payouts.append((f'Row {row+1}: Four 7s', wager * 250))
                    winning_lines.append((positions, symbol))
                elif symbol == 'W':
                    payouts.append((f'Row {row+1}: Four Ws', wager * 40))
                    winning_lines.append((positions, symbol))
                elif symbol == 'O':
                    payouts.append((f'Row {row+1}: Four Os', wager * 12))
                    winning_lines.append((positions, symbol))
            elif symbols[0] == symbols[1] == symbols[2]:
                positions = [(col, row) for col in range(3)]
                if symbol == '7':
                    payouts.append((f'Row {row+1}: Three 7s', wager * 125))
                    winning_lines.append((positions, symbol))
                elif symbol == 'W':
                    payouts.append((f'Row {row+1}: Three Ws', wager * 20))
                    winning_lines.append((positions, symbol))
                elif symbol == 'O':
                    payouts.append((f'Row {row+1}: Three Os', wager * 5))
                    winning_lines.append((positions, symbol))

        diag_lr = [reels[0][0], reels[1][0], reels[2][1], reels[3][2], reels[4][2]]
        if diag_lr[0] == diag_lr[1] == diag_lr[2] == diag_lr[3] == diag_lr[4] and diag_lr[0] != 'L':
            if diag_lr[0] == '7':
                payouts.append(('Diagonal \\: Five 7s', wager * 500))
            elif diag_lr[0] == 'W':
                payouts.append(('Diagonal \\: Five Ws', wager * 100))
            elif diag_lr[0] == 'O':
                payouts.append(('Diagonal \\: Five Os', wager * 25))

        diag_rl = [reels[4][0], reels[3][0], reels[2][1], reels[1][2], reels[0][2]]
        if diag_rl[0] == diag_rl[1] == diag_rl[2] == diag_rl[3] == diag_rl[4] and diag_rl[0] != 'L':
            if diag_rl[0] == '7':
                payouts.append(('Diagonal /: Five 7s', wager * 500))
            elif diag_rl[0] == 'W':
                payouts.append(('Diagonal /: Five Ws', wager * 100))
            elif diag_rl[0] == 'O':
                payouts.append(('Diagonal /: Five Os', wager * 25))

        v_shape = [reels[0][0], reels[1][1], reels[2][2], reels[3][1], reels[4][0]]
        if v_shape[0] == v_shape[1] == v_shape[2] == v_shape[3] == v_shape[4] and v_shape[0] != 'L':
            if v_shape[0] == '7':
                payouts.append(('V Pattern: Five 7s', wager * 500))
            elif v_shape[0] == 'W':
                payouts.append(('V Pattern: Five Ws', wager * 100))
            elif v_shape[0] == 'O':
                payouts.append(('V Pattern: Five Os', wager * 25))

        inv_v_shape = [reels[0][2], reels[1][1], reels[2][0], reels[3][1], reels[4][2]]
        if inv_v_shape[0] == inv_v_shape[1] == inv_v_shape[2] == inv_v_shape[3] == inv_v_shape[4] and inv_v_shape[0] != 'L':
            if inv_v_shape[0] == '7':
                payouts.append(('Inverted V: Five 7s', wager * 500))
            elif inv_v_shape[0] == 'W':
                payouts.append(('Inverted V: Five Ws', wager * 100))
            elif inv_v_shape[0] == 'O':
                payouts.append(('Inverted V: Five Os', wager * 25))

        return payouts, winning_lines

    while True:
        command = input(f"\n{CYAN}> {RESET}").lower().strip()

        if command == "exit":
            clear_screen()
            print(f"{YELLOW}You leave the Score Slots machine.{RESET}")
            return

        elif command == "wager":
            clear_screen()
            print(f"{MAGENTA}{BOLD}\n=== SCORE SLOTS ==={RESET}")
            print(f"{GREEN}Your current score: {player.score}{RESET}")

            if player.score <= 0:
                print(f"{RED}You have no score to wager! You need at least 1 point to play.{RESET}")
                continue

            wager_input = input(f"{YELLOW}How much do you want to wager? (1, 2, 3, 5, 10, or 'all', press Enter for minimum bet of 1): {RESET}").strip().lower()

            if wager_input == "":
                current_wager = 1
                if current_wager > player.score:
                    print(f"{RED}You don't have enough score for the minimum bet! (Current score: {player.score}){RESET}")
                    continue
                print(f"{CYAN}Wagering minimum bet of {current_wager} point.{RESET}")
            elif wager_input == "all":
                if player.score <= 0:
                    print(f"{RED}You have no score to wager!{RESET}")
                    continue
                current_wager = player.score
                print(f"{MAGENTA}{BOLD}You've bet it all! Wagering {current_wager} points.{RESET}")
            else:
                try:
                    current_wager = int(wager_input)
                    if current_wager not in [1, 2, 3, 5, 10]:
                        print(f"{RED}You can only bet 1, 2, 3, 5, 10, or 'all'!{RESET}")
                        continue
                    if current_wager > player.score:
                        print(f"{RED}You don't have that much score! (Current score: {player.score}){RESET}")
                        continue
                except ValueError:
                    print(f"{RED}Invalid wager amount!{RESET}")
                    continue

            ready_to_spin = True
            print(f"{CYAN}Wager set to {current_wager} points. Use 'spin' to play!{RESET}")

        elif command == "spin" or command == "":
            if is_spinning:
                continue

            if player.score <= 0:
                print(f"{RED}You have no score to wager! You need at least 1 point to play.{RESET}")
                continue

            if not ready_to_spin and current_wager == 0:
                if player.score < 1:
                    print(f"{RED}You don't have enough score for the minimum bet!{RESET}")
                    continue
                current_wager = 1
                ready_to_spin = True

            is_spinning = True

            clear_screen()
            print(f"{MAGENTA}{BOLD}\n=== SCORE SLOTS ==={RESET}")

            if not ready_to_spin:
                print(f"{CYAN}Auto-wagering minimum bet of 1 point.{RESET}")
                current_wager = 1
                ready_to_spin = True

            print(f"{YELLOW}Wager: {current_wager} points{RESET}")

            was_all_in = (current_wager == player.score)
            player.score -= current_wager

            print(f"{GREEN}Current score: {player.score}{RESET}")

            reels = spin_reels()
            animate_spin(reels)

            payouts, winning_lines = calculate_payout(reels, current_wager, player.score)

            display_text_based_lines(reels, payouts)

            if payouts:
                total_winnings = sum(p[1] for p in payouts)
                player.score += total_winnings

                if player.score < 0:
                    player.score = 0

                if total_winnings > 0:
                    print(f"\n{GREEN}{BOLD}Total winnings: +{total_winnings} points{RESET}")
                    print(f"{GREEN}Current score: {player.score}{RESET}")
                elif total_winnings < 0:
                    print(f"\n{RED}{BOLD}Total loss: {total_winnings} points{RESET}")
                    if player.score == 0:
                        print(f"{RED}Score bottomed out at 0!{RESET}")
                    else:
                        print(f"{YELLOW}Current score: {player.score}{RESET}")
                else:
                    print(f"\n{YELLOW}Results cancel out to 0{RESET}")
                    print(f"{YELLOW}Current score: {player.score}{RESET}")
            else:
                print(f"\n{RED}No winning combinations. You lose!{RESET}")
                if was_all_in:
                    print(f"{RED}{BOLD}You bet it all and lost everything!{RESET}")
                print(f"{YELLOW}Current score: {player.score}{RESET}")

            ready_to_spin = True
            is_spinning = False

        elif command not in ["wager", "spin", "exit"]:
            print(f"{RED}Invalid command. Use: wager, spin, exit{RESET}")
