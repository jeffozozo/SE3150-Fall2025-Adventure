import builtins
import types
import pytest
from Room9_garrett import Room

class FakePlayer:
    def __init__(self):
        self.name = "Tester"
        self.health = 100
        self.condition = []
        self.inventory = []
        self.score = 0
        self.current_room = 9
    def is_alive(self):
        return self.health > 0
    def show_inventory(self):
        pass
    def print_stats(self):
        pass

def feed_inputs(monkeypatch, inputs):
    it = iter(inputs)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(it))

def test_riddles_repeat_until_correct(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = [
        "talk",
        "idk", "incorrectly",
        "nope", "door",
        "huh", "piano",
        "east"
    ]
    feed_inputs(monkeypatch, inputs)
    result = room.enter(player)
    assert result == "east"
    assert player.score == 10*3 + 20
    assert player.health == 100 - 5*3

def test_reward_added(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = ["talk", "incorrectly", "door", "piano", "inventory", "east"]
    feed_inputs(monkeypatch, inputs)
    room.enter(player)
    assert any(item.name == "Bag of Acorns" for item in player.inventory)

def test_exit_blocked_until_reward(monkeypatch, capsys):
    room = Room()
    player = FakePlayer()
    inputs = ["east", "talk", "incorrectly", "door", "piano", "east"]
    feed_inputs(monkeypatch, inputs)
    result = room.enter(player)
    out = capsys.readouterr().out
    # Assert that the first "east" command is blocked (look for a blocking message)
    assert "You can't leave yet" in out or "You must earn the reward before exiting" in out or "The exit is blocked" in out
    assert result == "east"
def test_talk_after_reward(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = ["talk", "incorrectly", "door", "piano", "talk", "east"]
    feed_inputs(monkeypatch, inputs)
    result = room.enter(player)
    assert result == "east"
    assert sum(1 for i in player.inventory if i.name == "Bag of Acorns") == 1

def test_hint(monkeypatch, capsys):
    room = Room()
    player = FakePlayer()
    inputs = ["hint", "talk", "incorrectly", "door", "piano", "hint", "east"]
    feed_inputs(monkeypatch, inputs)
    room.enter(player)
    out = capsys.readouterr().out
    assert "Try 'talk' to the wizard" in out or "You’ve already earned the Bag of Acorns" in out
    
def test_all_correct(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = ["talk", "incorrectly", "door", "piano", "east"]
    feed_inputs(monkeypatch, inputs)
    result = room.enter(player)
    assert result == "east"
    assert player.score == 10*3 + 20
    assert player.health == 100

def test_multiple_wrong_attempts(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = [
        "talk",
        "idk", "incorrectly",
        "nope", "door",
        "wrong", "wrong", "piano",
        "south"
    ]
    feed_inputs(monkeypatch, inputs)
    result = room.enter(player)
    assert result == "south"
    assert player.score == 10*3 + 20
    assert player.health == 100 - (1+1+2)*5

def test_inventory_contains_acorns(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = ["talk", "incorrectly", "door", "piano", "inventory", "east"]
    feed_inputs(monkeypatch, inputs)
    room.enter(player)
    assert any(item.name == "Bag of Acorns" for item in player.inventory)

def test_hint_changes(monkeypatch, capsys):
    room = Room()
    player = FakePlayer()
    inputs = ["hint", "talk", "incorrectly", "door", "piano", "hint", "east"]
    feed_inputs(monkeypatch, inputs)
    room.enter(player)
    out = capsys.readouterr().out
    assert "Try 'talk' to the wizard" in out or "You’ve already earned the Bag of Acorns" in out

def test_no_duplicate_rewards(monkeypatch):
    room = Room()
    player = FakePlayer()
    inputs = ["talk", "incorrectly", "door", "piano", "talk", "east"]
    feed_inputs(monkeypatch, inputs)
    room.enter(player)
    assert sum(1 for i in player.inventory if i.name == "Bag of Acorns") == 1

def feed_inputs(monkeypatch, inputs):
    it = iter(inputs)
    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            return "quit"
    monkeypatch.setattr(builtins, "input", fake_input)
