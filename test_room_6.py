import pytest
from Room6_jason import *
from player import Player
from unittest.mock import call, patch


@pytest.fixture
def load_and_exit(mocker):
    mocker.patch('builtins.input', side_effect=["quit", "y"])
@pytest.fixture
def move_and_exit(mocker):
    mocker.patch('builtins.input', side_effect=["go east", "quit", "y"])
@pytest.fixture
def no_answers(mocker):
    mocker.patch('builtins.input', side_effect=["begin", "stop", "quit", "y"])
@pytest.fixture
def one_correct_answer(mocker):
    mocker.patch('builtins.input', side_effect=["begin", "dragon", "stop", "quit", "y"])

def describe_test_room_entry():
    def it_loads_the_correct_description_initially(load_and_exit):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        assert room.description == (
            "You find yourself in a well-illuminated room with a small wooden chest in the center\n"
            "A note on the chest reads \"Answer me these questions three, and rewards I will bestow upon ye\"\n"
            "There is a corridor to your east, a flight of stairs leading up, and a flight of stairs leading down"
        )
    def it_loads_the_correct_amount_of_questions(load_and_exit):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        assert room.questions == [
            "I guard my treasure day and night,\nScales like armor, breath of blight.\nBrave the fire if you dare\nWhat creature waits within its lair?", 
            "Born from stone, yet I walk as men.\nStrike me down, I rise again.\nSilent sentinel, carved with grace\nWhat stands watch in an ancient place?", 
            "I vanish in sunlight, appear in the gloam,\nA pathway to danger or to a new home.\nStep through my shimmer, your fate may unfold\nWhat am I, woven of magic untold?"
        ]
    def it_loads_the_correct_amount_of_answers(load_and_exit):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        assert room.answers == [
            ["dragon", "a dragon", "wyrm", "a wyrm"], 
            ["a golem", "golem"], 
            ["a portal", "portal", "a gate", "gate", "dimension door"]
        ]
    def it_loads_a_new_description_after_reentry(move_and_exit):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        room.enter(player)
        room.enter(player)
        assert room.description == "The light that filled this room has been snuffed out, and the chest is gone"
    def it_deletes_the_chest_after_reentry(move_and_exit):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        room.enter(player)
        room.enter(player)
        assert room.objects == []
def describe_riddling_functionality():
    def you_cannot_riddle_again_after_stopping(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "stop", "begin", "quit", "y"])
        room = Room()
        room.enter(player)
        captured = capsys.readouterr()
        assert "The chest is not accepting new answers" in captured.out
        assert room.has_riddled_previously == True
        assert room.objects[0].riddling_begun == False
    def you_cannot_riddle_again_after_failing(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "l", "l", "l", "l", "l", "begin", "quit", "y"])
        room = Room()
        room.enter(player)
        captured = capsys.readouterr()
        assert "The chest is not accepting new answers" in captured.out
        assert "The chest locks tight, it seems to be disappointed in you" in captured.out
        assert room.has_riddled_previously == True
        assert room.objects[0].riddling_begun == False
    def it_gives_no_reward_for_no_questions_answered(no_answers):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        room.enter(player)
        assert player.inventory == []
    def it_gives_no_reward_for_one_question_answered(mocker):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "dragon", "stop", "quit", "y"])
        room = Room()
        room.enter(player)
        assert player.inventory == []
    def it_gives_a_minor_reward_for_two_questions_answered(mocker):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "dragon", "golem", "stop", "quit", "y"])
        room = Room()
        room.enter(player)
        assert player.score == 20
        assert player.inventory != []
    def it_increases_player_health_after_answering_all_questions(mocker):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "dragon", "golem", "portal", "quit", "y"])
        room = Room()
        room.enter(player)
        assert player.health == 150
        assert player.score == 50
    def you_cannot_riddle_again_after_succeeding(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "dragon", "golem", "portal", "begin", "quit", "y"])
        room = Room()
        room.enter(player)
        captured = capsys.readouterr()
        assert "The chest is not accepting new answers" in captured.out
    def the_chest_deletes_itself_if_you_leave_mid_riddle(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["begin", "dragon", "golem", "go east", "go west", "begin", "quit", "y"])
        room = Room()
        room.enter(player)
        room.enter(player)
        captured = capsys.readouterr()
        assert room.has_entered_previously == True
        assert room.has_riddled_previously == False
        assert room.objects == []
        assert "You can't do that here. Try something else or type 'help' for options or 'hint' for a clue." in captured.out
    def the_major_reward_method_works_as_intended(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["quit", "y"])
        room = Room()
        room.enter(player)
        room.give_major_reward(player)
        captured = capsys.readouterr()
        assert room.objects[0].riddling_begun == False
        assert player.health == 150
        assert "The chest opens to reveal a holy orb within it, as you grasp it you find yourself feeling stronger" in captured.out
        assert "You gained 50 health" in captured.out
    def the_minor_reward_method_works_as_intended(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        mocker.patch('builtins.input', side_effect=["quit", "y"])
        room = Room()
        room.enter(player)
        room.give_minor_reward(player)
        captured = capsys.readouterr()
        assert room.objects[0].riddling_begun == False
        assert player.inventory != []
        assert "However, as you turn away in defeat, it shifts open and within there lies a strange potion" in captured.out
        assert "Congratulations, you received a healing potion" in captured.out        
def describe_misc_functionality():
    def the_chest_is_not_getable(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        mocker.patch('builtins.input', side_effect=["get chest", "quit", "y"])
        room.enter(player)
        captured = capsys.readouterr()
        assert "The Chest cannot be taken." in captured.out
        assert player.inventory == []
    def the_chest_instructs_how_to_start(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        mocker.patch('builtins.input', side_effect=["use chest", "quit", "y"])
        room.enter(player)
        captured = capsys.readouterr()
        assert "The chest awaits your answers to its riddles, type \"begin\" to start and \"stop\" to stop\n once you stop however, the chest may be sealed forever" in captured.out
    def it_prints_the_correct_hint(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        mocker.patch('builtins.input', side_effect=["hint", "quit", "y"])
        room.enter(player)
        captured = capsys.readouterr()
        assert "Answer the chest's riddles, but answer carefully for you have limited attempts" in captured.out
    def the_potion_is_not_accessible(mocker, capsys):
        player = Player(
            name="bobert",
            health=100,
            condition="healthy",
            current_room=0
        )
        room = Room()
        mocker.patch('builtins.input', side_effect=["get potion", "quit", "y"])
        room.enter(player)
        captured = capsys.readouterr()
        assert "potion is not here" in captured.out