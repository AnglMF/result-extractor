from graphqlclient import GraphQLClient
from sets.set import Set
from datetime import datetime, timedelta
from time import sleep

import queries
import json


def is_dq(_set):
    if _set.score1 >= 0 and _set.score2 >= 0:
        return True
    else:
        return False


class Query:
    def __init__(self, token):
        self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
        self.client.inject_token('Bearer ' + token)
        self.last_request = datetime.now()
        self.next_request = datetime.now()

    def _post(self, body, variables):
        if (self.next_request-datetime.now()).total_seconds() > 0:
            sleep((self.next_request-datetime.now()).total_seconds())
        self.next_request = datetime.now() + timedelta(seconds=1, milliseconds=333)
        response = json.loads(self.client.execute(body, variables))
        if "errors" in response.keys():
            raise ValueError("There's an error with the query")
        return response

    def query_tournament_events(self, tournaments_list, events):
        request_body = queries.tournament_events_query()
        events_dict = {}
        for tournament in tournaments_list:
            response = self._post(request_body, {'tournamentName': tournament})
            try:
                for key, value in enumerate(response['data']['tournament']['events']):
                    for event in events:
                        if event == value['name']:
                            events_dict[tournament] = value['id']
            except TypeError:
                print("Tournament doesn't exist: {t}".format(t=tournament))
        if events_dict:
            return events_dict
        else:
            raise ValueError('Event {e} not found'.format(e=events))

    def query_event_standings(self, event):
        request_body = queries.event_standings_query()
        response = self._post(request_body, {'eventID': event})
        participants_standings_list = []
        total_participants = response['data']['event']['standings']['pageInfo']['total']
        for key, value in enumerate(response['data']['event']['standings']['nodes']):
            participant = {}
            participant['id'] = value["entrant"]["participants"][0]["player"]["id"]
            participant['name'] = value["entrant"]["participants"][0]["gamerTag"]
            participant['placement'] = value['placement']
            participant['seed'] = value["entrant"]["seeds"][0]["seedNum"]
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
        try:
            total_sets = event_sets["data"]["event"]["sets"]["pageInfo"]["total"]
            for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                try:
                    set_entry = Set(value, tournament)
                    if is_dq(set_entry):
                        sets.append(set_entry)
                        del set_entry
                except AttributeError:
                    print('invalid set')
            sets_registered += per_page
            while not sets_registered > total_sets:
                page_number += 1
                event_sets = self._post(request_body, {"eventID": event_id,
                                                       "page_number": page_number,
                                                       "per_page": per_page})
                for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                    set_entry = Set(value, tournament)
                    try:
                        if is_dq(set_entry):
                            sets.append(set_entry)
                            del set_entry
                    except AttributeError:
                        print('invalid set')
                sets_registered += per_page
        except TypeError:
            print("Error with {a}".format(a=tournament))
        return sets
