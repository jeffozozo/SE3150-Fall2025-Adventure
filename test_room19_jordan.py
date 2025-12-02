import pytest
from unittest.mock import patch
from Room19_jordan import Room, Mjolnir
from player import Player
from object import Object


class TestRoomInitialization:
    def test_room_number_is_19(self):
        room = Room()
        assert room.room_num == 19
    
    def test_room_has_description(self):
        room = Room()
        assert len(room.description) > 0
        assert "Curtis Sliwa" in room.description
    
    def test_room_has_exits(self):
        room = Room()
        assert "south" in room.exits
    
    def test_room_starts_with_mjolnir(self):
        Room.objects = []
        room = Room()
        assert len(room.objects) >= 1
        assert any(obj.name == "Mjolnir" for obj in room.objects)
    
    def test_mjolnir_not_gettable_initially(self):
        room = Room()
        mjolnir = room.objects[0]
        assert mjolnir.can_be_gotten == False
    
    def test_quiz_not_completed_initially(self):
        room = Room()
        assert room.quiz_completed == False
    
    def test_quiz_not_failed_initially(self):
        room = Room()
        assert room.quiz_failed == False


class TestMjolnirObject:
    def test_mjolnir_creation(self):
        mjolnir = Mjolnir("Mjolnir", "Hammer of Thor", True, None, True)
        assert mjolnir.name == "Mjolnir"
        assert mjolnir.visible == True
    
    def test_mjolnir_use_prints_message(self, capsys):
        mjolnir = Mjolnir("Mjolnir", "Hammer", True, None, True)
        mjolnir.use()
        captured = capsys.readouterr()
        assert "Mjolnir" in captured.out or "use" in captured.out.lower()


class TestRoomMethods:
    def test_describe_room(self, capsys):
        room = Room()
        room.describe_room()
        captured = capsys.readouterr()
        assert "Curtis Sliwa" in captured.out
        assert "Mjolnir" in captured.out
    
    def test_move_south_returns_south(self, capsys):
        room = Room()
        result = room.move("south")
        assert result == "south"
    
    def test_move_invalid_direction_returns_none(self, capsys):
        room = Room()
        result = room.move("north")
        assert result is None
    
    def test_show_help(self, capsys):
        room = Room()
        room.show_help()
        captured = capsys.readouterr()
        assert "commands" in captured.out.lower()
    
    def test_show_hint_before_quiz(self, capsys):
        room = Room()
        room.show_hint()
        captured = capsys.readouterr()
        assert "Curtis" in captured.out or "worthy" in captured.out.lower()
    
    def test_show_hint_after_quiz(self, capsys):
        room = Room()
        room.quiz_completed = True
        room.show_hint()
        captured = capsys.readouterr()
        assert "worthy" in captured.out.lower() or "Mjolnir" in captured.out
    
    def test_unknown_command(self, capsys):
        room = Room()
        room.unknown_command()
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestPlayerInteraction:
    def test_get_item_from_inventory(self):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        test_item = Mjolnir("TestItem", "Test", True, None, True)
        player.inventory.append(test_item)
        
        found_item = room.get_item_from_inventory("testitem", player)
        assert found_item is not None
        assert found_item.name == "TestItem"
    
    def test_get_item_from_object_list(self):
        room = Room()
        mjolnir = room.get_item_from_object_list("mjolnir")
        assert mjolnir is not None
        assert mjolnir.name == "Mjolnir"
    
    def test_get_item_not_in_list(self):
        room = Room()
        item = room.get_item_from_object_list("fake_item")
        assert item is None


class TestLookCommand:
    def test_look_at_room(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.look(None, player)
        captured = capsys.readouterr()
        assert "Curtis" in captured.out
    
    def test_look_at_curtis(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.look("curtis", player)
        captured = capsys.readouterr()
        assert "Curtis" in captured.out
        assert "beret" in captured.out
    
    def test_look_at_mjolnir(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.look("mjolnir", player)
        captured = capsys.readouterr()
        assert "hammer" in captured.out.lower() or "Thor" in captured.out
    
    def test_look_at_nonexistent_item(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.look("banana", player)
        captured = capsys.readouterr()
        assert "nothing" in captured.out.lower()


class TestGetCommand:
    def test_get_mjolnir_before_worthy(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.get("mjolnir", player)
        captured = capsys.readouterr()
        assert "cannot be taken" in captured.out or "worthy" in captured.out.lower()
    
    def test_get_item_already_in_inventory(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        mjolnir = Mjolnir("Mjolnir", "Hammer", True, None, True)
        player.inventory.append(mjolnir)
        room.get("mjolnir", player)
        captured = capsys.readouterr()
        assert "already have" in captured.out
    
    def test_get_nonexistent_item(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.get("banana", player)
        captured = capsys.readouterr()
        assert "not here" in captured.out


class TestDropCommand:
    def test_drop_item_in_inventory(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        test_item = Mjolnir("TestItem", "Test", True, None, True)
        player.inventory.append(test_item)
        
        room.drop("testitem", player)
        captured = capsys.readouterr()
        assert "drop" in captured.out.lower()
        assert test_item not in player.inventory
        assert test_item in room.objects
    
    def test_drop_item_not_in_inventory(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.drop("banana", player)
        captured = capsys.readouterr()
        assert "don't have" in captured.out


class TestUseCommand:
    def test_use_mjolnir_in_room(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.use("mjolnir", player)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_use_nonexistent_item(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.use("banana", player)
        captured = capsys.readouterr()
        assert "can't use" in captured.out.lower()


class TestInventoryAndStats:
    def test_show_inventory(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.show_inventory(player)
        captured = capsys.readouterr()
        assert "inventory" in captured.out.lower() or "empty" in captured.out.lower()
    
    def test_show_stats(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.show_stats(player)
        captured = capsys.readouterr()
        assert "Test" in captured.out


class TestTalkToCurtis:
    def test_talk_before_quiz(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.talk_to_curtis(player)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_talk_after_quiz_completed(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.quiz_completed = True
        room.talk_to_curtis(player)
        captured = capsys.readouterr()
        assert "proved" in captured.out or "hammer" in captured.out.lower()
    
    def test_talk_with_mjolnir(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        mjolnir = Mjolnir("Mjolnir", "Hammer", True, None, True)
        player.inventory.append(mjolnir)
        room.talk_to_curtis(player)
        captured = capsys.readouterr()
        assert "hammer" in captured.out.lower() or "innocent" in captured.out.lower()


class TestQuizMechanics:
    def test_quiz_all_correct_not_worthy(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = False
        
        with patch('builtins.input', side_effect=['B', 'C', 'B']):
            room.run_worthiness_quiz(player)
        
        assert room.quiz_completed == True
        assert player.has_item("Mjolnir") == True
        assert player.score >= 150
    
    def test_quiz_two_correct_worthy(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = True
        
        with patch('builtins.input', side_effect=['B', 'C', 'A']):
            room.run_worthiness_quiz(player)
        
        assert room.quiz_completed == True
        assert player.has_item("Mjolnir") == True
    
    def test_quiz_two_correct_not_worthy_fails(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = False
        
        with patch('builtins.input', side_effect=['B', 'C', 'A']):
            room.run_worthiness_quiz(player)
        
        assert room.quiz_completed == False
        assert room.quiz_failed == True
        assert player.has_item("Mjolnir") == False
    
    def test_quiz_one_correct_not_worthy_fails(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = False
        
        with patch('builtins.input', side_effect=['A', 'A', 'B']):
            room.run_worthiness_quiz(player)
        
        assert room.quiz_failed == True
        assert player.has_item("Mjolnir") == False
    
    def test_quiz_one_correct_worthy_fails(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = True
        
        with patch('builtins.input', side_effect=['A', 'A', 'B']):
            room.run_worthiness_quiz(player)
        
        assert room.quiz_failed == True
    
    def test_quiz_zero_correct_fails(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = False
        
        with patch('builtins.input', side_effect=['A', 'A', 'A']):
            room.run_worthiness_quiz(player)
        
        assert room.quiz_failed == True


class TestQuizFailedState:
    def test_quiz_failed_state_exists(self):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.quiz_failed = True
        
        assert room.quiz_failed == True


class TestScoring:
    def test_score_increases_on_quiz_completion(self):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        player.worthy = False
        initial_score = player.score
        
        with patch('builtins.input', side_effect=['B', 'C', 'B']):
            room.run_worthiness_quiz(player)
        
        assert player.score > initial_score
        assert player.score >= 150


class TestEdgeCases:
    def test_mjolnir_visible_initially(self):
        room = Room()
        mjolnir = room.objects[0]
        assert mjolnir.visible == True
    
    def test_room_objects_list_mutable(self):
        room = Room()
        initial_count = len(room.objects)
        test_item = Mjolnir("TestItem", "Test", True, None, True)
        room.objects.append(test_item)
        assert len(room.objects) == initial_count + 1
    
    def test_player_can_have_multiple_items(self):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        item1 = Mjolnir("Item1", "Test1", True, None, True)
        item2 = Mjolnir("Item2", "Test2", True, None, True)
        player.inventory.append(item1)
        player.inventory.append(item2)
        assert len(player.inventory) == 2
    
    def test_case_insensitive_item_lookup(self):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        mjolnir = room.get_item_from_object_list("MJOLNIR")
        assert mjolnir is not None
        
        mjolnir2 = room.get_item_from_object_list("mjolnir")
        assert mjolnir2 is not None
    
    def test_empty_look_target(self, capsys):
        room = Room()
        player = Player("Test", 100, "healthy", 0)
        room.look("", player)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
