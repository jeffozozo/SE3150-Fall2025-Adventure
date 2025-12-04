import pytest

from Room3_gisela import Room, Mirror


# ----------------- DUMMIES ----------------- #

class DummyPlayer:
    """Minimal replacement for Player, just enough for this room."""
    def __init__(self):
        self.inventory = []
        self.condition = []
        self.health = 100
        self.score = 0

    def show_inventory(self):
        pass

    def print_stats(self):
        pass


class DummyNeedle:
    name = "Needle"
    description = "A sharp little needle."
    state = None

    def use(self):
        # In the real game this might do nothing;
        # Room.use() handles the cockroach logic.
        pass


class DummyAzulOro:
    name = "Azul Oro"
    description = "A shimmering charm of transformation."
    state = None

    def use(self, player):
        # In the real object, using Azul Oro might set mouse condition.
        # For testing, we can simulate that here if you want to rely on it.
        player.condition.append("mouse")


# ------------- FIXTURES / SETUP ------------- #

@pytest.fixture(autouse=True)
def reset_room_objects():
    """
    Room.objects is a class-level list, so reset it before each test
    to avoid leaking objects between tests.
    """
    Room.objects = []
    yield
    Room.objects = []


@pytest.fixture
def room():
    return Room()


@pytest.fixture
def player():
    return DummyPlayer()


# ------------- BASIC ROOM SETUP ------------- #

def test_room_initializes_with_mirror(room):
    assert any(isinstance(obj, Mirror) for obj in room.objects)
    assert room.mirror in room.objects
    assert room.exits == ["down", "west", "south"]


def test_describe_room_prints_description_and_mirror(room, capsys):
    room.describe_room()
    out = capsys.readouterr().out

    assert "Bathed in a soft pink glow" in out
    assert "There is a Mirror here." in out


# ------------- LOOK LOGIC ------------- #

def test_look_no_target_shows_room_and_notices(room, player, capsys):
    room.look("", player)
    out = capsys.readouterr().out

    assert "Bathed in a soft pink glow" in out
    assert "You notice:" in out
    assert "DOWN" in out
    assert "WEST" in out
    assert "SOUTH" in out


def test_look_at_mirror_triggers_mirror_use(room, player, capsys):
    room.look("mirror", player)
    out = capsys.readouterr().out

    assert "Turn away, but the mirror won’t forget you… and you shouldn’t forget it." in out


def test_look_at_cockroach_prints_hint(room, player, capsys):
    room.look("cockroach", player)
    out = capsys.readouterr().out

    assert "Where's pest control when you need it?" in out


def test_look_at_west_shows_crack_and_guard_if_not_slayed(room, player, capsys):
    room.look("west", player)
    out = capsys.readouterr().out

    assert "narrow crack runs down the western wall" in out
    assert "A large cockroach guards the crack." in out


def test_look_at_west_after_slayed_cucaracha_shows_crack_only(room, player, capsys):
    player.condition.append("slayed_cucaracha")

    room.look("west", player)
    out = capsys.readouterr().out

    assert "narrow crack runs down the western wall" in out
    assert "cockroach" not in out.lower()


def test_look_unknown_target(room, player, capsys):
    room.look("nonexistent", player)
    out = capsys.readouterr().out

    assert "There is nothing like nonexistent to look at." in out


# ------------- USE LOGIC ------------- #

def test_use_unknown_item_prints_cant_use(room, player, capsys):
    room.use("nothing", player)
    out = capsys.readouterr().out

    assert "you can't use that." in out.lower()


def test_use_mirror_via_use_command(room, player, capsys):
    room.use("mirror", player)
    out = capsys.readouterr().out

    assert "Turn away, but the mirror won’t forget you… and you shouldn’t forget it." in out


def test_use_needle_sets_slayed_cucaracha_condition(room, player):
    # Put dummy Needle in inventory
    player.inventory.append(DummyNeedle())

    # For this to work, Room.use must check item.name, not item itself:
    # if item.name in ["Dagger", "Needle", "Mjolnir"]:
    room.use("Needle", player)

    assert "slayed_cucaracha" in player.condition


# ------------- EXIT / MOVE LOGIC (WEST & SOUTH) ------------- #

def test_move_south_always_allows_exit(room, player):
    result = room.move("south", player)
    assert result == "south"


def test_move_west_blocked_without_slayed_cucaracha(room, player, capsys):
    result = room.move("west", player)
    out = capsys.readouterr().out

    assert result is None
    assert "A pest stands in your way." in out


def test_move_west_requires_mouse_after_slayed_cucaracha(room, player, capsys):
    # Pretend player has already slain the cockroach
    player.condition.append("slayed_cucaracha")

    result = room.move("west", player)
    out = capsys.readouterr().out

    assert result is None
    assert "far too small for you to fit through" in out


def test_move_west_succeeds_with_slayed_cucaracha_and_mouse(room, player, capsys):
    player.condition.extend(["slayed_cucaracha", "mouse"])

    result = room.move("west", player)
    out = capsys.readouterr().out

    assert result == "west"
    assert "Through the cracks you go" in out


# ------------- HINT LOGIC ------------- #

def test_show_hint_before_any_conditions(room, player, capsys):
    room.show_hint(player)
    out = capsys.readouterr().out

    assert "Try looking at the mirror more closely" in out
    assert "cockroach blocks the western passage" in out


def test_show_hint_after_slayed_cucaracha_before_mouse(room, player, capsys):
    player.condition.append("slayed_cucaracha")

    room.show_hint(player)
    out = capsys.readouterr().out

    assert "western crack is too small" in out


def test_show_hint_after_slayed_cucaracha_and_mouse(room, player, capsys):
    player.condition.extend(["slayed_cucaracha", "mouse"])

    room.show_hint(player)
    out = capsys.readouterr().out

    assert "You seem ready to explore. Try the available exits: west, down, south" in out
