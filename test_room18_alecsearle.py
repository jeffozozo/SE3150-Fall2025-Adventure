import builtins
import pytest

from Room18_alecsearle import Room, Book


# ---- Test helpers ----

class FakePlayer:
    """Minimal stand-in for the real Player object."""

    def __init__(self):
        self.inventory = []
        self.score = 0
        self._inventory_shown = False
        self._stats_shown = False

    def has_item(self, item_name: str) -> bool:
        return any(item.name.lower() == item_name.lower() for item in self.inventory)

    def show_inventory(self):
        self._inventory_shown = True

    def print_stats(self):
        self._stats_shown = True


@pytest.fixture
def room():
    """
    Fresh room for each test.

    Room.objects is a class attribute, so we reset it to avoid tests
    leaking state into each other.
    """
    Room.objects = []
    return Room()


@pytest.fixture
def player():
    return FakePlayer()


# ---- Book tests ----

def test_book_use_toggles_state_and_messages(capsys):
    book = Book("Book", "An old, dusty book with a leather cover.", True, "off", True)

    # First use: place book on shelf
    assert book.state == "off"
    book.use()
    out = capsys.readouterr().out
    assert "place the book back onto the empty shelf" in out
    assert "soft click" in out
    assert book.state == "on"

    # Second use: remove book from shelf
    book.use()
    out = capsys.readouterr().out
    assert "remove the book from the shelf" in out
    assert "seal itself once more" in out
    assert book.state == "off"


# ---- Room initialization ----

def test_room_initial_state(room):
    assert room.room_num == 18
    assert "The room is lit like an old library." in room.description
    assert "Bookshelves line the walls to the south and east" in room.description

    # Exits
    assert sorted(room.exits) == ["east", "south"]

    # Objects
    assert len(room.objects) == 1
    book = room.objects[0]
    assert isinstance(book, Book)
    assert book.name == "Book"
    assert book.state == "off"
    assert book.can_be_gotten is True


def test_describe_room_shows_description_and_book(room, capsys):
    room.describe_room()
    out = capsys.readouterr().out
    assert "The room is lit like an old library." in out
    assert "There is a Book here." in out


# ---- Movement behavior ----

def test_move_south_blocked_when_book_not_placed(room, capsys):
    result = room.move("south")
    out = capsys.readouterr().out
    assert "bookshelf blocks your way" in out
    assert result is None


def test_move_east_blocked_when_book_not_placed(room, capsys):
    result = room.move("east")
    out = capsys.readouterr().out
    assert "The east bookshelf is just a wall of books." in out
    assert "You can't go that way." in out
    assert result is None


def test_move_south_allowed_when_book_placed(room, capsys):
    book = room.get_item_from_object_list("book")
    book.state = "on"

    result = room.move("south")
    out = capsys.readouterr().out
    assert "hidden passage has opened" in out
    assert result == "south"


def test_move_east_allowed_when_book_placed(room, capsys):
    book = room.get_item_from_object_list("book")
    book.state = "on"

    result = room.move("east")
    out = capsys.readouterr().out
    assert "secret door has revealed itself" in out
    assert result == "east"


def test_move_unknown_direction(room, capsys):
    result = room.move("north")
    out = capsys.readouterr().out
    assert "You can't go that way." in out
    assert result is None


# ---- Look behavior ----

def test_look_room_no_target_calls_describe(room, player, capsys):
    room.look("", player)
    out = capsys.readouterr().out
    assert "The room is lit like an old library." in out


def test_look_bookshelf(room, player, capsys):
    room.look("bookshelf", player)
    out = capsys.readouterr().out
    assert "filled with old books" in out
    assert "two empty spaces" in out


def test_look_book_in_room(room, player, capsys):
    room.look("book", player)
    out = capsys.readouterr().out
    assert "An old, dusty book with a leather cover." in out
    assert "is not on the shelf" in out


def test_look_book_when_on_shelf(room, player, capsys):
    book = room.get_item_from_object_list("book")
    book.state = "on"
    room.look("book", player)
    out = capsys.readouterr().out
    assert "An old, dusty book with a leather cover." in out
    assert "is placed on the shelf" in out


def test_look_unknown_target(room, player, capsys):
    room.look("lamp", player)
    out = capsys.readouterr().out
    assert "There is nothing like lamp to look at." in out


# ---- Get / drop / use ----

def test_get_book_moves_to_inventory_and_removes_from_room(room, player, capsys):
    assert len(player.inventory) == 0
    assert room.get_item_from_object_list("book") is not None

    room.get("Book", player)
    out = capsys.readouterr().out
    assert "You take the Book and add it to your inventory." in out

    # Now it's in inventory
    assert len(player.inventory) == 1
    assert player.inventory[0].name == "Book"
    # And no longer in the room
    assert room.get_item_from_object_list("book") is None


def test_get_book_already_in_inventory(room, player, capsys):
    # First get
    room.get("book", player)
    capsys.readouterr()

    # Second get
    room.get("book", player)
    out = capsys.readouterr().out
    assert "You already have the book." in out


def test_get_nonexistent_item(room, player, capsys):
    room.get("lamp", player)
    out = capsys.readouterr().out
    assert "lamp is not here." in out


def test_drop_book_moves_from_inventory_to_room(room, player, capsys):
    # Take it first
    room.get("book", player)
    capsys.readouterr()

    assert len(player.inventory) == 1
    assert room.get_item_from_object_list("book") is None

    room.drop("book", player)
    out = capsys.readouterr().out
    assert "You drop the Book." in out

    assert len(player.inventory) == 0
    assert room.get_item_from_object_list("book") is not None


def test_drop_item_not_in_inventory(room, player, capsys):
    room.drop("book", player)
    out = capsys.readouterr().out
    assert "You don't have the book." in out


def test_use_book_in_room(room, player, capsys):
    # Use directly from room
    room.use("book", player)
    out = capsys.readouterr().out
    assert "place the book back onto the empty shelf" in out

    # State should now be "on"
    book = room.get_item_from_object_list("book")
    assert book.state == "on"


def test_use_book_in_inventory(room, player, capsys):
    # First take the book
    room.get("book", player)
    capsys.readouterr()
    assert room.get_item_from_object_list("book") is None

    # Use from inventory
    room.use("book", player)
    out = capsys.readouterr().out
    # Should still trigger Book.use()
    assert "place the book back onto the empty shelf" in out


def test_use_unknown_item(room, player, capsys):
    room.use("lamp", player)
    out = capsys.readouterr().out
    assert "you can't use that." in out.lower()


# ---- Inventory / stats / helpers ----

def test_show_inventory_calls_player_method(room, player):
    assert not player._inventory_shown
    room.show_inventory(player)
    assert player._inventory_shown


def test_show_stats_calls_player_method(room, player):
    assert not player._stats_shown
    room.show_stats(player)
    assert player._stats_shown


def test_get_item_from_inventory_and_object_list(room, player):
    # In room
    book_room = room.get_item_from_object_list("book")
    assert isinstance(book_room, Book)

    # Move to inventory
    room.get("book", player)
    book_inv = room.get_item_from_inventory("book", player)
    assert isinstance(book_inv, Book)
    assert book_inv is player.inventory[0]


# ---- Help, hint, unknown_command ----

def test_show_help_prints_commands(room, capsys):
    room.show_help()
    out = capsys.readouterr().out
    assert "Available commands" in out
    assert "move" in out
    assert "hint" in out


def test_show_hint_prints_clue(room, capsys):
    room.show_hint()
    out = capsys.readouterr().out
    assert "book on the floor" in out
    assert "empty spaces on the shelves" in out


def test_unknown_command_message(room, capsys):
    room.unknown_command()
    out = capsys.readouterr().out
    assert "You can't do that here" in out


# ---- Quit behavior ----

def test_quit_game_yes(room, player, monkeypatch, capsys):
    # Simulate user typing "yes"
    monkeypatch.setattr(builtins, "input", lambda _: "yes")
    result = room.quit_game(player)
    out = capsys.readouterr().out
    assert "Final Score" in out
    assert result == "quit"


def test_quit_game_no(room, player, monkeypatch, capsys):
    # Simulate user typing "no"
    monkeypatch.setattr(builtins, "input", lambda _: "no")
    result = room.quit_game(player)
    out = capsys.readouterr().out
    assert "Final Score" not in out
    assert result is None
