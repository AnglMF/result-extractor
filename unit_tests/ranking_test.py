from ranking import Ranking
from ranking.competitor import Competitor
from ranking.set import Set
import unittest


class RankingTest(unittest.TestCase):
    mock_tournaments = ['t1', 't2', 't3', 't4', 't5']
    mock_ranking = Ranking()
    mock_competitor1 = Competitor(1000, 'player1', mock_tournaments)
    mock_competitor2 = Competitor(2000, 'player2', mock_tournaments)
    mock_competitor3 = Competitor(3000, 'player3', mock_tournaments)
    mock_competitor4 = Competitor(4000, 'player4', mock_tournaments)
    mock_competitor5 = Competitor(5000, 'player5', mock_tournaments)
    mock_competitor1.register_placing('t1', {'placing': 1, 'seed': 1})
    mock_competitor1.register_placing('t2', {'placing': 1, 'seed': 1})
    mock_competitor1.register_placing('t3', {'placing': 3, 'seed': 3})
    mock_competitor1.register_placing('t4', {'placing': 1, 'seed': 1})
    mock_competitor1.register_placing('t5', {'placing': 1, 'seed': 1})
    mock_competitor2.register_placing('t1', {'placing': 2, 'seed': 2})
    mock_competitor2.register_placing('t2', {'placing': 7, 'seed': 7})
    mock_competitor2.register_placing('t3', {'placing': 5, 'seed': 5})
    mock_competitor2.register_placing('t4', {'placing': 7, 'seed': 7})
    mock_competitor2.register_placing('t5', {'placing': 3, 'seed': 3})
    mock_competitor3.register_placing('t1', {'placing': 3, 'seed': 3})
    mock_competitor3.register_placing('t4', {'placing': 2, 'seed': 2})
    mock_competitor3.register_placing('t5', {'placing': 2, 'seed': 2})
    mock_competitor4.register_placing('t1', {'placing': 5, 'seed': 5})
    mock_competitor4.register_placing('t3', {'placing': 1, 'seed': 1})
    mock_competitor4.register_placing('t4', {'placing': 7, 'seed': 7})
    mock_competitor4.register_placing('t5', {'placing': 9, 'seed': 9})
    mock_competitor5.register_placing('t5', {'placing': 2, 'seed': 2})
    mock_ranking.competitors[mock_competitor1.id] = mock_competitor1
    mock_ranking.competitors[mock_competitor2.id] = mock_competitor2
    mock_ranking.competitors[mock_competitor3.id] = mock_competitor3
    mock_ranking.competitors[mock_competitor4.id] = mock_competitor4
    mock_ranking.competitors[mock_competitor5.id] = mock_competitor5

    mock_set1_data_raw = {
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
                            "gamerTag": "player1",
                            "player": {
                                "id": 1000
                            }
                        }
                    ],
                    "seeds": [{"seedNum": 0}]
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
                            "gamerTag": "player2",
                            "player": {
                                "id": 2000
                            }
                        }
                    ],
                    "seeds": [{"seedNum": 0}]
                }
            }
        ]
    }
    mock_set2_data_raw = {
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
                            "gamerTag": "player1",
                            "player": {
                                "id": 1000
                            }
                        }
                    ],
                    "seeds": [{"seedNum": 0}]
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
                            "gamerTag": "player3",
                            "player": {
                                "id": 3000
                            }
                        }
                    ],
                    "seeds": [{"seedNum": 0}]
                }
            }
        ]
    }
    mock_set3_data_raw = {
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
                            "gamerTag": "player3",
                            "player": {
                                "id": 3000
                            }
                        }
                    ],
                    "seeds": [{"seedNum": 0}]
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
                            "gamerTag": "player4",
                            "player": {
                                "id": 4000
                            }
                        }
                    ],
                    "seeds": [{"seedNum": 0}]
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
    mock_set3_data = {}
    mock_set3_data['player1'] = mock_set3_data_raw["slots"][0]["entrant"]["participants"][0]["gamerTag"]
    mock_set3_data['player2'] = mock_set3_data_raw["slots"][1]["entrant"]["participants"][0]["gamerTag"]
    mock_set3_data['player1_id'] = mock_set3_data_raw["slots"][0]["entrant"]["participants"][0]["player"]["id"]
    mock_set3_data['player2_id'] = mock_set3_data_raw["slots"][1]["entrant"]["participants"][0]["player"]["id"]
    mock_set3_data['score1'] = mock_set3_data_raw["slots"][0]["standing"]["stats"]["score"]["value"]
    mock_set3_data['score2'] = mock_set3_data_raw["slots"][1]["standing"]["stats"]["score"]["value"]
    mock_set3_data['seed1'] = mock_set3_data_raw["slots"][0]["entrant"]["seeds"][0]["seedNum"]
    mock_set3_data['seed2'] = mock_set3_data_raw["slots"][1]["entrant"]["seeds"][0]["seedNum"]
    mock_set3_data['winner'] = mock_set3_data_raw["slots"][0]["standing"]["placement"]
    mock_set3_data['set_id'] = mock_set3_data_raw["id"]
    mock_set3_data['tournament'] = 'tournament1'
    mock_set3_data['round'] = abs(mock_set3_data_raw["round"])
    mock_set1 = Set(mock_set1_data, 't1')
    mock_set2 = Set(mock_set2_data, 't2')
    mock_set3 = Set(mock_set3_data, 't2')

    def test_returns_sorted_list_by_average_placing(self):
        self.mock_ranking.sort_by_avg_placing()
        expected_list = [self.mock_competitor1,
                         self.mock_competitor3,
                         self.mock_competitor2,
                         self.mock_competitor4]
        self.assertEqual(self.mock_ranking.competitors_sorted, expected_list)

    def test_removes_low_attendance_players_from_competitor_list(self):
        self.mock_ranking.set_assistance_requirement(tournament_number=2)
        expected_dict = {1000: self.mock_competitor1,
                         2000: self.mock_competitor2,
                         3000: self.mock_competitor3,
                         4000: self.mock_competitor4}
        assert self.mock_ranking.competitors == expected_dict

    def test_registers_set_for_players(self):
        self.mock_ranking.total_sets.register_set(self.mock_set1)
        self.mock_ranking.total_sets.register_set(self.mock_set2)
        self.mock_ranking.total_sets.register_set(self.mock_set3)
        self.mock_ranking.assign_set_history()
        self.mock_ranking.competitors[1000].sets.get_sets()
        expected_list = [self.mock_set2.as_dict(), self.mock_set1.as_dict()]
        assert self.mock_ranking.competitors[1000].sets.get_sets() == expected_list

    def test_z_merge_players(self):
        self.mock_ranking.merge_players(["player2", "player5"], "player1")
        assert (self.mock_competitor5.id not in self.mock_ranking.competitors.keys()) and (
            self.mock_competitor2.id not in self.mock_ranking.competitors.keys()
        )
