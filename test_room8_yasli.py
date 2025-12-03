import pytest
from room8_yasli import Room, Dagger
from player import Player

@pytest.fixture
def player():
    return Player("TestPlayer", 100, "healthy", 8)

@pytest.fixture
def room():
    return Room()

def test_exits(room):
    assert "up" in room.exits
    assert "west" in room.exits
    assert "east" in room.exits

def test_dagger_exists(room):
    dagger = None
    for obj in room.objects:
        if obj.name == "Dagger":
            dagger = obj
    assert dagger is not None
    assert dagger.can_be_gotten == True


def test_altar_cannot_be_taken(room):
    altar = None
    for obj in room.objects:
        if obj.name == "Altar":
            altar = obj
    assert altar is not None
    assert altar.can_be_gotten == False


def test_blood_sacrifice(player, room):
    # Give player the dagger
    dagger = room.find_item("dagger")
    player.inventory.append(dagger)
    room.objects.remove(dagger)

    # Simulate offering blood
    room.offer_blood(player)
    assert player.health < 100
    assert "awakened" in player.condition
    assert room.altar.state == "active"