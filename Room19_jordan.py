from object import Object
from player import Player
import sys

class Mjolnir(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("You currently can't use Mjolnir. Maybe in a future room it will be used against a tough enemy.")

class Room:
    objects = []
    
    def __init__(self):
        self.room_num = 19
        self.description = (
            "You enter the room and you see an older man in a suit with a bright red beret.\n"
            "He spins around dramatically and strikes a heroic pose.\n\n"
            "\"Ay yo! Curtis Sliwa here! Fuhgeddaboudit! "
            "You're lookin' at a genuine New Yawk legend, pal! Back in '79 "
            "this city was goin' straight down the tubes - crime everywhere, muggers and thugs everywhere! "
            "Scumbags runnin' wild like they own the place! Somebody had to do somethin', so I did! \n\n"
            "And let me tell ya somethin' - June 19th, 1992, I'll NEVAH forget it! "
            "John Gotti and his Gambino crime family goons, they don't like me talkin' about 'em on the radio, "
            "so what do they do? They put a HIT on me! Two wiseguys jumped in my cab on the East Side - "
            "I'm sittin' there, and BAM BAM BAM BAM BAM - FIVE TIMES they shot me! Five bullets, pal! "
            "Through the legs! They left me for DEAD in that taxi! "
            "But you know what? I SURVIVED! Curtis Sliwa don't go down that easy! "
            "Takes more than the whole Gambino crime family to stop ME!\n\n"
            "Those mob rats thought they could silence me? NAH! I came back even LOUDAH! "
            "Still wearin' this red beret, still walkin' these streets, still ridin' the subway! "
            "We stand up to these mugs, these gangsters, these FUGAZI tough guys!\n\n"
            "Behind me you see somethin' special - MJOLNIR, the hammer of Thor himself! "
            "But lemme tell ya, not just anyone can wield this baby. You gotta be WORTHY! "
            "You think you got what it takes? Answer my questions, and we'll see if you're ready!\""
        )
        self.exits = ["west", "north", "east"]
        self.quiz_completed = False
        self.quiz_failed = False
        
        mjolnir = Mjolnir(
            "Mjolnir",
            "The legendary hammer of Thor, crackling with divine energy. Its handle is wrapped in leather and inscribed with ancient runes.",
            False,
            None,
            True
        )
        self.objects.append(mjolnir)

    def enter(self, player):
        self.describe_room()
        
        if not self.quiz_completed and not player.has_item("Mjolnir") and not self.quiz_failed:
            self.run_worthiness_quiz(player)
        
        if self.quiz_failed:
            print("\nCurtis stands between you and Mjolnir, arms crossed.")
            print("\"I told ya, you ain't worthy yet! Get outta here and come back when you're ready!\"\n")
        
        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]

            if len(parts) > 1:
                other_part = parts[1]
            else:
                other_part = ""

            if self.quiz_failed:
                if command_base in ["move", "go"]:
                    next_room = self.move(other_part)
                    if next_room != None:
                        self.quiz_failed = False
                        return next_room
                elif command_base in ["help", "?"]:
                    print("Curtis won't let you do anything. You can only 'move west' to leave.")
                elif command_base == "quit":
                    if self.quit_game(player) == "quit":
                        sys.exit(0)
                else:
                    print("Curtis blocks you. \"I said GET OUTTA HERE! Try 'move west' to leave!\"")
                continue

            if command_base in ["move", "go"]:
                next_room = self.move(other_part)
                if next_room != None:
                    return next_room
            
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
                
            elif command_base == "talk" and "curtis" in other_part:
                self.talk_to_curtis(player)

            elif command_base == "quit":
                if self.quit_game(player) == "quit":
                    sys.exit(0)

            elif command_base in ["help", "?"]:
                self.show_help()
            
            elif command_base == "hint":
                self.show_hint()
            else:
                self.unknown_command()

    def run_worthiness_quiz(self, player):
        print("\nCurtis clears his throat and adjusts his red beret.")
        print("\"Alright pal, listen up! You want Mjolnir? You gotta prove you're WORTHY!")
        print("I'm gonna ask you three questions about what it means to be a true hero.")
        print("Answer honestly - I'll know if you're lyin'!\"\n")
        
        correct_answers = 0
        
        print("QUESTION 1:")
        print("\"You're walkin' down the street and some punk is harassing an old lady. Whaddya do?\"")
        print("A) Mind your own business - not your problem")
        print("B) Step up and say 'HEY! I'M WALKIN' HERE!' and protect her")
        print("C) Call 911 and hope they show up eventually")
        
        answer1 = input("\nYour answer (A, B, or C): ").upper().strip()
        
        if answer1 == "B":
            print("\n\"EXACTLY! That's what I'm talkin' about! You don't let some mook push people around!")
            print("You stand up, you speak up! That's real New Yawk right there!\"")
            correct_answers += 1
        else:
            print("\n\"Eh, not the answer I was lookin' for, but let's keep goin'...\"")
        
        print("\n\nQUESTION 2:")
        print("\"You get shot FIVE TIMES by the mob. What do you do?\"")
        print("A) Give up and retire to Florida")
        print("B) Get revenge on everyone who wronged you")
        print("C) Survive, recover, and come back STRONGAH to keep fightin' for what's right")
        
        answer2 = input("\nYour answer (A, B, or C): ").upper().strip()
        
        if answer2 == "C":
            print("\n\"YES! THAT'S IT! You don't let the bad guys win! You come back LOUDAH!")
            print("That's EXACTLY what I did! You're gettin' it now!\"")
            correct_answers += 1
        else:
            print("\n\"Hmm, I dunno about that one, pal. But alright, one more question...\"")
        
        print("\n\nQUESTION 3:")
        print("\"Who do you fight for?\"")
        print("A) Yourself and your own glory")
        print("B) The little guy - the working people who can't defend themselves")
        print("C) Whoever pays you the most")
        
        answer3 = input("\nYour answer (A, B, or C): ").upper().strip()
        
        if answer3 == "B":
            print("\n\"BINGO! The PEOPLE! The real New Yawkas! The ones who ride the subway,")
            print("who work hard every day, who deserve to feel SAFE! That's who we protect!\"")
            correct_answers += 1
        else:
            print("\n\"Nah, that ain't it, friend...\"")
        
        print("\n" + "="*60)
        print("Curtis strokes his chin thoughtfully...")
        print("="*60 + "\n")
        
        is_worthy = "worthy" in player.condition
        required_correct = 2 if is_worthy else 3
        
        if correct_answers >= required_correct:
            if is_worthy:
                print("\"You know what? I heard about you savin' that squirrel! That's the kinda thing a TRUE hero does!")
                print("And you got", correct_answers, "outta 3 right. That's good enough for me!\"")
            else:
                print("\"PERFECT! You got ALL THREE right!\"")
            
            print("You got the heart of a HERO! You understand what it means to be WORTHY!")
            print("You stand up for the little guy, you don't back down, and you fight for what's RIGHT!")
            print("\nMjolnir is YOURS, my friend! Use it wisely! Use it to protect the innocent!")
            print("Now go out there and show these FUGAZI villains what real justice looks like!\"")
            print("\nCurtis gestures toward Mjolnir with pride.")
            print("The hammer begins to glow with divine energy - you are worthy!\n")
            
            mjolnir = self.get_item_from_object_list("Mjolnir")
            if mjolnir:
                player.inventory.append(mjolnir)
                self.objects.remove(mjolnir)
                print("Curtis hands you Mjolnir! Lightning crackles as you grasp the legendary hammer!")
                print("The power of Thor flows through you!\n")
                player.score += 100
            
            self.quiz_completed = True
            player.score += 50
            
            print("You can go west, north, and east from here.")
        else:
            if is_worthy:
                print("\"Ehhhh, I dunno pal. You only got", correct_answers, "outta 3 right.")
                print("Even though you saved that squirrel, you still need at least 2 outta 3!\"")
            else:
                print("\"Ehhhh, I dunno pal. You only got", correct_answers, "outta 3 right.")
                print("You need to get ALL THREE questions right to prove you're worthy!")
                print("Maybe if you did somethin' heroic first - like savin' an innocent creature - I'd cut you some slack!")
            
            print("That hammer's for TRUE HEROES who understand what it means to be worthy!")
            print("Come back when you've learned what it really means to stand up for the little guy!")
            print("Now get outta here - I got streets to walk! This whole thing's FUGAZI without the right person!\"\n")
            print("Curtis shakes his head and turns away. The hammer remains out of reach.")
            print("Curtis now stands blocking your path to Mjolnir. You'll have to leave and try again.\n")
            
            self.quiz_failed = True

    def talk_to_curtis(self, player):
        if self.quiz_completed:
            print("\"You already proved yourself, pal! Now get out there and use that hammer for GOOD!\"")
        elif player.has_item("Mjolnir"):
            print("\"You got the hammer! Now use it to protect the innocent, capisce?\"")
        else:
            print("\"You wanna try the worthiness test again? Get outta here first and come back!\"")

    def describe_room(self):
        print(self.description)
        if self.objects:
            for obj in self.objects:
                if obj.visible:
                    print(f"There is {obj.name} here, resting on a stone pedestal.")

    def move(self, direction):
        if direction in ["west", "w"]:
            print("You head back through the door to the west.")
            return "west"
        elif direction in ["north", "n"]:
            print("You push open a heavy stone door to the north.")
            print("You hear an ominous buzzing sound growing louder...")
            return "north"
        elif direction in ["east", "e"]:
            print("You head east through a narrow passage.")
            return "east"
        else:
            print("You can't go that way.")
            return None

    def look(self, target, player):
        if target == None or target == "":
            self.describe_room()
            return
        
        if "curtis" in target or "sliwa" in target:
            print("Curtis Sliwa stands before you in his signature red beret and jacket.")
            print("He looks ready to take on any threat to the city. A true New York legend.")
            return
        
        item = self.get_item_from_inventory(target, player)
        if item == None:
            item = self.get_item_from_object_list(target)
            if item == None:
                print(f"There is nothing like {target} to look at.")
                return
        
        if target == item.name.lower().strip():
            print(item.description)
            if item.state != None:
                print(f"The {item.name} is {item.state}")
            return

    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            item = self.get_item_from_object_list(item_name)
        
        if item == None:
            print("You can't use that.")
            return
        
        item.use()

    def get(self, item_name, player):
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return
        
        item = self.get_item_from_object_list(item_name)
        if item == None:
            print(f"{item_name} is not here.")
            return
        
        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken yet. You must prove yourself worthy first!")
            print("Curtis shouts: \"HEY! I'M WALKIN' HERE! You can't just TAKE Mjolnir! You gotta earn it, pal!\"")
            return

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You grasp {item.name}! Lightning crackles around you as the hammer recognizes your worthiness!")
        print("Curtis cheers: \"THAT'S what I'm talkin' about! Go get 'em, hero!\"")
        player.score += 100
        return

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            print(f"You don't have the {item_name}.")
            return
        
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
        print("Available commands: move, go, look, get, take, drop, use, talk, inventory, stats, quit, help, hint")

    def show_hint(self):
        if not self.quiz_completed:
            print("Curtis seems to be testing your worthiness. Answer his questions honestly and think like a true hero!")
        else:
            print("You've proven yourself worthy! Take Mjolnir and continue your adventure.")

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