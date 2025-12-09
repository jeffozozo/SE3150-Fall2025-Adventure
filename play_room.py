import os
import sys
import importlib
from Adventure import load_rooms
from player import Player


try:
    room_num = int(sys.argv[1])
except (IndexError, ValueError):
    print("Usage: python play_room <num> for example: python play_room 16\n")
    sys.exit()


# load the room
rooms = load_rooms()



# setup the player
player = Player(
    name="test",
    health=100,
    condition="healthy",
    current_room=room_num
)   


for r in rooms:
    print("room: " + str(r.room_num) + "\n")
    print(r.description)
    print("\n\n------")



#direction = rooms[room_num].enter(player)

#print("Room "+str(room_num)+" exited with direction: " + direction + "\n")





