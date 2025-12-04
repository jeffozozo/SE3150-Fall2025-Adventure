import random
import builtins
import pytest

from Room21_aydenwayman import Room
from player import Player
from object import Object


import random
import builtins
import pytest

from Room21_aydenwayman import Room
from player import Player
from object import Object


def make_player():
    return Player("Tester", 100, "healthy", 21)


def test_initial_random_objects_and_positions():
    # deterministic seed so positions are stable for the test
    random.seed(42)
    room = Room()
    room.reset_room()
    # Basic expectations
    assert hasattr(room, 'objects')
    # Millenium Eye should exist as an Object in the room
    eye = next((o for o in room.objects if o.name.lower() == 'millenium eye'), None)
    assert eye is not None
    # All objects must have a pos inside the 11x11 grid
    for obj in room.objects:
        assert hasattr(obj, 'pos')
        r, c = obj.pos
        assert 0 <= r < room.GRID_SIZE and 0 <= c < room.GRID_SIZE


def test_north_exit_requires_password(monkeypatch):
    random.seed(1)
    room = Room()
    room.reset_room()
    player = make_player()
    # move player to the north-exit square
    room.player_pos = [room.EXIT_NORTH[0], room.EXIT_NORTH[1]]

    # wrong password
    monkeypatch.setattr(builtins, 'input', lambda prompt='': 'nope')
    assert room.move('north', player) is None
    assert not getattr(room, 'password_unlocked', False)

    # correct password
    monkeypatch.setattr(builtins, 'input', lambda prompt='': '404')
    assert room.move('north', player) == 'north'


def test_west_exit_requires_millenium_eye():
    random.seed(2)
    room = Room()
    room.reset_room()
    player = make_player()
    room.player_pos = [room.EXIT_WEST[0], room.EXIT_WEST[1]]

    # without the eye the west exit does not open
    assert room.move('west', player) is None

    # give player the Millenium Eye and try again
    player.inventory.append(Object('Millenium Eye', 'ancient', True, None, True))
    assert player.has_item('Millenium Eye')
    assert room.move('west', player) == 'west'


def test_stepping_on_mine_raises_systemexit():
    random.seed(3)
    room = Room()
    room.reset_room()
    player = make_player()
    assert hasattr(room, 'mine_pos')
    mr, mc = room.mine_pos
    # place player adjacent to mine and step onto it
    # choose a valid adjacent cell
    if mr > 0:
        room.player_pos = [mr - 1, mc]
        direction = 'south'
    else:
        room.player_pos = [mr + 1, mc]
        direction = 'north'

    with pytest.raises(SystemExit):
        room.move(direction, player)


def test_shuffler_triggers_object_movement():
    random.seed(4)
    room = Room()
    room.reset_room()
    player = make_player()
    before = {o.name: o.pos for o in room.objects}
    # step onto the first shuffler
    sr, sc = room.shuffler_positions[0]
    # approach from south if possible
    if sr + 1 < room.GRID_SIZE:
        room.player_pos = [sr + 1, sc]
        direction = 'north'
    else:
        room.player_pos = [sr - 1, sc]
        direction = 'south'

    room.move(direction, player)
    after = {o.name: o.pos for o in room.objects}
    # at least one object's position should differ after shuffle
    assert any(before[name] != after[name] for name in before)


def test_get_puts_object_in_inventory_and_mine_not_gettable():
    random.seed(5)
    room = Room()
    room.reset_room()
    player = make_player()
    # find a dummy object and move to its square
    dummy = next((o for o in room.objects if not o.name.lower().startswith('millenium eye')), None)
    assert dummy is not None
    room.player_pos = list(dummy.pos)

    # pick it up by exact name
    room.get(dummy.name, player)
    assert any(it.name == dummy.name for it in player.inventory)
    assert all(o.name != dummy.name for o in room.objects)

    # move to mine and ensure it cannot be picked up
    mr, mc = room.mine_pos
    room.player_pos = [mr, mc]
    room.get('mine', player)
    assert not any(it.name.lower() == 'mine' for it in player.inventory)


def test_super_hint_and_enter_loop(monkeypatch, capsys):
    random.seed(6)
    room = Room()
    # enter() itself calls reset_room, so we don't need to call it explicitly here
    player = make_player()

    inputs = ['hint', 'hint', 'hint', 'quit', 'y']

    def fake_input(prompt=''):
        return inputs.pop(0)

    monkeypatch.setattr(builtins, 'input', fake_input)
    res = room.enter(player)
    out = capsys.readouterr().out
    assert 'Super hint:' in out
    assert res == 'quit'


def test_grid_bounds_prevent_movement():
    random.seed(7)
    room = Room()
    player = make_player()
    room.player_pos = [0, 0]
    assert room.move('north', player) is None
    assert room.move('west', player) is None
    # place player at corner and try to move outside

    room.player_pos = [0, 0]

