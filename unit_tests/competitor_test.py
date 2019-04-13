from competitor.competitor import Competitor
from sets.set import Set
import unittest


class CompetitorTest(unittest.TestCase):
    player_id = 00000
    tournaments = ['tournament1', 'tournament2', 'tournament3', 'tournament4']
    mock_competitor = Competitor(player_id, 'Tag', tournaments)
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
                            "name": "GreatPlayer",
                            "id": 3
                        }
                    }
                ]
            }
            }
        ]
    }
    mock_set1 = Set(mock_set1_data, 'tournament1')

    def test_return_attendance(self):
        placings = self.mock_competitor.placings
        expected_placings = {'tournament1': 3, 'tournament2': '-', 'tournament3': 1, 'tournament4': '-'}
        assert expected_placings == placings

    def test_calculates_average_placing_correctly(self):
        self.mock_competitor.register_placing('tournament1', 3)
        self.mock_competitor.register_placing('tournament3', 1)
        assert self.mock_competitor.get_avg_placing() == 2

    def test_return_tournament_attendance(self):
        attendance = self.mock_competitor.assistance_percentage
        assert attendance == 50

    def test_register_competitor_set(self):
        self.mock_competitor.register_set(self.mock_set1)
        assert True

    def test_return_empty_list_for_not_found_sets(self):
        assert self.mock_competitor.sets('won') == []

    def test_return_list_with_sets_found(self):
        assert self.mock_competitor.sets('vs', opponent='GreatPlayer') == [self.mock_set1.as_dict()]

    def test_fails_when_invalid_option_on_set_request(self):
        try:
            self.mock_competitor.sets('invalid_option')
        except ValueError:
            assert True

