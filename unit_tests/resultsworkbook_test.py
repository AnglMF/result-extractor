from ResultsWorkbook import ResultsWorkBook
from ranking.competitor import Competitor
from ranking.set import Set
from result_extractor import ResultExtractor
import unittest

class ResultsWorkbookTest(unittest.TestCase):
    mock_competitor1 = Competitor(1000, 'Archi', ["tourney1", "tourney2"])
    mock_competitor2 = Competitor(2000, 'Mang0', ["tourney1", "tourney2"])
    mock_set_data = {}
    mock_set_data['player1'] = "Archi"
    mock_set_data['player2'] = "Mang0"
    mock_set_data['player1_id'] = 1000
    mock_set_data['player2_id'] = 2000
    mock_set_data['score1'] = 3
    mock_set_data['score2'] = 0
    mock_set_data['seed1'] = 2
    mock_set_data['seed2'] = 1
    mock_set_data['winner'] = 1
    mock_set_data['set_id'] = 1234
    mock_set_data['tournament'] = "tourney1"
    mock_set_data['round'] = 1
    mock_set_entry = Set(mock_set_data, 'tourney1')
    mock_tournament_set_request = ResultExtractor()

    def test_a_initialize(self):
        self.mock_tournament_set_request.ranking.competitors[1000] = self.mock_competitor1
        self.mock_tournament_set_request.ranking.competitors[2000] = self.mock_competitor2
        self.mock_tournament_set_request.participants_dict[1000] = self.mock_competitor1
        self.mock_tournament_set_request.participants_dict[2000] = self.mock_competitor2
        self.mock_competitor1.register_placing('tourney1',
                                               {"placing": 1,
                                                "seed": 2})
        self.mock_competitor2.register_placing('tourney1',
                                               {"placing": 2,
                                                "seed": 1})
        self.mock_tournament_set_request.sets.register_set(self.mock_set_entry)
        self.mock_tournament_set_request.ranking.assign_set_history()
        self.mock_tournament_set_request.ranking.sort_by_avg_placing()

    def test_create_sample_workbook(self):
        participants_placings = []
        for participant in self.mock_tournament_set_request.ranking.competitors_sorted:
            participants_placings.append(participant.get_all_placings())
        file = ResultsWorkBook()
        file.create_spreadsheet(
            self.mock_tournament_set_request, 
            participants_placings, 
            ["tourney1", "tourney2"],
            "test")