from resultExtractor import Ranking
from competitor.competitor import Competitor
from sets.set import Set
import unittest


class RankingTest(unittest.TestCase):
    mock_tournaments = ['t1', 't2', 't3', 't4', 't5']
    mock_ranking = Ranking()
    mock_competitor1 = Competitor(1, 'player1', mock_tournaments)
    mock_competitor2 = Competitor(1, 'player2', mock_tournaments)
    mock_competitor3 = Competitor(1, 'player3', mock_tournaments)
    mock_competitor4 = Competitor(1, 'player4', mock_tournaments)
    mock_competitor5 = Competitor(1, 'player5', mock_tournaments)
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
    mock_ranking.competitors.append(mock_competitor1)
    mock_ranking.competitors.append(mock_competitor2)
    mock_ranking.competitors.append(mock_competitor3)
    mock_ranking.competitors.append(mock_competitor4)
    mock_ranking.competitors.append(mock_competitor5)

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
                            "gamerTag": "player1",
                            "playerId": 1
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
                            "gamerTag": "player2",
                            "playerId": 3
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
                            "gamerTag": "player1",
                            "playerId": 1
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
                            "gamerTag": "player3",
                            "playerId": 3
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
                            "gamerTag": "player3",
                            "playerId": 1
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
                            "gamerTag": "player4",
                            "playerId": 2
                        }
                    ]
                }
            }
        ]
    }
    mock_set1 = Set(mock_set1_data, 't1')
    mock_set2 = Set(mock_set2_data, 't2')
    mock_set3 = Set(mock_set3_data, 't2')

    def test_returns_sorted_list_by_average_placing(self):
        expected_list = [self.mock_competitor1.get_all_placings(),
                         self.mock_competitor3.get_all_placings(),
                         self.mock_competitor2.get_all_placings(),
                         self.mock_competitor4.get_all_placings()]
        assert self.mock_ranking.get() == expected_list

    def test_removes_low_attendance_players_from_competitor_list(self):
        self.mock_ranking.set_assistance_requirement(tournament_number=2)
        expected_list = [self.mock_competitor1.get_all_placings(),
                         self.mock_competitor3.get_all_placings(),
                         self.mock_competitor2.get_all_placings(),
                         self.mock_competitor4.get_all_placings()]
        assert self.mock_ranking.get() == expected_list

    def test_registers_set_for_players(self):
        self.mock_ranking.total_sets.register_set(self.mock_set1)
        self.mock_ranking.total_sets.register_set(self.mock_set2)
        self.mock_ranking.total_sets.register_set(self.mock_set3)
        self.mock_ranking.assign_set_history_for_top_players(15)
        expected_list = [self.mock_set2.as_dict(), self.mock_set1.as_dict()]
        assert self.mock_ranking.competitors[0].sets('all') == expected_list
