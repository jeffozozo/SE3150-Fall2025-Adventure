import unittest
from unittest.mock import patch, MagicMock
from Room4_JoshBice import Room, LightningSkull


class FakePlayer:
    def __init__(self):
        self.health = 10
        self.inventory = []
        self.condition = []
        self.score = 0

    def has_item(self, name):
        return any(i.name == name for i in self.inventory)

    def show_inventory(self):
        print("INVENTORY:", [i.name for i in self.inventory])

    def print_stats(self):
        print(f"Health: {self.health}")

class FakeObject:
    def __init__(self, name="fake", description="a fake object", can_be_gotten=True, state=None, visible=True):
        self.name = name
        self.description = description
        self.can_be_gotten = can_be_gotten
        self.state = state
        self.visible = visible

    def use(self):
        print(f"You use the {self.name}, but nothing happens.")


class TestRoom4(unittest.TestCase):

    def setUp(self):
        self.room = Room()
        self.player = FakePlayer()

    @patch("builtins.print")
    def test_describe_room_prints(self, mock_print):
        self.room.describe_room()
        mock_print.assert_any_call(self.room.description)
        mock_print.assert_any_call("Exits: up, west")

    @patch("builtins.print")
    def test_move_up_no_vine(self, mock_print):
        self.player.condition.append("vine_snapped")
        result = self.room.move("up", self.player)
        self.assertIsNone(result)
        mock_print.assert_called_with("There is no vine left to climb. The path upward is gone.")

    @patch("builtins.print")
    def test_move_west(self, mock_print):
        result = self.room.move("west", self.player)
        self.assertEqual(result, "west")
        self.assertIn("lock_tree", self.player.condition)

    def test_move_invalid(self):
        with patch("builtins.print") as p:
            result = self.room.move("north", self.player)
            self.assertIsNone(result)
            p.assert_called_with("You can't go that way.")

    def test_fake_object_get_and_drop(self):
        fake = FakeObject(name="rock")
        self.room.objects.append(fake)

        with patch("builtins.print") as p:
            self.room.get("rock", self.player)
            p.assert_called_with("You pick up the rock.")

        self.assertIn(fake, self.player.inventory)

        with patch("builtins.print") as p:
            self.room.drop("rock", self.player)
            p.assert_called_with("You drop the rock.")


    def test_get_item_from_inventory(self):
        skull = LightningSkull()
        self.player.inventory.append(skull)
        found = self.room.get_item_from_inventory("skull", self.player)
        self.assertEqual(found, skull)

    def test_get_item_from_object_list(self):
        skull = LightningSkull()
        self.room.objects.append(skull)
        found = self.room.get_item_from_object_list("skull")
        self.assertEqual(found, skull)

    @patch("builtins.print")
    def test_get_item_success(self, mock_print):
        skull = LightningSkull()
        self.room.objects.append(skull)
        self.room.get("skull", self.player)

        self.assertIn(skull, self.player.inventory)
        self.assertNotIn(skull, self.room.objects)
        mock_print.assert_called_with("You pick up the skull.")

    @patch("builtins.print")
    def test_get_item_not_here(self, mock_print):
        self.room.get("skull", self.player)
        mock_print.assert_called_with("There is no skull here.")

    @patch("builtins.print")
    def test_get_item_already_have(self, mock_print):
        skull = LightningSkull()
        self.player.inventory.append(skull)
        self.room.get("skull", self.player)
        mock_print.assert_called_with("You already have the skull.")

    @patch("builtins.print")
    def test_drop_success(self, mock_print):
        skull = LightningSkull()
        self.player.inventory.append(skull)
        self.room.drop("skull", self.player)

        self.assertIn(skull, self.room.objects)
        self.assertNotIn(skull, self.player.inventory)
        mock_print.assert_called_with("You drop the skull.")

    @patch("builtins.print")
    def test_drop_no_item(self, mock_print):
        self.room.drop("skull", self.player)
        mock_print.assert_called_with("You don't have a skull.")

    @patch("builtins.print")
    def test_use_inventory_item(self, mock_print):
        skull = LightningSkull()
        self.player.inventory.append(skull)
        self.room.use("skull", self.player)
        mock_print.assert_called_with("You don't really know what this does.")

    @patch("builtins.print")
    def test_use_invalid(self, mock_print):
        self.room.use("banana", self.player)
        mock_print.assert_called_with("You can't use that.")

    @patch.object(Room, "trigger_fight_scene")
    def test_look_triggers_scene(self, mock_scene):
        self.room.look("tree", self.player)
        mock_scene.assert_called_once()

    @patch("builtins.print")
    def test_look_unknown(self, mock_print):
        self.room.look("nothing", self.player)
        mock_print.assert_called_with("There is nothing like 'nothing' to look at.")

    @patch("builtins.input", return_value="punch")
    @patch("builtins.print")
    def test_fight_scene_punch(self, mock_print, mock_input):
        self.room.trigger_fight_scene(self.player)

        self.assertTrue(self.room.skeleton_defeated)
        self.assertIn("worthy", self.player.condition)
        self.assertEqual(len(self.room.objects), 1)
        self.assertIsInstance(self.room.objects[0], LightningSkull)
        self.assertEqual(self.player.health, 7) 

    @patch("builtins.input", return_value="slide")
    @patch("builtins.print")
    def test_fight_scene_slide(self, mock_print, mock_input):
        self.room.trigger_fight_scene(self.player)
        mock_print.assert_any_call("You quietly retreat, pretending you saw nothing.")

    @patch("builtins.print")
    def test_show_help(self, mock_print):
        self.room.show_help()
        mock_print.assert_called_with(
            "Commands: move/go, look, get/take, drop, use, inventory, stats, quit, hint, help"
        )

    @patch("builtins.print")
    def test_show_hint(self, mock_print):
        self.room.show_hint()
        mock_print.assert_called_with("Jeff may need your help… the tree is watching.")

    @patch("builtins.input", return_value="y")
    @patch("builtins.print")
    def test_quit_game_yes(self, mock_print, mock_input):
        result = self.room.quit_game(self.player)
        self.assertEqual(result, "quit")
        mock_print.assert_any_call("Final Score: 0")

    @patch("builtins.input", return_value="n")
    @patch("builtins.print")
    def test_quit_game_no(self, mock_print, mock_input):
        result = self.room.quit_game(self.player)
        self.assertIsNone(result)

    @patch("builtins.print")
    def test_unknown_command(self, mock_print):
        self.room.unknown_command()
        mock_print.assert_called_with("You can't do that here.")


if __name__ == "__main__":
    unittest.main()
