from sets.set import Set
from sets.set_history import SetHistory
import unittest


class SetHistoryTest(unittest.TestCase):
    mock_set1_data = {
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
                        "gamerTag": "GoodPlayer",
                        "player": [
                                {
                                    "id": 1
                                }
                        ]
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
                        "gamerTag": "GreatPlayer",
                        "player": [
                                {
                                    "id": 3
                                }
                        ]
                    }
                ]
            }
            }
        ]
    }
    mock_set2_data = {
        "id": 2, "round": 4, "slots": [
            {
                "standing": {
                    "placement": 1, "stats": {
                        "score": {
                            "value": 3
                        }
                    }
                }, "entrant": {
                "participants": [
                    {
                        "gamerTag": "GoodPlayer",
                        "player": [
                                {
                                    "id": 1
                                }
                        ]
                    }
                ]
            }
            },
            {
                "standing": {
                    "placement": 2,
                    "stats": {
                        "score": {
                            "value": 1
                        }
                    }
                }, "entrant": {
                "participants": [
                    {
                        "gamerTag": "BadPlayer",
                        "player": [
                                {
                                    "id": 2
                                }
                        ]
                    }
                ]
            }
            }
        ]
    }
    mock_set3_data = {
        "id": 3, "round": 2, "slots": [
            {
                "standing": {
                    "placement": 1, "stats": {
                        "score": {
                            "value": 3
                        }
                    }
                }, "entrant": {
                "participants": [
                    {
                        "gamerTag": "GoodPlayer",
                        "player": [
                                {
                                    "id": 1
                                }
                        ]
                    }
                ]
            }
            },
            {
                "standing": {
                    "placement": 2,
                    "stats": {
                        "score": {
                            "value": 0
                        }
                    }
                }, "entrant": {
                "participants": [
                    {
                        "gamerTag": "BadPlayer",
                        "player": [
                                {
                                    "id": 2
                                }
                        ]
                    }
                ]
            }
            }
        ]
    }
    mock_set1 = Set(mock_set1_data, 'tournament1')
    mock_set2 = Set(mock_set2_data, 'tournament2')
    mock_set3 = Set(mock_set3_data, 'tournament3')
    set_history = SetHistory('GoodPlayer')

    def test_correctly_register_set(self):
        try:
            self.set_history.register_set(self.mock_set1)
            self.set_history.register_set(self.mock_set2)
            self.set_history.register_set(self.mock_set3)
            assert True
        except ValueError:
            assert False

    def test_returns_sorted_sets_by_relevance(self):
        expected_value = [self.mock_set2.as_dict(), self.mock_set3.as_dict(), self.mock_set1.as_dict()]
        assert self.set_history.get_sets() == expected_value

    def test_returns_sets_vs_opponent(self):
        expected_value = [self.mock_set2.as_dict(), self.mock_set3.as_dict()]
        assert self.set_history.get_sets_vs('BadPlayer') == expected_value

    def test_returns_lost_sets(self):
        expected_value = [self.mock_set1.as_dict()]
        assert self.set_history.get_sets_lost() == expected_value

    def test_returns_error_when_calling_sets_vs_opponent_not_in_sets(self):
        try:
            self.set_history.get_sets_vs('non_existent_player')
        except ValueError:
            assert True

    def test_fails_when_invalid_set_registered(self):
        try:
            self.set_history.register_set(8)
        except ValueError:
            assert True

    def test_returns_list_of_set_dictionares(self):
        expected_value = [
            {"score1": 3, "p1": "GoodPlayer", "score2": 1, "p2": "BadPlayer", "winner": "GoodPlayer",
            "round": 4, "tournament": "tournament2"},
            {"score1": 3, "p1": "GoodPlayer", "score2": 0, "p2": "BadPlayer", "winner": "GoodPlayer",
            "round": 2, "tournament": "tournament3"},
            {"score1": 0, "p1": "GoodPlayer", "score2": 2, "p2": "GreatPlayer", "winner": "GreatPlayer",
            "round": 1, "tournament": "tournament1"}
        ]
        self.assertEqual(expected_value, self.set_history.get_sets())

    def test_get_correct_win_percentage(self):
        assert self.set_history.get_win_percentage() == 2/3

