from ranking.competitor import Competitor
from ranking.competitor import calculate_performance
from ranking.set import Set
import unittest
unittest.TestLoader.sortTestMethodsUsing=None


class CompetitorTest(unittest.TestCase):
    player_id = 00000
    tournaments = ['tournament1', 'tournament2', 'tournament3', 
                   'tournament4', 'tournament5']
    mock_competitor = Competitor(player_id, 'GoodPlayer', tournaments)
    mock_competitor_great = Competitor(player_id, 'GreatPlayer', tournaments)
    mock_competitor_copy = Competitor(player_id, 'Tag_copy', ['tournament1', 
                                                              'tournament2', 
                                                              'tournament3', 
                                                              'tournament4', 
                                                              'tournament5'])
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
                            "gamerTag": "GoodPlayer",
                            "player": {
                                "id": 1
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
                            "gamerTag": "GreatPlayer",
                            "player": {
                                "id": 3
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
    print(mock_set1_data)
    mock_set1 = Set(mock_set1_data, 'tournament1')

    def test_return_attendance(self):
        placings = self.mock_competitor.placings
        expected_placings = {'tournament1': {'placing': 3, 'seed': 3}, 
                             'tournament2': {'placing': '-','seed': '-'},
                             'tournament3': {'placing': 1, 'seed': 1}, 
                             'tournament4': {'placing': '-','seed': '-'},
                             'tournament5': {'placing': '-','seed': '-'}
        }
        assert expected_placings == placings

    def test_calculates_average_placing_correctly(self):
        self.mock_competitor.register_placing('tournament1', {'placing': 3, 'seed': 3})
        self.mock_competitor.register_placing('tournament3', {'placing': 1, 'seed': 1})
        assert self.mock_competitor.average == 2

    def test_return_tournament_attendance(self):
        attendance = self.mock_competitor.assistance_percentage
        assert attendance == (2/5*100)

    def test_return_h2h_for_player_with_gamertag(self):
        expected = '0-1'
        result = self.mock_competitor.record_vs("GreatPlayer")
        self.assertEqual(result, expected)

    def test_return_h2h_for_player_with_competitor_obj(self):
        expected = '0-1'
        result = self.mock_competitor.record_vs(self.mock_competitor_great)
        self.assertEqual(result, expected)

    def test_return_games_h2h_for_player_with_gamertag(self):
        expected = '0-2'
        result = self.mock_competitor.record_vs_games("GreatPlayer")
        self.assertEqual(result, expected)

    def test_return_games_h2h_for_player_with_competitor_obj(self):
        expected = '0-2'
        result = self.mock_competitor.record_vs_games(self.mock_competitor_great)
        self.assertEqual(result, expected)

    def test_register_competitor_set(self):
        self.mock_competitor.register_set(self.mock_set1)
        assert True

    def test_return_empty_list_for_not_found_sets(self):
        self.assertEqual(self.mock_competitor.sets.get_sets_won(),[])

    def test_return_list_with_sets_found(self):
        assert self.mock_competitor.sets.get_sets_vs(Competitor(3,'GreatPlayer',['tournament'])) == [self.mock_set1.as_dict()]

    def test_calculate_performance_results(self):
        assert calculate_performance(9, 7) == '+1'

    def test_z_fuse_participant(self):
        self.mock_competitor_copy.register_placing('tournament5', {'placing': 5, 'seed': 1})
        self.mock_competitor.combine_data(self.mock_competitor_copy)
        attendance = self.mock_competitor.average
        assert attendance == 3
