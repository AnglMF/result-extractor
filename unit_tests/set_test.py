from sets.set import Set
import unittest


class SetTest(unittest.TestCase):
    mock_set_data = {
        "id": 1, "round": 1, "slots": [
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
                        "gamerTag": "GoodPlayer",
                        "player": {
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
                        "gamerTag": "BadPlayer",
                        "player": {
                            "id": 2
                        }
                    }
                ]
            }
            }
        ]
    }
    mock_set = Set(mock_set_data, 'tournament1')

    def test_returns_players_list(self):
        assert self.mock_set.get_players() == ['BadPlayer', 'GoodPlayer']

    def test_assigns_correct_winner(self):
        assert self.mock_set.player1 == 'BadPlayer'

    def test_returns_dictionary_with_set_information(self):
        expected_dict_value = {"score1": 2, "winner": "BadPlayer", "score2": 0, "loser": "GoodPlayer",
                               "round": 1, "tournament": "tournament1"}
        self.assertEqual(expected_dict_value, self.mock_set.as_dict())

    def test_returns_set_round_with_no_sign(self):
        mock_set_data = {
            "id": 1, "round": -3, "slots": [
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
                            "player": {
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
                            "gamerTag": "BadPlayer",
                            "player": {
                                "id": 2
                            }
                        }
                    ]
                }
                }
            ]
        }
        mock_set_negative_round = Set(mock_set_data, 'tournament2')
        assert mock_set_negative_round.round == 3
