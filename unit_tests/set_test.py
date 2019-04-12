from sets.set import Set
import unittest


class SetTest(unittest.TestCase):
    mock_set_data = {
        "id": 1, "round": 1, "slots": [
            {
                "standing": {
                    "placement": 2, "stats": {
                        "score": {
                            "value": 0
                        }
                    }
                }, "entrant": {
                "participants": [
                    {
                        "player": {
                            "name": "GoodPlayer",
                            "id": 1
                        }
                    }
                ]
            }
            },
            {
                "standing": {
                    "placement": 1,
                    "stats": {
                        "score": {
                            "value": 2
                        }
                    }
                }, "entrant": {
                "participants": [
                    {
                        "player": {
                            "name": "BadPlayer",
                            "id": 2
                        }
                    }
                ]
            }
            }
        ]
    }
    mock_set = Set(mock_set_data)

    def test_returns_players_list(self):
        assert self.mock_set.get_players() == ['GoodPlayer', 'BadPlayer']

    def test_assigns_correct_winner(self):
        assert self.mock_set.winner == 'GoodPlayer'

    def test_returns_dictionary_with_set_information(self):
        expected_dict_value = {"score1": 3, "p1": "GoodPlayer", "score2": 1, "p2": "BadPlayer", "winner": "GoodPlayer",
                               "round": 1}
        assert self.mock_set.as_dict() == expected_dict_value
