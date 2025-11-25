from player import Player
from Room16_gabriel import Room

# Create a test player
player = Player("TestPlayer", 100, "normal", 16)

# Create your room
room = Room()

# Enter the room
print("Testing Room 16...")
print("=" * 60)
result = room.enter(player)
print("=" * 60)
print(f"Room exited with result: {result}")
print(f"Final player score: {player.score}")
