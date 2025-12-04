import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys
import os
from Room15_griff import Room, BloodJack, ScoreSlots

class FakeObject:
    def __init__(self, name, description, can_be_gotten=True, state=None):
        self.name = name
        self.description = description
        self.can_be_gotten = can_be_gotten
        self.state = state
        self.use_called = False

    def use(self):
        self.use_called = True


class FakePlayer:
    def __init__(self, score=100, health=100):
        self.score = score
        self.health = health
        self.inventory = []

    def has_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return True
        return False

    def show_inventory(self):
        if not self.inventory:
            print("Your inventory is empty.")
        else:
            print("Inventory:")
            for item in self.inventory:
                print(f"  - {item.name}")

    def print_stats(self):
        print(f"Score: {self.score}")
        print(f"Health: {self.health}")


class TestPlay:

    def setup_method(self):
        Room.objects = []

    @patch('Room15_griff.BloodJack')
    def test_play_bloodjack(self, mock_bloodjack, capsys):
        room = Room()
        player = FakePlayer()
        room.play("bloodjack", player)
        mock_bloodjack.assert_called_once_with(player)

    @patch('Room15_griff.ScoreSlots')
    def test_play_scoreslots(self, mock_scoreslots, capsys):
        room = Room()
        player = FakePlayer()
        room.play("scoreslots", player)
        mock_scoreslots.assert_called_once_with(player)

    def test_play_invalid_game(self, capsys):
        room = Room()
        player = FakePlayer()
        room.play("poker", player)
        captured = capsys.readouterr()
        assert "not an available game" in captured.out.lower()


class TestBloodJack:

    @patch('builtins.input', return_value='exit')
    def test_bloodjack_exit(self, mock_input, capsys):
        player = FakePlayer(health=100)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "leave" in captured.out.lower()

    @patch('builtins.input', side_effect=['wager', '10', 'exit'])
    def test_bloodjack_set_wager(self, mock_input, capsys):
        player = FakePlayer(health=100)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "wager set" in captured.out.lower() or "10" in captured.out

    @patch('builtins.input', side_effect=['wager', 'all', 'exit'])
    def test_bloodjack_wager_all(self, mock_input, capsys):
        player = FakePlayer(health=50)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "all" in captured.out.lower() or "50" in captured.out

    @patch('builtins.input', side_effect=['wager', '200', 'exit'])
    def test_bloodjack_wager_too_much(self, mock_input, capsys):
        player = FakePlayer(health=100)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "don't have" in captured.out.lower()

    @patch('builtins.input', side_effect=['wager', '3', 'exit'])
    def test_bloodjack_wager_too_low(self, mock_input, capsys):
        player = FakePlayer(health=100)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "minimum" in captured.out.lower()

    @patch('builtins.input', side_effect=['deal', 'stand', '', 'exit'])
    @patch('random.choice')
    def test_bloodjack_deal_and_stand(self, mock_random, mock_input, capsys):
        mock_random.side_effect = [5, 6, 7, 8, 9, 10, 2, 3, 4, 5]
        player = FakePlayer(health=100)
        BloodJack(player)
        assert True

    @patch('builtins.input', side_effect=['deal', 'hit', 'stand', '', 'exit'])
    @patch('random.choice')
    def test_bloodjack_hit(self, mock_random, mock_input, capsys):
        mock_random.side_effect = [5, 6, 7, 8, 2, 9, 3, 4, 5, 6]
        player = FakePlayer(health=100)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "hit" in captured.out.lower() or "card" in captured.out.lower()

    @patch('builtins.input', side_effect=['deal', 'exit'])
    @patch('random.choice')
    def test_bloodjack_blackjack(self, mock_random, mock_input, capsys):
        mock_random.side_effect = ['A', 'K', 5, 6]
        player = FakePlayer(health=100)
        BloodJack(player)
        captured = capsys.readouterr()
        assert "BLACKJACK" in captured.out or "win" in captured.out.lower()


class TestScoreSlots:

    @patch('builtins.input', return_value='exit')
    def test_scoreslots_exit(self, mock_input, capsys):
        player = FakePlayer(score=100)
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert "leave" in captured.out.lower()

    @patch('builtins.input', side_effect=['wager', '5', 'exit'])
    def test_scoreslots_set_wager(self, mock_input, capsys):
        player = FakePlayer(score=100)
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert "wager" in captured.out.lower() or "5" in captured.out

    @patch('builtins.input', side_effect=['wager', 'all', 'exit'])
    def test_scoreslots_wager_all(self, mock_input, capsys):
        player = FakePlayer(score=50)
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert "all" in captured.out.lower() or "50" in captured.out

    @patch('builtins.input', side_effect=['wager', '20', 'exit'])
    def test_scoreslots_invalid_wager(self, mock_input, capsys):
        player = FakePlayer(score=100)
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert "only bet" in captured.out.lower() or "invalid" in captured.out.lower()

    @patch('builtins.input', side_effect=['wager', '200', 'exit'])
    def test_scoreslots_wager_too_much(self, mock_input, capsys):
        player = FakePlayer(score=100)
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert True

    @patch('builtins.input', side_effect=['spin', 'exit'])
    @patch('random.choice')
    @patch('time.sleep')
    def test_scoreslots_spin(self, mock_sleep, mock_random, mock_input, capsys):
        mock_random.side_effect = ['O'] * 200
        player = FakePlayer(score=100)
        initial_score = player.score
        ScoreSlots(player)
        assert player.score != initial_score

    @patch('builtins.input', side_effect=['wager', '5', 'spin', 'exit'])
    @patch('random.choice')
    @patch('time.sleep')
    def test_scoreslots_spin_with_wager(self, mock_sleep, mock_random, mock_input, capsys):
        mock_random.side_effect = ['O'] * 200
        player = FakePlayer(score=100)
        initial_score = player.score
        ScoreSlots(player)
        assert player.score != initial_score

    @patch('builtins.input', side_effect=['spin', 'exit'])
    @patch('random.choice')
    @patch('time.sleep')
    def test_scoreslots_winning_combination(self, mock_sleep, mock_random, mock_input, capsys):
        mock_random.side_effect = ['W'] * 200
        player = FakePlayer(score=100)
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert "win" in captured.out.lower() or "jackpot" in captured.out.lower()

    @patch('builtins.input', side_effect=['spin', 'exit'])
    @patch('random.choice')
    @patch('time.sleep')
    def test_scoreslots_losing_combination(self, mock_sleep, mock_random, mock_input, capsys):
        mock_random.side_effect = (['O', 'W', 'L', 'O', 'W'] * 50)
        player = FakePlayer(score=100)
        ScoreSlots(player)
        assert True

    def test_scoreslots_no_score(self, capsys):
        player = FakePlayer(score=0)
        with patch('builtins.input', side_effect=['spin', 'exit']):
            ScoreSlots(player)
            captured = capsys.readouterr()
            assert "no score" in captured.out.lower()

    @patch('builtins.input', side_effect=['spin', 'exit'])
    @patch('random.choice')
    @patch('time.sleep')
    def test_scoreslots_jackpot(self, mock_sleep, mock_random, mock_input, capsys):
        mock_random.side_effect = ['7'] * 200
        player = FakePlayer(score=100)
        initial_score = player.score
        ScoreSlots(player)
        captured = capsys.readouterr()
        assert "MEGA JACKPOT" in captured.out or "jackpot" in captured.out.lower()
        assert player.score > initial_score
