from sets.set import Set
import unittest


class SetTest(unittest.TestCase):
    mock_set1_data_raw = {
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
                ],
                            "seeds": [
                                {"seedNum": 0}
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
                ],
                            "seeds": [
                                {"seedNum": 0}
                            ]
            }
            }
        ]
    }
    mock_set1_data = {}
    mock_set1_data['player1'] = mock_set1_data_raw["slots"][0]["entrant"]["participants"][0]["gamerTag"]
    mock_set1_data['player2'] = mock_set1_data_raw["slots"][1]["entrant"]["participants"][0]["gamerTag"]
    mock_set1_data['player1_id'] = mock_set1_data_raw["slots"][0]["entrant"]["participants"][0]["player"]["id"]
    mock_set1_data['player2_id'] = mock_set1_data_raw["slots"][1]["entrant"]["participants"][0]["player"]["id"]
    mock_set1_data['score1'] = mock_set1_data_raw["slots"][0]["standing"]["stats"]["score"]["value"]
    mock_set1_data['score2'] = mock_set1_data_raw["slots"][1]["standing"]["stats"]["score"]["value"]
    mock_set1_data['seed1'] = mock_set1_data_raw["slots"][0]["entrant"]["seeds"][0]["seedNum"]
    mock_set1_data['seed2'] = mock_set1_data_raw["slots"][1]["entrant"]["seeds"][0]["seedNum"]
    mock_set1_data['winner'] = mock_set1_data_raw["slots"][0]["standing"]["placement"]
    mock_set1_data['set_id'] = mock_set1_data_raw["id"]
    mock_set1_data['tournament'] = 'tournament1'
    mock_set1_data['round'] = abs(mock_set1_data_raw["round"])
    mock_set = Set(mock_set1_data, 'tournament1')

    def test_returns_players_list(self):
        assert self.mock_set.get_players() == [{2: 'BadPlayer'}, {1:'GoodPlayer'}]

    def test_assigns_correct_winner(self):
        assert self.mock_set.player1 == 'BadPlayer'

    def test_returns_dictionary_with_set_information(self):
        expected_dict_value = {"score1": 2, "winner": "BadPlayer", "score2": 0, 
                               "loser": "GoodPlayer", "round": 1, 
                               "tournament": "tournament1", "result": "expected",
                               "winner_id":2, "loser_id":1}
        self.assertEqual(expected_dict_value, self.mock_set.as_dict())

    def test_returns_set_round_with_no_sign(self):
        mock_set2_data_raw = {
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
                    ],
                            "seeds": [
                                {"seedNum": 0}
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
                        ],
                        "seeds": [
                            {"seedNum": 0}
                        ]
                }
                }
            ]
        }
        mock_set2_data = {}
        mock_set2_data['player1'] = mock_set2_data_raw["slots"][0]["entrant"]["participants"][0]["gamerTag"]
        mock_set2_data['player2'] = mock_set2_data_raw["slots"][1]["entrant"]["participants"][0]["gamerTag"]
        mock_set2_data['player1_id'] = mock_set2_data_raw["slots"][0]["entrant"]["participants"][0]["player"]["id"]
        mock_set2_data['player2_id'] = mock_set2_data_raw["slots"][1]["entrant"]["participants"][0]["player"]["id"]
        mock_set2_data['score1'] = mock_set2_data_raw["slots"][0]["standing"]["stats"]["score"]["value"]
        mock_set2_data['score2'] = mock_set2_data_raw["slots"][1]["standing"]["stats"]["score"]["value"]
        mock_set2_data['seed1'] = mock_set2_data_raw["slots"][0]["entrant"]["seeds"][0]["seedNum"]
        mock_set2_data['seed2'] = mock_set2_data_raw["slots"][1]["entrant"]["seeds"][0]["seedNum"]
        mock_set2_data['winner'] = mock_set2_data_raw["slots"][0]["standing"]["placement"]
        mock_set2_data['set_id'] = mock_set2_data_raw["id"]
        mock_set2_data['tournament'] = 'tournament1'
        mock_set2_data['round'] = abs(mock_set2_data_raw["round"])
        mock_set_negative_round = Set(mock_set2_data, 'tournament2')
        assert mock_set_negative_round.round == 3
