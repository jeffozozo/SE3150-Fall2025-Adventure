import pytest
from Room11_ryan import Room, Cat
from player import Player
from object import Object

@pytest.fixture
def player():
    return Player(name="Test Adventurer", health=100, condition="healthy", current_room=11)

@pytest.fixture
def room():
    return Room()

def test_initial_state(room):
    assert len(room.objects) == 1
    assert room.objects[0].name == "Cat"
    assert room.objects[0].state == "worried"

def test_get_cat_fails(room, player):
    room.get("Cat", player)
    
    assert len(player.inventory) == 0
    assert len(room.objects) == 2

def test_solve_puzzle_receive_acorns(room, player):
    baby_cat = Object("Baby Cat", "A tiny kitten", True, "small", True)
    player.inventory.append(baby_cat)
    
    assert player.has_item("Baby Cat") is True
    room.use("Baby Cat", player)
    assert player.has_item("Baby Cat") is False
    assert player.has_item("Bag of Acorns") is True
    acorns = player.get_item("Bag of Acorns")
    assert acorns.description == "A sack filled with baby acorns"

def test_drop_item(room, player):
    sword = Object("Sword", "A sharp blade", True, "sharp", True)
    player.inventory.append(sword)
    
    room.drop("Sword", player)
    
    assert len(player.inventory) == 0
    
    item_in_room = room.get_item_from_object_list("Sword")
    assert item_in_room is not None
    assert item_in_room.name == "Sword"

def test_look_cat_description(room, player, capsys):
    room.look("cat", player)
    
    captured = capsys.readouterr()
    assert "body of a poptart" in captured.out
    assert "strangely pixelated" in captured.out

def test_invalid_move(room):
    result = room.move("west")
    assert result is None