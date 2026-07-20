from unittest.mock import patch
from engine import MatchEngine

@patch('engine.random.randint')
def test_random_choose(mock_randint):
    mock_randint.return_value = 4
    engine = MatchEngine()
    result = engine._winner_choose(attack=5,defence=5)

    assert result

    mock_randint.assert_called_once_with(1,10)

@patch('engine.random.randint')
def test_random_choose_edge_case(mock_randint):
    mock_randint.return_value = 4
    engine = MatchEngine()
    result = engine._winner_choose(attack=0,defence=0)

    assert result is False

    mock_randint.assert_not_called()

