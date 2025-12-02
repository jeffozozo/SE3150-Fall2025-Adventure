import pytest
from io import StringIO
import sys
from unittest.mock import patch, MagicMock

from Room2_saul import Room, AzulOro, Needle

class FakePlayer:
    def __init__(self):
        self.name = "Test Player"
        self.health = 100
        self.condition = ["healthy"]
        self.inventory = []
        self.current_room = 2
        self.score = 0
    
    def has_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return True
        return False
    
    def get_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None
    
    def show_inventory(self):
        if not self.inventory:
            print("Your inventory is empty.")
        else:
            print("Inventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description}")
    
    def print_stats(self):
        print(f"{self.name}")
        print(f"Health: {self.health}")
        print("Condition:", self.condition)
        print(f"Current Room: {self.current_room}")
        print(f"Score: {self.score}")
    
    def is_alive(self):
        return self.health > 0


class TestRoomInitialization: 
    def test_room_number(self):
        room = Room()
        assert room.room_num == 2
    
    def test_room_description(self):
        room = Room()
        assert room.description is not None
        assert len(room.description) > 0
        assert "rat" in room.description.lower() or "cheese" in room.description.lower()
    
    def test_room_has_objects(self):
        room = Room()
        assert len(room.objects) == 2
        
        ring = None
        needle = None
        for obj in room.objects:
            if obj.name == "azul_oro":
                ring = obj
            elif obj.name == "needle":
                needle = obj
        
        assert ring is not None, "Room should contain azul_oro ring"
        assert needle is not None, "Room should contain needle"
    
    def test_room_exits(self):
        room = Room()
        assert "south" in room.exits
        assert "east" in room.exits
        assert "up" in room.exits


class TestAzulOroRing:
    def test_ring_initialization(self):
        """Test ring is properly initialized"""
        ring = AzulOro("azul_oro", "A beautiful ring", True, "unworn", True)
        assert ring.name == "azul_oro"
        assert ring.can_be_gotten == True
        assert ring.state == "unworn"
        assert ring.visible == True
    
    def test_ring_use_method(self, capsys):
        """Test ring's use method"""
        ring = AzulOro("azul_oro", "A beautiful ring", True, "unworn", True)
        ring.use()
        captured = capsys.readouterr()
        assert "wear" in captured.out.lower()


class TestNeedle:
    def test_needle_initialization(self):
        needle = Needle("needle", "A sharp needle", True, "sharp", True)
        assert needle.name == "needle"
        assert needle.can_be_gotten == True
        assert needle.state == "sharp"
        assert needle.visible == True
    
    def test_needle_use_method(self, capsys):
        needle = Needle("needle", "A sharp needle", True, "sharp", True)
        needle.use()
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestGetAndDrop:
    def test_get_ring(self, capsys):
        """Test picking up the ring"""
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        captured = capsys.readouterr()
        
        assert player.has_item("azul_oro")
        assert len(room.objects) == 1  # Only needle should remain
        assert "take" in captured.out.lower() or "add" in captured.out.lower()
    
    def test_get_needle(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("needle", player)
        captured = capsys.readouterr()
        
        assert player.has_item("needle")
        assert len(room.objects) == 1  # Only ring should remain
    
    def test_get_nonexistent_item(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("banana", player)
        captured = capsys.readouterr()
        
        assert not player.has_item("banana")
        assert "no" in captured.out.lower() or "not" in captured.out.lower()
    
    def test_get_already_have(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()  
        
        room.get("azul_oro", player)
        captured = capsys.readouterr()
        
        assert "already" in captured.out.lower() or "no" in captured.out.lower()
    
    def test_drop_item(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()
        
        room.drop("azul_oro", player)
        captured = capsys.readouterr()
        
        assert not player.has_item("azul_oro")
        assert len(room.objects) == 2  
        assert "drop" in captured.out.lower()
    
    def test_drop_item_not_in_inventory(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.drop("banana", player)
        captured = capsys.readouterr()
        
        assert "don't" in captured.out.lower() or "not" in captured.out.lower()


class TestLook:
    def test_look_at_room(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "azul_oro" in captured.out.lower() or "needle" in captured.out.lower()
    
    def test_look_at_ring(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("azul_oro", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "unworn" in captured.out.lower()
    
    def test_look_at_needle(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("needle", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "sharp" in captured.out.lower() or "needle" in captured.out.lower()
    
    def test_look_at_cheese(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("cheese", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "cheese" in captured.out.lower()
    
    def test_look_at_rats(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("rats", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "rat" in captured.out.lower()
    
    def test_look_at_crack(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("crack", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "crack" in captured.out.lower() or "wall" in captured.out.lower()
    
    def test_look_at_nonexistent(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.look("banana", player)
        captured = capsys.readouterr()
        
        assert "nothing" in captured.out.lower() or "not" in captured.out.lower()


class TestWearAndRemove:
    def test_wear_ring_from_inventory(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()
        
        room.wear("azul_oro", player)
        captured = capsys.readouterr()
        
        ring = player.get_item("azul_oro")
        assert ring.state == "worn"
        assert "mouse" in player.condition
        assert player.score > 0  
        assert "transform" in captured.out.lower() or "mouse" in captured.out.lower()
    
    def test_wear_ring_alternate_names(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()
        
        # Try with "ring"
        room.wear("ring", player)
        captured = capsys.readouterr()
        
        assert "mouse" in player.condition
        assert len(captured.out) > 0
    
    def test_wear_ring_not_in_inventory(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.wear("azul_oro", player)
        captured = capsys.readouterr()
        
        assert "pick" in captured.out.lower() or "need" in captured.out.lower()
        assert "mouse" not in player.condition
    
    def test_wear_ring_already_worn(self, capsys):
        """Test trying to wear ring when already wearing it"""
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()
        
        room.wear("azul_oro", player)
        capsys.readouterr()
        
        room.wear("azul_oro", player)
        captured = capsys.readouterr()
        
        assert "already" in captured.out.lower()
    
    def test_remove_ring(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        room.wear("azul_oro", player)
        capsys.readouterr()
        
        room.remove("azul_oro", player)
        captured = capsys.readouterr()
        
        ring = player.get_item("azul_oro")
        assert ring.state == "unworn"
        assert "mouse" not in player.condition
        assert "human" in captured.out.lower() or "normal" in captured.out.lower()
    
    def test_remove_ring_not_worn(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()
        
        room.remove("azul_oro", player)
        captured = capsys.readouterr()
        
        assert "not wearing" in captured.out.lower()
    
    def test_wear_non_wearable(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.wear("needle", player)
        captured = capsys.readouterr()
        
        assert "can't" in captured.out.lower()


class TestMovement:
    def test_move_south(self, capsys):
        room = Room()
        player = FakePlayer()
        
        result = room.move("south", player)
        captured = capsys.readouterr()
        
        assert result == "south"
        assert len(captured.out) > 0
    
    def test_move_up(self, capsys):
        room = Room()
        player = FakePlayer()
        
        result = room.move("up", player)
        captured = capsys.readouterr()
        
        assert result == "up"
        assert len(captured.out) > 0
    
    def test_move_east_without_transformation(self, capsys):
        room = Room()
        player = FakePlayer()
        
        result = room.move("east", player)
        captured = capsys.readouterr()
        
        assert result is None
        assert "small" in captured.out.lower() or "mouse" in captured.out.lower()
    
    def test_move_east_with_transformation(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        room.wear("azul_oro", player)
        capsys.readouterr()
        
        result = room.move("east", player)
        captured = capsys.readouterr()
        
        assert result == "east"
        assert "squeeze" in captured.out.lower() or "through" in captured.out.lower()
    
    def test_move_invalid_direction(self, capsys):
        room = Room()
        player = FakePlayer()
        
        result = room.move("north", player)
        captured = capsys.readouterr()
        
        assert result is None
        assert "can't" in captured.out.lower()
    
    def test_move_with_abbreviations(self, capsys):
        room = Room()
        player = FakePlayer()
        
        result_s = room.move("s", player)
        assert result_s == "south"
        
        result_u = room.move("u", player)
        assert result_u == "up"
        
        result_e = room.move("e", player)
        assert result_e is None  


class TestHelperMethods:
    
    def test_get_item_from_inventory(self):
        room = Room()
        player = FakePlayer()
        
        # Add ring to inventory
        ring = room.get_item_from_object_list("azul_oro")
        player.inventory.append(ring)
        
        # Try to get it
        found = room.get_item_from_inventory("azul_oro", player)
        assert found is not None
        assert found.name == "azul_oro"
    
    def test_get_item_from_object_list(self):
        room = Room()
        
        ring = room.get_item_from_object_list("azul_oro")
        assert ring is not None
        assert ring.name == "azul_oro"
        
        needle = room.get_item_from_object_list("needle")
        assert needle is not None
        assert needle.name == "needle"
    
    def test_get_nonexistent_from_object_list(self):
        room = Room()
        
        item = room.get_item_from_object_list("banana")
        assert item is None


class TestUse:
    def test_use_ring_from_inventory(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        capsys.readouterr()
        
        room.use("azul_oro", player)
        captured = capsys.readouterr()
        
        assert "wear" in captured.out.lower()
    
    def test_use_needle(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("needle", player)
        capsys.readouterr()
        
        room.use("needle", player)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
    
    def test_use_nonexistent(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.use("banana", player)
        captured = capsys.readouterr()
        
        assert "can't" in captured.out.lower()


class TestInventoryAndStats:
    def test_show_inventory_empty(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.show_inventory(player)
        captured = capsys.readouterr()
        
        assert "empty" in captured.out.lower()
    
    def test_show_inventory_with_items(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        room.get("needle", player)
        capsys.readouterr()
        
        room.show_inventory(player)
        captured = capsys.readouterr()
        
        assert "azul_oro" in captured.out.lower() or "ring" in captured.out.lower()
        assert "needle" in captured.out.lower()
    
    def test_show_stats(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.show_stats(player)
        captured = capsys.readouterr()
        
        assert "health" in captured.out.lower()
        assert "score" in captured.out.lower()


class TestHelpAndHints:
    def test_show_help(self, capsys):
        room = Room()
        
        room.show_help()
        captured = capsys.readouterr()
        
        assert "command" in captured.out.lower()
        assert "move" in captured.out.lower() or "go" in captured.out.lower()
    
    def test_show_hint(self, capsys):
        room = Room()
        
        room.show_hint()
        captured = capsys.readouterr()
        
        assert "ring" in captured.out.lower() or "wear" in captured.out.lower()
    
    def test_unknown_command(self, capsys):
        room = Room()
        
        room.unknown_command()
        captured = capsys.readouterr()
        
        assert "can't" in captured.out.lower() or "help" in captured.out.lower()


class TestQuit:
    @patch('builtins.input', return_value='yes')
    def test_quit_yes(self, mock_input, capsys):
        room = Room()
        player = FakePlayer()
        
        result = room.quit_game(player)
        captured = capsys.readouterr()
        
        assert result == "quit"
        assert "score" in captured.out.lower()
    
    @patch('builtins.input', return_value='no')
    def test_quit_no(self, mock_input):
        room = Room()
        player = FakePlayer()
        
        result = room.quit_game(player)
        
        assert result is None


class TestDescribeRoom:
    def test_describe_room_with_objects(self, capsys):
        room = Room()
        
        room.describe_room()
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0
        assert "azul_oro" in captured.out.lower() or "needle" in captured.out.lower()
    
    def test_describe_room_after_taking_objects(self, capsys):
        room = Room()
        player = FakePlayer()
        
        room.get("azul_oro", player)
        room.get("needle", player)
        capsys.readouterr()
        
        room.describe_room()
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])