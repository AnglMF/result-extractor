import unittest
import json
from resultExtractor import TournamentSetsRequest


class TestTournamentRequest(unittest.TestCase):
    def test_tournament_events_returns_valid_response_for_existing_tournament(self):

        tournament_events_query = '''
        query TournamentQuery($tournamentName: String) {
            tournament(slug: $tournamentName){
              id
              name
            events {
                id
                name
              }
            }
          }
        '''

        query_variables = '{"tournamentName": "xtr-ultimate-tournament"}'
        obj = TournamentSetsRequest()
        response = obj._post( 'test_request', tournament_events_query, query_variables)

        expected_response = json.loads('{"data":{"tournament":{"id":128094,"name":"XTR Ultimate Tournament","events":[' \
                            '{"id":294000,"name":"Smash Ultimate Singles"},{"id":294007,' \
                            '"name":"Smash Ultimate Dobles"}]}},"extensions":{"queryComplexity":3},' \
                            '"actionRecords":[]}')

        self.assertEqual(response, expected_response)

    def test_tournament_events_returns_null_tournament_for_nonexistent_tournament(self):

        tournament_events_query = '''
        query TournamentQuery($tournamentName: String) {
            tournament(slug: $tournamentName){
              id
              name
            events {
                id
                name
              }
            }
          }
        '''

        query_variables = '{"tournamentName": "non-existent-tournament"}'
        obj = TournamentSetsRequest()
        response = obj._post( 'test_request', tournament_events_query, query_variables)

        expected_response = {'data': {'tournament': None}, 'extensions': {'queryComplexity': 1}, 'actionRecords': []}

        self.assertEqual(expected_response, response)

# good result '{"data":{"tournament":{"id":128094,"name":"XTR Ultimate Tournament","events":[{"id":294000,"name":"Smash Ultimate Singles"},{"id":294007,"name":"Smash Ultimate Dobles"}]}},"extensions":{"queryComplexity":3},"actionRecords":[]}'
# no tournament '{"data":{"tournament":null},"extensions":{"queryComplexity":1},"actionRecords":[]}'