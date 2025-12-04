from Room10_drew import Room
from player import Player
from object import Object
import pytest


@pytest.fixture
def player():
    return Player("drew", 100, "good", 10)


@pytest.fixture
def room():
    Room.objects = []
    return Room()


@pytest.fixture
def acorns():
    return Object("bag of acorns", "", True, True, True)


def test_correct_objects_exist_at_start(room):
    names = [obj.name for obj in room.objects]
    assert "mass of darkness" in names
    assert "Baby Cat" in names


def test_moving_in_each_direction_works(room):
    assert room.move("north") == None
    assert room.move("south") == "south"
    assert room.move("east") == None
    assert room.move("west") == "west"


def test_gives_reward_when_given_acorns(room, player, acorns):
    player.inventory.append(acorns)
    room.use("bag of acorns", player)

    assert acorns not in player.inventory
    assert room.darkness not in room.objects


def test_quest_gets_accepted_when_talking_for_first_time(room, player):
    assert room.quest_accepted == False
    room.look("mass of darkness", player)
    assert room.quest_accepted == True


def test_cant_accept_quest_if_already_completed(room, player, acorns):
    player.inventory.append(acorns)
    room.use("bag of acorns", player)

    assert room.quest_accepted == False
    room.look("mass of darkness", player)
    assert room.quest_accepted == False


def test_get_baby_cat(room, player):
    room.get("baby cat", player)
    print([obj.name for obj in room.objects])
    assert room.baby_cat not in room.objects
    assert room.baby_cat in player.inventory
