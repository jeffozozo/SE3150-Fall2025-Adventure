from unittest.mock import MagicMock, patch
from Room7_nicolas import Room, RustyCoin
from player import Player


def describe_Room_7_Unit_Tests():

    def describe_setup():

        def it_has_a_coin_in_the_room():
            room = Room()
            coin = room.get_item_from_object_list("coin")
            assert coin is not None
            assert isinstance(coin, RustyCoin)

    def describe_commands():

        def it_can_get_and_drop_the_coin():
            room = Room()
            player = Player("nick", 100, "healthy", 7)

            room.get("coin", player)
            assert player.has_item("coin")
            assert room.get_item_from_object_list("coin") is None

            room.drop("coin", player)
            assert not player.has_item("coin")
            assert room.get_item_from_object_list("coin") is not None

        def it_can_use_the_coin():
            room = Room()
            player = Player("nick", 100, "healthy", 7)

            coin = room.get_item_from_object_list("coin")
            assert coin is not None
            # In your current Room, the coin starts "rusty"
            assert coin.state == "rusty"

            room.use("coin", player)

            # After use(), your implementation sets it to "clean"
            assert coin.state == "clean"

        def it_can_look_at_the_coin():
            room = Room()
            player = Player("nick", 100, "healthy", 7)

            with patch("builtins.print") as mock_print:
                room.look("coins", player)

            # Just check that the description was printed at least once
            calls = [str(args[0]) for args, _ in mock_print.call_args_list]
            assert any("rusty coin engraved with a swirling pattern" in c for c in calls)

        def it_can_show_inventory():
            room = Room()
            player = MagicMock()
            room.show_inventory(player)
            player.show_inventory.assert_called_once()

        def it_can_show_stats():
            room = Room()
            player = MagicMock()
            room.show_stats(player)
            player.print_stats.assert_called_once()

        def it_shows_help_without_crashing():
            room = Room()
            with patch("builtins.print") as mock_print:
                room.show_help()
            # We don't care about exact text, just that something was printed
            assert mock_print.called

        def it_shows_hint_without_crashing():
            room = Room()
            with patch("builtins.print") as mock_print:
                room.show_hint()
            assert mock_print.called

    def describe_movement():

        def it_can_move_down():
            room = Room()
            assert room.move("down") == "down"

        def it_rejects_other_directions():
            room = Room()
            assert room.move("north") is None
            assert room.move("south") is None
            assert room.move("east") is None
            assert room.move("west") is None
            assert room.move("up") is None
