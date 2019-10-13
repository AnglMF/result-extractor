from graphqlclient import GraphQLClient
from sets.set import Set

import queries
import json


class Query:
    def __init__(self, token):
        self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
        self.client.inject_token('Bearer ' + token)

    def _post(self, body, variables):
        response = json.loads(self.client.execute(body, variables))
        if "errors" in response.keys():
            raise ValueError("There's an error with the query")
        return response

    def query_tournament_events(self, tournaments_list, event):
        request_body = queries.tournament_events_query()
        events_dict = {}
        for tournament in tournaments_list:
            response = self._post(request_body, {'tournamentName': tournament})
            for key, value in enumerate(response['data']['tournament']['events']):
                if event == value['name']:
                    events_dict[tournament] = value['id']
        if events_dict:
            return events_dict
        else:
            raise ValueError('Event {e} not found'.format(e=event))

    def query_event_standings(self, event):
        request_body = queries.event_standings_query()
        response = self._post(request_body, {'eventID': event})
        participants_standings_list = []
        total_participants = response['data']['event']['standings']['pageInfo']['total']
        for key, value in enumerate(response['data']['event']['standings']['nodes']):
            participant = {}
            participant['id'] = value["entrant"]["participants"][0]["playerId"]
            participant['name'] = value["entrant"]["participants"][0]["gamerTag"]
            participant['placement'] = value['placement']
            participants_standings_list.append(participant)
            del participant
        return participants_standings_list, total_participants

    def query_event_sets(self, tournament, event_id):
        page_number = 1
        per_page = 49
        sets_registered = 0
        request_body = queries.event_sets_query()
        sets = []
        event_sets = self._post(request_body, {"eventID": event_id,
                                               "page_number": page_number,
                                               "per_page": per_page})
        total_sets = event_sets["data"]["event"]["sets"]["pageInfo"]["total"]
        for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
            try:
                set_entry = Set(value, tournament)
                if self._is_dq(set_entry):
                    sets.append(set_entry)
                    del set_entry
            except TypeError:
                print('invalid set')
        sets_registered += per_page
        while not sets_registered > total_sets:
            page_number += 1
            event_sets = self._post(request_body, {"eventID": event_id,
                                                   "page_number": page_number,
                                                   "per_page": per_page})
            for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                set_entry = Set(value, tournament)
                if self._is_dq(set_entry):
                    sets.append(set_entry)
                    del set_entry
            sets_registered += per_page
        return sets

    def _is_dq(self, set):
        if set.score1 >= 0 and set.score2 >= 0:
            return True
        else:
            return False
