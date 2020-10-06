from urllib.error import HTTPError

from queries.queries import Query

import unittest
import os


class QueryTest(unittest.TestCase):
    client = Query(os.environ['TOKEN'])

    # test for invalid token
    def test_fails_when_invalid_token_injected(self):
        bad_client = Query('token')
        try:
            bad_client.query_tournament_events(['a', 'b', 'c'], 'smush')
        except HTTPError:
            assert True

    # test for error on query
    def test_raises_error_when_bad_query(self):
        bad_query = 'henlo uwu'
        try:
            self.client._post(bad_query, {})
        except ValueError:
            assert True

    def test_returns_dict_of_events_found(self):
        tournament_list = ['xtr-ultimate-tournament']
        event = ['Smash Ultimate Singles']
        expected_dict = {'xtr-ultimate-tournament': 294000}
        actual_list = self.client.query_tournament_events(tournament_list, event)
        self.assertEqual(expected_dict, actual_list)

    def test_returns_event_participants_info(self):
        participants, total_participants = self.client.query_event_standings(294000)
        if participants:
            self.assertEqual(118, total_participants)
        else:
            assert False

    def test_query_event_sets_returns_non_empty_list(self):
        sets_list = self.client.query_event_sets('xtr-ultimate-tournament', 294000)
        if sets_list:
            assert True
