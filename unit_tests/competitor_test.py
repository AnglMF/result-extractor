from competitor.competitor import Competitor
import unittest


class CompetitorTest(unittest.TestCase):
    player_id = 00000
    tournaments = ['tournament1', 'tournament2', 'tournament3', 'tournament4']
    mock_competitor = Competitor(player_id, 'Tag', tournaments)

    def test_return_no_attendance(self):
        placings = self.mock_competitor.get_placings()
        expected_placings = {'tournament1': '-', 'tournament2': '-', 'tournament3': '-', 'tournament4': '-'}
        assert expected_placings == placings

    def test_return_tournament_attendance(self):
        self.mock_competitor.register_placing('tournament1', 3)
        self.mock_competitor.register_placing('tournament3', 3)
        attendance = self.mock_competitor.get_attendance()
        assert attendance == 0.5
