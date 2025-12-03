import builtins
import pytest
import sys
from unittest.mock import MagicMock
import Room14_oliver as room_module 
from Room14_oliver import Room, LifeBuoy, Object

# ---- Mocks and Fakes ----

class FakePlayer:
    """
    A stand-in for the Player class.
    We updated this because your new code fixed the 'has_item' bug! 
    It now correctly expects a string name, not an object.
    """
    def __init__(self):
        self.inventory = []
        self.health = 100
        self.score = 0
        self.condition = []
        self.current_room = None
        # Flags to verify method calls
        self._inventory_shown = False
        self._stats_shown = False

    def has_item(self, item_name: str) -> bool:
        # Your updated code correctly passes a string now.
        return any(item.name.lower() == item_name.lower() for item in self.inventory)

    def is_alive(self):
        return self.health > 0

    def show_inventory(self):
        self._inventory_shown = True

    def print_stats(self):
        self._stats_shown = True

@pytest.fixture
def clean_room():
    """Resets the room and objects list for every test."""
    Room.objects = []
    return Room()

@pytest.fixture
def player():
    return FakePlayer()

@pytest.fixture
def mock_timed_input(monkeypatch):
    """Mocks the timed_input function so we don't actually wait for time."""
    mock = MagicMock()
    monkeypatch.setattr(room_module, "timed_input", mock)
    return mock

@pytest.fixture
def bypass_printwait(monkeypatch):
    """Bypasses the 'Press Enter to Continue' pauses."""
    monkeypatch.setattr(builtins, "input", lambda *args: "")

# ---- Initialization Tests ----

def test_room_initial_state(clean_room):
    assert clean_room.room_num == 14  # Updated from 0 to 14
    assert "obstacle course in the sea" in clean_room.description
    assert clean_room.exits == ["north"]
    assert len(clean_room.objects) == 0

def test_describe_room(clean_room, capsys):
    clean_room.describe_room()
    out = capsys.readouterr().out
    assert "obstacle course" in out

# ---- Movement & Obstacle Course Tests ----

def test_move_north_perfect_run(clean_room, player, mock_timed_input, bypass_printwait, capsys):
    """
    Path: User answers all questions correctly.
    """
    # Answers: 1. 't' (Box), 2. 'a' (Seagull), 3. 'cos' (Math)
    mock_timed_input.side_effect = ["t", "a", "cos"]
    
    result = clean_room.move("north", player)
    out = capsys.readouterr().out
    
    # Assertions
    assert "jumped over to a barrel" in out
    assert "dodged out of the way" in out
    assert "correct answer" in out
    assert "reached the shore" in out  # Updated text
    assert result == "north"
    
    # Check Player State
    assert player.health == 100
    assert player.has_item("Life Buoy") # Should receive the item

def test_move_north_survivable_failure(clean_room, player, mock_timed_input, bypass_printwait, capsys):
    """
    Path: User gets everything wrong but has enough health to survive.
    """
    # Answers: 1. 'z' (Wrong Box), 2. None (Seagull Timeout), 3. 'tan' (Wrong Math)
    mock_timed_input.side_effect = ["z", None, "tan"]
    
    result = clean_room.move("north", player)
    out = capsys.readouterr().out

    # Assertions
    assert "collapsed" in out
    assert "Ouch! -10 Health" in out
    assert "papercut" in out
    assert "reached the shore" in out
    
    # Check Damage Calculation
    # -10 (Box) -10 (Seagull) -1 (Math) = -21 total
    assert player.health == 79
    assert "Emotionally Damaged" in player.condition
    assert player.has_item("Life Buoy") # Still gets the item

def test_move_north_death_first_obstacle(clean_room, player, mock_timed_input, bypass_printwait, capsys):
    """
    Path: User fails an obstacle and dies.
    """
    player.health = 5 # Set low health
    # Fail the first obstacle ("z") which deals 10 damage
    mock_timed_input.side_effect = ["z"] 

    # We expect the game to exit here
    with pytest.raises(SystemExit):
        clean_room.move("north", player)
    
    out = capsys.readouterr().out
    assert "You have perished" in out
    assert player.health <= 0

def test_move_north_death_second_obstacle(clean_room, player, mock_timed_input, bypass_printwait, capsys):
    """
    Path: User fails an obstacle and dies.
    """
    player.health = 5 # Set low health
    # Fail the second obstacle, deals 10 damage
    mock_timed_input.side_effect = ["t","acos"] 

    # We expect the game to exit here
    with pytest.raises(SystemExit):
        clean_room.move("north", player)
    
    out = capsys.readouterr().out
    assert "You have perished" in out
    assert player.health <= 0

def test_move_north_death_third_obstacle(clean_room, player, mock_timed_input, bypass_printwait, capsys):
    """
    Path: User fails an obstacle and dies.
    """
    player.health = 1 # Set low health
    # Fail the third obstacle, deals 1 damage
    mock_timed_input.side_effect = ["t","a","-sin"] 

    # We expect the game to exit here
    with pytest.raises(SystemExit):
        clean_room.move("north", player)
    
    out = capsys.readouterr().out
    assert "You have perished" in out
    assert player.health <= 0

def test_move_north_shortcut_with_lifebuoy(clean_room, player, monkeypatch, capsys):
    """
    Path: User has the Life Buoy and chooses to use it.
    """
    # 1. Give player the item
    lb = LifeBuoy()
    player.inventory.append(lb)
    
    # 2. Mock input to say "yes" to the "Do you want to use it?" prompt
    monkeypatch.setattr(builtins, "input", lambda *args: "yes")
    
    result = clean_room.move("north", player)
    out = capsys.readouterr().out
    
    assert "skipped the obstacle course" in out
    assert result == "north"
    assert player.health == 100 # No damage taken

def test_move_north_refuse_shortcut(clean_room, player, mock_timed_input, monkeypatch, capsys):
    """
    Path: User has Life Buoy but says 'no' to shortcut.
    The test ensures that if they say no, the obstacle course logic RUNS.
    """
    lb = LifeBuoy()
    player.inventory.append(lb)
    
    # Mock inputs: 
    # This lambda returns "no" forever. 
    # 1. "no" to "Do you want to use it?" -> Enters course.
    # 2. "no" to any printwait() calls inside the course -> acts as pressing Enter.
    monkeypatch.setattr(builtins, "input", lambda *args: "no")
    
    # We provide the answers for the obstacle course because we expect it to run
    mock_timed_input.side_effect = ["t", "a", "cos"]
    
    # We simply call the function. We do NOT expect an error.
    clean_room.move("north", player)
    
    out = capsys.readouterr().out
    
    # ASSERTION: 
    # If the user took the shortcut, this text would NOT be here.
    # Since we refused the shortcut, we expect to see the obstacle description.
    assert "doesn't feel stable" in out 
    assert "correct answer" in out

# ---- Interaction Tests (Get, Drop, Use) ----

def test_get_item(clean_room, player, capsys):
    obj = Object("Key", "Desc", True, None, True)
    clean_room.objects.append(obj)
    
    clean_room.get("Key", player)
    
    assert player.has_item("Key")
    assert len(clean_room.objects) == 0

def test_drop_item(clean_room, player, capsys):
    obj = Object("Key", "Desc", True, None, True)
    player.inventory.append(obj)
    
    clean_room.drop("Key", player)
    
    assert not player.has_item("Key")
    assert len(clean_room.objects) == 1

def test_use_lifebuoy_restriction(clean_room, player, capsys):
    """Verify LifeBuoy cannot be used directly via command."""
    lb = LifeBuoy()
    player.inventory.append(lb)
    
    clean_room.use("life buoy", player)
    out = capsys.readouterr().out
    assert "need to use the life buoy when prompted" in out

# ---- Helper & Logic Tests ----

def test_damage_player_fatal(clean_room, player, capsys):
    """Test the dedicated damage method specifically."""
    player.health = 5
    with pytest.raises(SystemExit):
        clean_room.damage_player(player, 10)
    
    out = capsys.readouterr().out
    assert "Game over" in out

def test_hint(clean_room, capsys):
    clean_room.show_hint()
    assert "tacos" in capsys.readouterr().out

def test_quit_game(clean_room, player, monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda *args: "yes")
    result = clean_room.quit_game(player)
    assert result == "quit"
    assert "Final Score" in capsys.readouterr().out