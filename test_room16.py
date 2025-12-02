import pytest
from unittest.mock import patch, MagicMock
from player import Player
from Room16_gabriel import Room, FakeKey, RealKey, GrandfatherClock, FakeKeypad, Door
import time


class TestRoom16:
    """Comprehensive unit tests for Room 16"""
    
    @pytest.fixture
    def player(self):
        """Create a test player"""
        return Player("TestPlayer", 100, "normal", 16)
    
    @pytest.fixture
    def room(self):
        """Create a fresh room instance"""
        return Room()
    
    # Test Room Initialization
    def test_room_initialization(self, room):
        """Test that room initializes with correct attributes"""
        assert room.room_num == 16
        assert "Victorian study" in room.description
        assert room.exits == ["west"]
        assert len(room.objects) == 5
        assert room.clock_unlocked == False
        assert room.door_unlocked == False
    
    # Test Objects Creation
    def test_fake_key_exists(self, room):
        """Test that fake key is created and visible"""
        fake_key = room.get_item_from_object_list("rusty_key")
        assert fake_key is not None
        assert fake_key.visible == True
        assert fake_key.can_be_gotten == True
    
    def test_real_key_hidden(self, room):
        """Test that real key starts hidden"""
        real_key = room.get_item_from_object_list("key_16_west")
        assert real_key is not None
        assert real_key.visible == False
        assert real_key.can_be_gotten == True
    
    def test_clock_locked(self, room):
        """Test that grandfather clock starts locked"""
        clock = room.get_item_from_object_list("clock")
        assert clock is not None
        assert clock.state == "locked"
        assert clock.can_be_gotten == False
    
    def test_door_locked(self, room):
        """Test that door starts locked"""
        door = room.get_item_from_object_list("door")
        assert door is not None
        assert door.state == "locked"
        assert door.can_be_gotten == False
    
    def test_keypad_exists(self, room):
        """Test that fake keypad exists"""
        keypad = room.get_item_from_object_list("keypad")
        assert keypad is not None
        assert keypad.can_be_gotten == False
    
    # Test Object Use Methods
    def test_fake_key_use(self, capsys):
        """Test fake key use method"""
        fake_key = FakeKey("rusty_key", "test", True, None, True)
        fake_key.use()
        captured = capsys.readouterr()
        assert "doesn't fit" in captured.out or "wrong key" in captured.out
    
    def test_real_key_use(self, capsys):
        """Test real key use method"""
        real_key = RealKey("key_16_west", "test", True, None, True)
        real_key.use()
        captured = capsys.readouterr()
        assert "correct key" in captured.out
    
    def test_clock_use(self, capsys):
        """Test grandfather clock use method"""
        clock = GrandfatherClock("clock", "test", False, "locked", True)
        clock.use()
        captured = capsys.readouterr()
        assert "examine" in captured.out
    
    def test_keypad_use(self, capsys):
        """Test fake keypad use method"""
        keypad = FakeKeypad("keypad", "test", False, None, True)
        keypad.use()
        captured = capsys.readouterr()
        assert "decoy" in captured.out or "nothing happens" in captured.out
    
    # Test Helper Methods
    def test_get_item_from_inventory(self, room, player):
        """Test retrieving items from player inventory"""
        fake_key = room.get_item_from_object_list("rusty_key")
        player.inventory.append(fake_key)
        
        result = room.get_item_from_inventory("rusty_key", player)
        assert result is not None
        assert result.name == "rusty_key"
    
    def test_get_item_from_object_list(self, room):
        """Test retrieving items from room objects"""
        clock = room.get_item_from_object_list("clock")
        assert clock is not None
        assert clock.name == "clock"
    
    def test_get_nonexistent_item(self, room, player):
        """Test getting non-existent item returns None"""
        result = room.get_item_from_inventory("nonexistent", player)
        assert result is None
        
        result = room.get_item_from_object_list("nonexistent")
        assert result is None
    
    # Test Get/Drop Commands
    def test_get_visible_item(self, room, player, capsys):
        """Test getting a visible item"""
        room.get("rusty_key", player)
        captured = capsys.readouterr()
        assert "take" in captured.out
        assert player.has_item("rusty_key")
    
    def test_get_hidden_item(self, room, player, capsys):
        """Test that hidden items cannot be gotten"""
        room.get("key_16_west", player)
        captured = capsys.readouterr()
        assert "don't see" in captured.out
        assert not player.has_item("key_16_west")
    
    def test_get_already_owned_item(self, room, player, capsys):
        """Test getting item already in inventory"""
        room.get("rusty_key", player)
        capsys.readouterr()  # Clear
        room.get("rusty_key", player)
        captured = capsys.readouterr()
        assert "already have" in captured.out
    
    def test_get_nonexistent_item_command(self, room, player, capsys):
        """Test getting non-existent item"""
        room.get("banana", player)
        captured = capsys.readouterr()
        assert "not here" in captured.out
    
    def test_drop_item(self, room, player, capsys):
        """Test dropping an item"""
        room.get("rusty_key", player)
        capsys.readouterr()  # Clear
        room.drop("rusty_key", player)
        captured = capsys.readouterr()
        assert "drop" in captured.out
        assert not player.has_item("rusty_key")
    
    def test_drop_nonexistent_item(self, room, player, capsys):
        """Test dropping item not in inventory"""
        room.drop("banana", player)
        captured = capsys.readouterr()
        assert "don't have" in captured.out
    
    # Test Look Command
    def test_look_at_room(self, room, capsys):
        """Test looking at the room with no target"""
        room.describe_room()
        captured = capsys.readouterr()
        assert "Victorian study" in captured.out
        assert "rusty_key" in captured.out
    
    def test_look_at_clock_locked(self, room, player, capsys):
        """Test looking at locked clock"""
        room.look("clock", player)
        captured = capsys.readouterr()
        assert "magnificent" in captured.out
        assert "locked" in captured.out
    
    def test_look_at_clock_unlocked(self, room, player, capsys):
        """Test looking at unlocked clock"""
        clock = room.get_item_from_object_list("clock")
        clock.state = "unlocked"
        room.look("clock", player)
        captured = capsys.readouterr()
        assert "open" in captured.out
    
    def test_look_at_door(self, room, player, capsys):
        """Test looking at door"""
        room.look("door", player)
        captured = capsys.readouterr()
        assert "wooden door" in captured.out or "key" in captured.out
    
    def test_look_at_keypad(self, room, player, capsys):
        """Test looking at keypad"""
        room.look("keypad", player)
        captured = capsys.readouterr()
        assert "keypad" in captured.out or "buttons" in captured.out
    
    # Test Examine Command
    def test_examine_clock_locked(self, room, player, capsys):
        """Test examining locked clock gives puzzle hint"""
        room.examine("clock", player)
        captured = capsys.readouterr()
        assert "compartment" in captured.out
        assert "solve clock" in captured.out
    
    def test_examine_clock_unlocked(self, room, player, capsys):
        """Test examining unlocked clock"""
        clock = room.get_item_from_object_list("clock")
        clock.state = "unlocked"
        room.examine("clock", player)
        captured = capsys.readouterr()
        assert "open" in captured.out or "empty" in captured.out
    
    # Test Clock Puzzle
    @patch('builtins.input', side_effect=['26', '68', '60'])
    @patch('time.sleep', return_value=None)
    def test_solve_clock_puzzle_success(self, mock_sleep, mock_input, room, player, capsys):
        """Test successfully solving clock puzzle"""
        # Mock the math questions to be predictable
        room.generate_math_questions = lambda: [
            ("What is 13 + 13?", 26),
            ("What is 78 - 10?", 68),
            ("What is 15 × 4?", 60)
        ]
        
        room.solve_clock_puzzle(player)
        captured = capsys.readouterr()
        
        assert "SUCCESS" in captured.out
        assert room.clock_unlocked == True
        assert player.score == 30
        
        # Check that real key is now visible
        real_key = room.get_item_from_object_list("key_16_west")
        assert real_key.visible == True
    
    @patch('builtins.input', side_effect=['25', '67', '59'])
    @patch('time.sleep', return_value=None)
    def test_solve_clock_puzzle_failure(self, mock_sleep, mock_input, room, player, capsys):
        """Test failing clock puzzle"""
        room.generate_math_questions = lambda: [
            ("What is 13 + 13?", 26),
            ("What is 78 - 10?", 68),
            ("What is 15 × 4?", 60)
        ]
        
        room.solve_clock_puzzle(player)
        captured = capsys.readouterr()
        
        assert "0/3" in captured.out or "Wrong" in captured.out
        assert room.clock_unlocked == False
        assert player.score == 0
    
    def test_solve_already_unlocked_clock(self, room, player, capsys):
        """Test solving clock that's already unlocked"""
        clock = room.get_item_from_object_list("clock")
        clock.state = "unlocked"
        room.clock_unlocked = True
        
        room.solve_clock_puzzle(player)
        captured = capsys.readouterr()
        assert "already solved" in captured.out
    
    # Test Math Question Generation
    def test_generate_math_questions(self, room):
        """Test that math questions are generated correctly"""
        questions = room.generate_math_questions()
        
        assert len(questions) == 3
        for question, answer in questions:
            assert isinstance(question, str)
            assert isinstance(answer, int)
            assert "?" in question
    
    # Test Unlock Command
    def test_unlock_door_with_real_key(self, room, player, capsys):
        """Test unlocking door with correct key"""
        # Give player the real key
        real_key = room.get_item_from_object_list("key_16_west")
        real_key.visible = True
        room.get("key_16_west", player)
        capsys.readouterr()  # Clear
        
        room.unlock("door", player)
        captured = capsys.readouterr()
        
        assert "unlock" in captured.out
        assert room.door_unlocked == True
    
    def test_unlock_door_with_fake_key(self, room, player, capsys):
        """Test unlocking door with wrong key"""
        room.get("rusty_key", player)
        capsys.readouterr()  # Clear
        
        room.unlock("door", player)
        captured = capsys.readouterr()
        
        assert "doesn't fit" in captured.out or "wrong" in captured.out
        assert room.door_unlocked == False
    
    def test_unlock_door_without_key(self, room, player, capsys):
        """Test unlocking door without any key"""
        room.unlock("door", player)
        captured = capsys.readouterr()
        
        assert "don't have" in captured.out
        assert room.door_unlocked == False
    
    # Test Move Command
    def test_move_west_door_locked(self, room, player, capsys):
        """Test moving west when door is locked"""
        result = room.move("west", player)
        captured = capsys.readouterr()
        
        assert result is None
        assert "locked" in captured.out
    
    def test_move_west_door_unlocked(self, room, player, capsys):
        """Test moving west when door is unlocked"""
        room.door_unlocked = True
        initial_score = player.score
        
        result = room.move("west", player)
        captured = capsys.readouterr()
        
        assert result == "west"
        assert player.score == initial_score + 50
    
    def test_move_invalid_direction(self, room, player, capsys):
        """Test moving in invalid direction"""
        result = room.move("north", player)
        captured = capsys.readouterr()
        
        assert result is None
        assert "can't go" in captured.out
    
    # Test Try Keypad
    def test_try_keypad(self, room, capsys):
        """Test that keypad is non-functional"""
        room.try_keypad()
        captured = capsys.readouterr()
        
        assert "non-functional" in captured.out or "decoy" in captured.out
    
    # Test Use Command
    def test_use_key_calls_unlock(self, room, player, capsys):
        """Test that using a key calls unlock"""
        room.get("rusty_key", player)
        capsys.readouterr()  # Clear
        
        room.use("rusty_key", player)
        captured = capsys.readouterr()
        
        assert "doesn't fit" in captured.out or "wrong" in captured.out
    
    def test_use_nonexistent_item(self, room, player, capsys):
        """Test using non-existent item"""
        room.use("banana", player)
        captured = capsys.readouterr()
        
        assert "can't use" in captured.out
    
    # Test Show Methods
    def test_show_inventory(self, room, player, capsys):
        """Test showing inventory"""
        room.show_inventory(player)
        captured = capsys.readouterr()
        assert "inventory" in captured.out.lower()
    
    def test_show_stats(self, room, player, capsys):
        """Test showing stats"""
        room.show_stats(player)
        captured = capsys.readouterr()
        assert "TestPlayer" in captured.out
        assert "100" in captured.out
    
    @patch('builtins.input', return_value='yes')
    def test_quit_game_yes(self, mock_input, room, player, capsys):
        """Test quitting game with yes"""
        result = room.quit_game(player)
        captured = capsys.readouterr()
        
        assert result == "quit"
        assert "Final Score" in captured.out
    
    @patch('builtins.input', return_value='no')
    def test_quit_game_no(self, mock_input, room, player):
        """Test declining to quit"""
        result = room.quit_game(player)
        assert result is None
    
    # Test Help and Hint
    def test_show_help(self, room, capsys):
        """Test help command"""
        room.show_help()
        captured = capsys.readouterr()
        
        assert "commands" in captured.out.lower()
        assert "solve clock" in captured.out
    
    def test_show_hint_clock_locked(self, room, player, capsys):
        """Test hint when clock is locked"""
        room.show_hint(player)
        captured = capsys.readouterr()
        
        assert "grandfather clock" in captured.out.lower()
    
    def test_show_hint_clock_unlocked_no_key(self, room, player, capsys):
        """Test hint when clock unlocked but key not taken"""
        room.clock_unlocked = True
        room.show_hint(player)
        captured = capsys.readouterr()
        
        assert "get" in captured.out or "brass key" in captured.out
    
    def test_show_hint_has_key_door_locked(self, room, player, capsys):
        """Test hint when player has key but door locked"""
        # Unlock clock first so we can get the key
        room.clock_unlocked = True
        real_key = room.get_item_from_object_list("key_16_west")
        real_key.visible = True
        room.get("key_16_west", player)
        capsys.readouterr()  # Clear the get output
        
        room.show_hint(player)
        captured = capsys.readouterr()
        
        assert "unlock" in captured.out or "door" in captured.out
    
    # Integration Test
    @patch('builtins.input', side_effect=['26', '68', '60'])
    @patch('time.sleep', return_value=None)
    def test_full_puzzle_solution_flow(self, mock_sleep, mock_input, room, player, capsys):
        """Test complete puzzle solution from start to finish"""
        # Solve puzzle
        room.generate_math_questions = lambda: [
            ("What is 13 + 13?", 26),
            ("What is 78 - 10?", 68),
            ("What is 15 × 4?", 60)
        ]
        room.solve_clock_puzzle(player)
        
        # Get the real key
        room.get("key_16_west", player)
        
        # Unlock door
        room.unlock("door", player)
        
        # Move west
        result = room.move("west", player)
        
        # Verify everything worked
        assert room.clock_unlocked == True
        assert room.door_unlocked == True
        assert player.has_item("key_16_west")
        assert result == "west"
        assert player.score == 80  # 30 for puzzle + 50 for exit
