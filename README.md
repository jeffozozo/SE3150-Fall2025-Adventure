# CS3150-Adventure

This is the repository for the template code to setup the Utah Tech CS-3150 crowd sourced adventure game. The intention of this project is that each student in class will build a ROOM that is part of a whole adventure game. The rooms are linked together by a MAP (really a bi-directional connected graph of rooms) that the PLAYER will traverse during their adventure. 

Both the instructor and the students will need to follow some precise specifications in order for their rooms to work. This is what needs to happen:

1. The instructor determines how many students will participate.
2. The instructor will run the mapgen.py tool and enter the number of students.
3. The map.txt will start at room 1 for student assignments and will specify what 'exits' the student's rooms need to support.
4. The instructor will create an instance of the map.txt (called student_map.txt) that contains student names assigned to rooms. The instructor will edit this file by hand.
5. The instructor will produce Room0_instructorName.py as the introductory room. It doesn't matter how the PLAYER gets out of that room, but they should end up in Room1_<student_name>.py next.
6. The instructor will edit map.txt to contain a Room0 reference with the correct connector to Room1.
7. The instructor will also create a 'end game' room like so Room<num_students+1>_instructor_name.py
8. The instructor will edit map.txt to make it so that at least one room in the map points to the end_game room.
9. A sample (very simple) completed map.txt is shown here for reference - assuming 4 students would participate here is an example generated map with the instructor additions:

Room:0  
down,1  

Room:1  
south,2  
east,3  

Room:2  
north,1  

Room:3  
west,1  
north,4  

Room:4  
south,3  
up,5  

Room:5  
end,5  

 10. As mentioned above, once this map.txt is complete, the instructor will make a copy of this map.txt file (call it student_map.txt) and put a single student name along each room number.
 11. The students will need to create the rooms associated with their name. They will look at the connections to their room and make sure that their descriptions match those connections and that the player can GO or MOVE in those directions. Here are the requirements for the rooms:
 12. Rooms are written as stand alone python programs. The file name is important and must follow the specification: Room<number>_<student_name>.py
 14. The rooms must support the following commands:
     
+ go, move <direction> - allows the player to move to the next Room. Players can only move in the directions allowed by the specification for the room. 
+ look <item> - provides a description of the item. the item can be in the player's inventory or it can be in an object array in the room. If no <item> is given, the room description is printed.
+ get, take <item> - allows the player to pick up the item and put it into their inventory. The room must create an object of type Object for the player to pick it up. (See Objects) below.
+ drop <item> - allows the player to remove an item from their inventory and place it in the room's list of Objects.
+ inventory - prints out the items in the PLAYERs inventory.
+ stats - prints out the PLAYERs statistics
+ help,? - prints out the list of commands
+ hint - prints out a room-specific hint that will help the player get through the puzzle in the room
+ quit - asks "Are you sure? (y/n) and if y prints out the player stats and ends the game.

15. Rooms can also support any custom commands that will support solving the puzzle. For example, a room could have a fountain in it, and the PLAYER could say "drink fountain" and the room would respond with a result. If the puzzle is hard, giving a hint is a good idea to keep the players from rage quitting.
16. OBJECTS - PLAYERS have an inventory and rooms have an list of Objects. Rooms must support dropping items so they MUST support an object list in some way. It doesn't matter what the room's object list is called, only that when a player drops something it goes out of the inventory and into the room's object list. If the player wants to get the object again, they should be able to do so. You could also make it so that the object would get destroyed if they did something crazy with it. Like there could be a pit in the room and the PLAYER could say "throw lamp in pit" and the result could be that the lamp is now gone.
    + All game Objects inherit from a base Object class that has a pure virtual function called "use"
    + You create an object by subclassing Object and implementing the use function.
    + The lamp is the example of how to implement an object. Take a look at the lamp defined in Room0.
17. The students should try to write the room descriptions so that they indicate the exits available in the room.
18.  When the room is complete the room should return the direction that the PLAYER has chosen or that is the result of the solution to the puzzle. For example if the PLAYER chooses "north" the room should return "north"

In this repository there are 3 files:
+ mapgen.py
+ Adventure.py
+ Room0_jeff.py (as an example of a room)

Once all of the rooms have been created, when they are placed in the same directory as Adventure.py, you just run Adventure.py and the rooms will load and you can play. The rooms have to correctly return the exits they are supposed to return as describe in map.txt or the game will crash. Here are some other considerations:

+ Look at the definition of Objects in object.py. You can use the attributes of the object to do things like make objects that are too big to get or that are attached to something. You can have puzzles that change those settings and then allow changes in the way that the players interact with the objects.
+ Objects will travel with the player from room to room. You can coordinate with other Room Authors to get an object in some room, and then use it in another.
+ rooms can change player stats. Rooms that do cool things should give the player a boost to their score. If players do dumb things you can hurt them by removing health. You might be generous and make an Object that the player could use to restore their health. You can also change the Player's condition - they could be any condition that you want. This can also pass from room to room and could affect the way play happens. For example, in one room, a person could fall in a river and be wet and cold. If they go to another room that is a wintery scene, say by an Ice Dragon, the person could freeze to death if they are cold and wet. The game would be over for them, and next time they wouldn't fall in the river.
+ Objects also have a state. On, off, broken, glowing, whatever. Use that to create interesting things across rooms as well.
