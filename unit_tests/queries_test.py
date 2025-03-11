from urllib.error import HTTPError
from queries.queries import start_gg, challonge_client
from requests.exceptions import HTTPError as req_error
import unittest
import json
import os


class StartGGTest(unittest.TestCase):
    with open ("credentials.json", "r") as file:
        credentials = json.load(file)
    start_gg_client = start_gg(credentials['start_gg'])

    # test for invalid token
    def test_fails_when_invalid_token_injected(self):
        bad_client = start_gg('token')
        try:
            bad_client.query_tournament_events(['a', 'b', 'c'], 'smush')
        except HTTPError:
            assert True

    # test for error on query
    def test_raises_error_when_bad_query(self):
        bad_query = 'henlo uwu'
        try:
            self.start_gg_client._post(bad_query, {})
        except ValueError:
            assert True

    def test_returns_dict_of_events_found(self):
        tournament_list = ['xtr-ultimate-tournament']
        event = ['Smash Ultimate Singles']
        expected_dict = {'xtr-ultimate-tournament': {'id': 294000, 'platform': 'start gg'}}
        actual_list = self.start_gg_client.query_tournament_events(tournament_list, event)
        self.assertEqual(expected_dict, actual_list)

    def test_returns_event_participants_info(self):
        participants, total_participants = self.start_gg_client.query_event_standings(294000)
        if participants:
            self.assertEqual(118, total_participants)
        else:
            assert False

    def test_query_event_sets_returns_non_empty_list(self):
        sets_list = self.start_gg_client.query_event_sets('xtr-ultimate-tournament', 294000)
        if sets_list:
            assert True

class ChallongeTest(unittest.TestCase):

    with open ("credentials.json", "r") as file:
        credentials = json.load(file)
    api = challonge_client(credentials["challonge_user"],
                        credentials["challonge"])
        

    # test for invalid token
    def test_fails_when_invalid_token_injected(self):
        bad_client = challonge_client('user', 'token')
        bad_client.query_tournament_events(['a', 'b', 'c'])
        self.assertRaises(req_error)

    def test_gets_tournament_names(self):
        tournament_list = ['2cn4e1j2', 'c2y4rrw3']
        response = self.api.query_tournament_events(tournament_list)
        expected = {"unfinished tournament": '2cn4e1j2', "Test tournament": '2cn4e1j2'}
        self.assertEqual(response, expected)

    def test_returns_event_participants_info(self):
        participants, total_participants = self.api.query_event_standings('2cn4e1j2')
        if participants:
            self.assertEqual(len(participants), 4)
        else:
            assert False

    def test_query_event_sets_returns_non_empty_list(self):
        sets_list = self.api.query_event_sets('unfinished tournament', '2cn4e1j2')
        if sets_list:
            assert True
