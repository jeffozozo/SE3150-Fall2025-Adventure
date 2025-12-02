import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from Room20_pace import Room, Barry
from player import Player
from object import Object


class TestRoom20Pace(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset the shared objects list (it's a class variable, shared across instances)
        Room.objects = []
        self.room = Room()
        self.player = Player("TestPlayer", 100, "healthy", 20)
        # Ensure Barry starts alive for each test
        barry = self.room.get_item_from_object_list("barry the bee")
        if barry:
            barry.state = "alive"
    
    def test_room_initialization(self):
        """Test that the room initializes correctly."""
        self.assertEqual(self.room.room_num, 20)
        self.assertEqual(self.room.exits, ["south", "east"])
        self.assertEqual(len(self.room.objects), 1)
        self.assertIsInstance(self.room.objects[0], Barry)
    
    def test_barry_initialization(self):
        """Test that Barry is created with correct attributes."""
        barry = self.room.objects[0]
        self.assertEqual(barry.name, "Barry the Bee")
        self.assertEqual(barry.state, "alive")
        self.assertFalse(barry.can_be_gotten)
        self.assertTrue(barry.visible)
    
    def test_describe_room_barry_alive(self):
        """Test room description when Barry is alive."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.describe_room()
            output = fake_out.getvalue()
            self.assertIn("Barry the Bee", output)
            self.assertIn("buzzing in the air", output)
            self.assertIn("There is a Barry the Bee here", output)
    
    def test_describe_room_barry_dead(self):
        """Test room description when Barry is dead."""
        barry = self.room.objects[0]
        barry.state = "dead"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.describe_room()
            output = fake_out.getvalue()
            self.assertIn("Barry the Bee lies defeated", output)
            self.assertIn("no longer a threat", output)
            self.assertIn("defeated Barry the Bee", output)
    
    def test_look_barry_alive(self):
        """Test looking at Barry when he's alive."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.look("barry", self.player)
            output = fake_out.getvalue()
            self.assertIn("Barry the Bee", output)
            self.assertIn("Jerry Seinfeld", output)
            self.assertIn("take your wife", output)
    
    def test_look_barry_dead(self):
        """Test looking at Barry when he's dead."""
        barry = self.room.objects[0]
        barry.state = "dead"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.look("barry", self.player)
            output = fake_out.getvalue()
            self.assertIn("Barry the Bee lies defeated", output)
            self.assertIn("no longer a threat", output)
    
    def test_look_barry_variations(self):
        """Test looking at Barry with different name variations."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.look("barry the bee", self.player)
            output = fake_out.getvalue()
            self.assertIn("Barry the Bee", output)
    
    def test_attack_without_mjolnir(self):
        """Test attacking Barry without Mjolnir - player should die."""
        initial_health = self.player.health
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.attack("barry", self.player)
            output = fake_out.getvalue()
            self.assertIn("bare hands", output)
            self.assertIn("stings you", output)
            self.assertIn("Mjolnir", output)
            self.assertIn("venom", output)
            self.assertIn("darkness", output)
        
        # Player should be dead
        self.assertEqual(self.player.health, 0)
        self.assertFalse(self.player.is_alive())
        # Barry should still be alive
        barry = self.room.objects[0]
        self.assertEqual(barry.state, "alive")
    
    def test_attack_with_mjolnir(self):
        """Test attacking Barry with Mjolnir - Barry should die."""
        # Create a mock Mjolnir object
        mjolnir = Object("Mjolnir", "Thor's mighty hammer", True, "normal", True)
        self.player.inventory.append(mjolnir)
        
        barry = self.room.objects[0]
        initial_state = barry.state
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.attack("barry", self.player)
            output = fake_out.getvalue()
            self.assertIn("Mjolnir", output)
            self.assertIn("Lightning", output)
            self.assertIn("struck down", output)
            self.assertIn("defeated", output)
        
        # Barry should be dead
        self.assertEqual(barry.state, "dead")
        # Player should still be alive
        self.assertTrue(self.player.is_alive())
        self.assertEqual(self.player.health, 100)
    
    def test_attack_barry_already_dead(self):
        """Test attacking Barry when he's already dead."""
        barry = self.room.objects[0]
        barry.state = "dead"
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.attack("barry", self.player)
            output = fake_out.getvalue()
            self.assertIn("already defeated", output)
            self.assertIn("no need to attack", output)
    
    def test_attack_no_target(self):
        """Test attack command with no target."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.attack("", self.player)
            output = fake_out.getvalue()
            self.assertIn("Attack what?", output)
    
    def test_attack_invalid_target(self):
        """Test attack command with invalid target."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.attack("wall", self.player)
            output = fake_out.getvalue()
            self.assertIn("can't attack", output)
    
    def test_get_barry(self):
        """Test that Barry cannot be taken."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.get("barry the bee", self.player)
            output = fake_out.getvalue()
            self.assertIn("cannot be taken", output)
        
        # Barry should still be in the room
        self.assertEqual(len(self.room.objects), 1)
        self.assertFalse(self.player.has_item("barry the bee"))
    
    def test_move_south(self):
        """Test moving south."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.room.move("south")
            output = fake_out.getvalue()
            self.assertIn("well", output)
            self.assertIn("tingles", output)
            self.assertEqual(result, "south")
    
    def test_move_east(self):
        """Test moving east."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.room.move("east")
            output = fake_out.getvalue()
            self.assertIn("well", output)
            self.assertEqual(result, "east")
    
    def test_move_invalid_direction(self):
        """Test moving in invalid direction."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.room.move("north")
            output = fake_out.getvalue()
            self.assertIn("can't go that way", output)
            self.assertIsNone(result)
    
    def test_show_help(self):
        """Test help command."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.show_help()
            output = fake_out.getvalue()
            self.assertIn("attack", output)
            self.assertIn("move", output)
            self.assertIn("look", output)
    
    def test_show_hint(self):
        """Test hint command."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.show_hint()
            output = fake_out.getvalue()
            self.assertIn("Barry the Bee", output)
            self.assertIn("Mjolnir", output)
            self.assertIn("dangerous", output)
    
    def test_use_barry(self):
        """Test using Barry."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.use("barry the bee", self.player)
            output = fake_out.getvalue()
            self.assertIn("can't use Barry", output)
    
    def test_get_item_from_object_list(self):
        """Test getting item from object list."""
        barry = self.room.get_item_from_object_list("barry the bee")
        self.assertIsNotNone(barry)
        self.assertEqual(barry.name, "Barry the Bee")
        
        nonexistent = self.room.get_item_from_object_list("nonexistent")
        self.assertIsNone(nonexistent)
    
    def test_get_item_from_inventory(self):
        """Test getting item from inventory."""
        # Add an item to inventory
        test_item = Object("TestItem", "A test item", True, "normal", True)
        self.player.inventory.append(test_item)
        
        item = self.room.get_item_from_inventory("testitem", self.player)
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "TestItem")
        
        nonexistent = self.room.get_item_from_inventory("nonexistent", self.player)
        self.assertIsNone(nonexistent)
    
    def test_attack_case_insensitive(self):
        """Test that attack command works with case variations."""
        mjolnir = Object("Mjolnir", "Thor's mighty hammer", True, "normal", True)
        self.player.inventory.append(mjolnir)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.attack("BARRY", self.player)
            output = fake_out.getvalue()
            self.assertIn("Mjolnir", output)
        
        barry = self.room.objects[0]
        self.assertEqual(barry.state, "dead")
    
    def test_room_description_updates_after_barry_death(self):
        """Test that room description updates after Barry is killed."""
        mjolnir = Object("Mjolnir", "Thor's mighty hammer", True, "normal", True)
        self.player.inventory.append(mjolnir)
        
        # Attack and kill Barry
        self.room.attack("barry", self.player)
        
        # Check that description was updated
        self.assertIn("lies defeated", self.room.description)
        self.assertIn("no longer a threat", self.room.description)
    
    def test_show_inventory(self):
        """Test showing inventory."""
        test_item = Object("TestItem", "A test item", True, "normal", True)
        self.player.inventory.append(test_item)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.show_inventory(self.player)
            output = fake_out.getvalue()
            self.assertIn("TestItem", output)
    
    def test_show_stats(self):
        """Test showing player stats."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.room.show_stats(self.player)
            output = fake_out.getvalue()
            self.assertIn("TestPlayer", output)
            self.assertIn("Health", output)
            self.assertIn("100", output)


if __name__ == '__main__':
    unittest.main()

