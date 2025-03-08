from graphqlclient import GraphQLClient
from sets.set import Set
from datetime import datetime, timedelta
from time import sleep

import challonge
import queries
import json


def is_valid(_set):
    dq = False
    invalid = False
    ## Check if the set is a DQ (one of the scores is -1)
    try:
        if _set.score1 < 0 or _set.score2 < 0:
            dq = True
    except (ValueError, TypeError) as e:
        invalid = True
        print(e)
    finally:
        return not (dq or invalid)


class start_gg:
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

    def query_tournament_events(self, tournaments_list, events_list=[]):
        request_body = queries.tournament_events_query()
        events_dict = {}
        for tournament in tournaments_list:
            response = self._post(request_body, {'tournamentName': tournament})
            try:
                for key, value in enumerate(response['data']['tournament']['events']):
                    for event in events_list:
                        if event == value['name']:
                            events_dict[tournament] = value['id']
            except TypeError:
                print("Tournament doesn't exist: {t}".format(t=tournament))
        if events_dict:
            return events_dict
        else:
            raise ValueError('Event {e} not found'.format(e=events_list))

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
        per_page = 41
        sets_registered = 0
        request_body = queries.event_sets_query()
        sets = []
        try:
            while True:
                event_sets = self._post(request_body, {"eventID": event_id,
                                                       "page_number": page_number,
                                                       "per_page": per_page})
                total_sets = event_sets["data"]["event"]["sets"]["pageInfo"]["total"]
                for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                    try:
                        set_data = {}
                        set_data['player1'] = value["slots"][0]["entrant"]["participants"][0]["gamerTag"]
                        set_data['player2'] = value["slots"][1]["entrant"]["participants"][0]["gamerTag"]
                        set_data['player1_id'] = value["slots"][0]["entrant"]["participants"][0]["player"]["id"]
                        set_data['player2_id'] = value["slots"][1]["entrant"]["participants"][0]["player"]["id"]
                        set_data['score1'] = value["slots"][0]["standing"]["stats"]["score"]["value"]
                        set_data['score2'] = value["slots"][1]["standing"]["stats"]["score"]["value"]
                        set_data['seed1'] = value["slots"][0]["entrant"]["seeds"][0]["seedNum"]
                        set_data['seed2'] = value["slots"][1]["entrant"]["seeds"][0]["seedNum"]
                        set_data['winner'] = value["slots"][0]["standing"]["placement"]
                        set_data['set_id'] = value["id"]
                        set_data['tournament'] = tournament
                        set_data['round'] = abs(value["round"])
                        set_entry = Set(set_data, tournament)
                        if is_valid(set_entry) and set_entry.valid:
                            sets.append(set_entry)
                            del set_entry
                    except AttributeError:
                        pass
                sets_registered += per_page
                page_number += 1
                if sets_registered >= total_sets:
                    print(f'Registered {sets_registered} sets of {total_sets}')
                    break
        except TypeError as e:
            print(f'Error with {tournament}')
            print(e)
        return sets
    
class challonge_client:
    def __init__(self, user, api_key):
        challonge.set_credentials(user, api_key)
        self.last_request = datetime.now()
        self.next_request = datetime.now()

    def query_tournament_events(self, tournaments_list, events_list=[]):
        events_dict = {}
        for tournament in tournaments_list:
            response = challonge.tournaments.show(tournament)
            try:
                events_dict[response['name']] = response['url']
            except TypeError:
                print("Tournament doesn't exist: {t}".format(t=tournament))
        if events_dict:
            return events_dict
        else:
            raise ValueError('Event {e} not found'.format(e=events_list))

    def query_event_standings(self, event):
        
        response = challonge.participants.index(event)
        participants_standings_list = []
        for competitor in response:
            participant = {}
            participant['id'] = competitor['id']
            participant['name'] = competitor['name']
            participant['placement'] = competitor['final_rank']
            participant['seed'] = competitor['seed']
            participants_standings_list.append(participant)
        return participants_standings_list, 0

    def query_event_sets(self, tournament, event_id=''):

        response = challonge.matches.index(event_id, state='complete')
        sets = []
        players_dict = {} # {<id>: <name>}
        for player in challonge.participants.index(event_id):
            players_dict[player['id']] = {"name": player['name'], 
                                          "seed": player['seed']
                                          }
        try:
            for match in response:
                try:
                    set_data = {}
                    score1, score2 = match['scores_csv'].split('-')
                    set_data['player1_id'] = match['winner_id']
                    set_data['player2_id'] = match['loser_id']
                    set_data['player1'] = players_dict[set_data['player1_id']]["name"]
                    set_data['player2'] = players_dict[set_data['player2_id']]["name"]
                    set_data['score1'] = int(score1)
                    set_data['score2'] = int(score2)
                    set_data['seed1'] = players_dict[set_data['player1_id']]["seed"]
                    set_data['seed2'] = players_dict[set_data['player2_id']]["seed"]
                    set_data['winner'] = 1
                    set_data['set_id'] = match["id"]
                    set_data['tournament'] = tournament
                    set_data['round'] = abs(match["round"])
                    set_entry = Set(set_data, tournament)
                    if is_valid(set_entry) and set_entry.valid:
                        sets.append(set_entry)
                        del set_entry
                except AttributeError as e:
                    print(e)
                    pass
        except TypeError as e:
            print(f'Error with {event_id}, {tournament}')
            print(e)
        return sets