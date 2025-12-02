import builtins
import pytest

from Room17_andy_rich import (
    Person,
    Wizard,
    Bed,
    Weight,
    HealthPotion,
    Room,
)


# ---------- Test helpers ----------

class FakePlayer:
    """Simple fake player with just what Room needs."""

    def __init__(self):
        self.inventory = []
        self.health = 10
        self.score = 0

    def has_item(self, name: str) -> bool:
        for item in self.inventory:
            if item.name.lower() == name.lower():
                return True
        return False

    def show_inventory(self):
        # For tests we just print something simple
        names = [item.name for item in self.inventory]
        print("INVENTORY:", ", ".join(names))

    def print_stats(self):
        print(f"Health: {self.health}, Score: {self.score}")


@pytest.fixture
def room():
    """
    Fresh Room instance for each test.

    Room.objects and Room.persons are class variables, so we reset them
    before constructing a new Room to avoid cross-test contamination.
    """
    Room.objects = []
    Room.persons = []
    return Room()


@pytest.fixture
def player():
    return FakePlayer()


# ---------- Person tests ----------

def test_person_stores_lowercase_name_and_description(capsys):
    p = Person("Wizard", "A test person.")
    assert p.name == "wizard"
    assert p.description == "A test person."

    p.interact()
    out = capsys.readouterr().out
    assert "Wizard" in out  # title-cased in message


# ---------- Wizard tests ----------

def test_wizard_inherits_from_person():
    w = Wizard()
    assert isinstance(w, Person)
    assert w.name == "wizard"
    assert len(w.questions) == 3
    assert w.asked_count == 0


def test_wizard_interact_stops_when_asked_count_at_least_three(capsys):
    w = Wizard()
    w.asked_count = 3
    w.interact()
    out = capsys.readouterr().out
    assert "I've told you all I can for now" in out


def test_wizard_interact_increments_asked_count(monkeypatch, capsys):
    """
    Simulate asking one question (choice '1') and then exiting ('0').
    """
    w = Wizard()

    inputs = iter(["1", "0"])  # first time choose question 1, then nevermind

    def fake_input(prompt=""):
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)

    w.interact()

    # After one valid question, asked_count should be 1
    assert w.asked_count == 1
    out = capsys.readouterr().out
    # We don't need to check every line, just that something wizard-y happened
    assert "You ask: Who are you?" in out or "Wizard:" in out


# ---------- Object subclass tests ----------

def test_bed_use_prints_message(capsys):
    bed = Bed("Bed", "desc", False, None, True)
    bed.use()
    out = capsys.readouterr().out
    assert "bed looks surprisingly comfy" in out.lower()


def test_weight_use_prints_message(capsys):
    w = Weight("Weight", "desc", True, None, True)
    w.use()
    out = capsys.readouterr().out
    assert "wow" in out.lower()


def test_health_potion_use_prints_message(capsys):
    p = HealthPotion("Health Potion", "desc", True, None, True)
    p.use()
    out = capsys.readouterr().out
    assert "potion" in out.lower()


# ---------- Room initialization tests ----------

def test_room_initial_state(room):
    assert room.room_num == 17  # make sure you updated this in your Room code

    # Objects
    names = sorted(obj.name for obj in room.objects)
    assert names == ["Bed", "Health Potion", "Weight"]

    # Persons
    assert len(room.persons) == 1
    assert room.persons[0].name == "wizard"

    # Exits
    assert sorted(room.exits) == ["north", "south"]


# ---------- Room movement tests ----------

def test_room_move_valid_south_and_north(room, capsys):
    # south
    result_s = room.move("south")
    out_s = capsys.readouterr().out
    assert result_s == "south"
    assert "south" in out_s.lower()

    # north
    result_n = room.move("north")
    out_n = capsys.readouterr().out
    assert result_n == "north"
    assert "north" in out_n.lower()


def test_room_move_invalid_direction(room, capsys):
    result = room.move("west")
    out = capsys.readouterr().out
    assert result is None
    assert "you can't go that way" in out.lower()


# ---------- Room item lookup tests ----------

def test_get_item_from_object_list(room):
    bed = room.get_item_from_object_list("Bed")
    assert bed is not None
    assert isinstance(bed, Bed)

    potion = room.get_item_from_object_list("health potion")
    assert potion is not None
    assert isinstance(potion, HealthPotion)

    assert room.get_item_from_object_list("NotReal") is None


def test_get_item_from_inventory(room, player):
    # Put Weight in inventory manually
    weight = room.get_item_from_object_list("Weight")
    player.inventory.append(weight)

    found = room.get_item_from_inventory("weight", player)
    assert found is weight

    not_found = room.get_item_from_inventory("not-inventory", player)
    assert not_found is None


# ---------- Room get / drop tests ----------

def test_get_weight_moves_it_to_inventory(room, player, capsys):
    # Precondition: Weight is in the room, not in inventory
    weight_in_room = room.get_item_from_object_list("Weight")
    assert weight_in_room is not None
    assert not player.has_item("Weight")

    room.get("Weight", player)
    out = capsys.readouterr().out

    assert player.has_item("Weight")
    assert room.get_item_from_object_list("Weight") is None
    assert "add it to your inventory" in out.lower()


def test_get_bed_cannot_be_taken(room, player, capsys):
    room.get("Bed", player)
    out = capsys.readouterr().out
    assert "cannot be taken" in out.lower()
    assert not player.has_item("Bed")


def test_drop_moves_item_back_to_room(room, player, capsys):
    # Put Health Potion into inventory
    potion = room.get_item_from_object_list("Health Potion")
    player.inventory.append(potion)
    room.objects.remove(potion)

    assert player.has_item("Health Potion")
    assert room.get_item_from_object_list("Health Potion") is None

    room.drop("Health Potion", player)
    out = capsys.readouterr().out

    assert not player.has_item("Health Potion")
    assert room.get_item_from_object_list("Health Potion") is not None
    assert "you drop the health potion" in out.lower()


# ---------- Room use tests ----------

def test_use_bed_increases_health_by_five(room, player, capsys):
    start_health = player.health
    room.use("Bed", player)
    out = capsys.readouterr().out

    assert player.health == start_health + 5
    assert "nap" in out.lower()


def test_use_weight_increases_score_by_five(room, player, capsys):
    start_score = player.score
    room.use("Weight", player)
    out = capsys.readouterr().out

    assert player.score == start_score + 5
    assert "impressive form" in out.lower()


def test_use_health_potion_does_not_change_health(room, player, capsys):
    start_health = player.health
    room.use("Health Potion", player)
    out = capsys.readouterr().out

    assert player.health == start_health
    assert "nothing changes" in out.lower()


def test_use_unknown_item_prints_error(room, player, capsys):
    room.use("NotRealItem", player)
    out = capsys.readouterr().out
    assert "you can't use that" in out.lower()


# ---------- Room interact tests ----------

def test_interact_with_no_target_prints_message(room, player, capsys):
    room.interact("", player)
    out = capsys.readouterr().out
    assert "interact with who" in out.lower()


def test_interact_with_unknown_person_prints_message(room, player, capsys):
    room.interact("ghost", player)
    out = capsys.readouterr().out
    assert "don't see anyone called 'ghost'" in out.lower()


def test_interact_with_wizard_calls_interact(room, player):
    # Replace the wizard's interact with a fake to detect call
    wizard = room.get_person_by_name("wizard")
    called = {"value": False}

    def fake_interact():
        called["value"] = True

    wizard.interact = fake_interact

    room.interact("wizard", player)
    assert called["value"] is True


# ---------- Room describe / help / hint / quit tests ----------

def test_describe_room_lists_objects_and_persons(room, capsys, player):
    room.describe_room()
    out = capsys.readouterr().out

    # Check for description and object/person names
    assert "cramped, cluttered room" in out.lower()
    assert "bed" in out.lower()
    assert "weight" in out.lower()
    assert "health potion" in out.lower()
    assert "wizard" in out.lower()


def test_show_help_lists_commands(room, capsys, player):
    room.show_help()
    out = capsys.readouterr().out
    assert "move" in out.lower()
    assert "look" in out.lower()
    assert "use" in out.lower()
    assert "interact" in out.lower()


def test_show_hint_prints_hint(room, capsys, player):
    room.show_hint()
    out = capsys.readouterr().out
    assert "try using some of the items" in out.lower()


def test_quit_game_yes_exits(room, player, monkeypatch, capsys):
    # Simulate user entering "yes"
    monkeypatch.setattr(builtins, "input", lambda prompt="": "yes")

    with pytest.raises(SystemExit):
        room.quit_game(player)

    out = capsys.readouterr().out
    assert "final score" in out.lower()


def test_quit_game_no_does_not_exit(room, player, monkeypatch, capsys):
    # Simulate user entering "no"
    monkeypatch.setattr(builtins, "input", lambda prompt="": "no")

    # Should not raise SystemExit
    room.quit_game(player)
    out = capsys.readouterr().out
    # No specific requirement, but ensure we didn't print Final Score
    assert "final score" not in out.lower()
