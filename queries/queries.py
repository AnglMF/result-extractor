from graphqlclient import GraphQLClient
from ranking.set import Set
from datetime import datetime, timedelta
from time import sleep
from requests import HTTPError as req_error

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
        self.platform = 'start gg'
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
    
    def __extract_set_data(self, data, tournament):
            set_data = {}
            set_data['player1'] = data["slots"][0]["entrant"]["participants"][0]["gamerTag"]
            set_data['player2'] = data["slots"][1]["entrant"]["participants"][0]["gamerTag"]
            set_data['player1_id'] = data["slots"][0]["entrant"]["participants"][0]["player"]["id"]
            set_data['player2_id'] = data["slots"][1]["entrant"]["participants"][0]["player"]["id"]
            set_data['score1'] = data["slots"][0]["standing"]["stats"]["score"]["value"]
            set_data['score2'] = data["slots"][1]["standing"]["stats"]["score"]["value"]
            set_data['seed1'] = data["slots"][0]["entrant"]["seeds"][0]["seedNum"]
            set_data['seed2'] = data["slots"][1]["entrant"]["seeds"][0]["seedNum"]
            set_data['winner'] = data["slots"][0]["standing"]["placement"]
            set_data['set_id'] = data["id"]
            set_data['tournament'] = tournament
            set_data['round'] = abs(data["round"])
            return set_data
    
    def _extract_participant_data(self, data):
        participant = {}
        participant['id'] = data["entrant"]["participants"][0]["player"]["id"]
        participant['name'] = data["entrant"]["participants"][0]["gamerTag"]
        participant['placement'] = data['placement']
        participant['seed'] = data["entrant"]["seeds"][0]["seedNum"]
        return participant

    def query_tournament_events(self, tournaments_list, events_list=[]):
        request_body = queries.tournament_events_query()
        events_dict = {}
        for tournament in tournaments_list:
            response = self._post(request_body, {'tournamentName': tournament})
            try:
                for key, value in enumerate(response['data']['tournament']['events']):
                    for event in events_list:
                        if event == value['name']:
                            event_dict = {}
                            event_dict['id'] = value['id']
                            event_dict['platform'] = self.platform
                            events_dict[tournament] = event_dict
            except TypeError:
                print("Tournament doesn't exist: {t}".format(t=tournament))
        if events_dict:
            return events_dict
        else:
            raise ValueError('Event {e} not found'.format(e=events_list))

    def query_event_standings(self, event):
        request_body = queries.event_standings_query()
        response = self._post(request_body, {'eventID': event})
        print(response)
        participants_standings_list = []
        total_participants = response['data']['event']['standings']['pageInfo']['total']
        for key, value in enumerate(response['data']['event']['standings']['nodes']):
            participant = self._extract_participant_data(value)
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
                        set_data = self.__extract_set_data(value, tournament)
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
        self.platform = 'challonge'
        self.last_request = datetime.now()
        self.next_request = datetime.now()

    def _extract_set_data(self, data, tournament, players_dict):
        set_data = {}
        score1, score2 = data['scores_csv'].split('-')
        set_data['player1_id'] = data['winner_id']
        set_data['player2_id'] = data['loser_id']
        set_data['player1'] = players_dict[set_data['player1_id']]["name"]
        set_data['player2'] = players_dict[set_data['player2_id']]["name"]
        set_data['score1'] = int(score1)
        set_data['score2'] = int(score2)
        set_data['seed1'] = players_dict[set_data['player1_id']]["seed"]
        set_data['seed2'] = players_dict[set_data['player2_id']]["seed"]
        set_data['winner'] = 1
        set_data['set_id'] = data["id"]
        set_data['tournament'] = tournament
        set_data['round'] = abs(data["round"])
        return set_data

    def _extract_participant_data(self, data):
        participant = {}
        participant['id'] = data['id']
        participant['name'] = data['name']
        participant['placement'] = data['final_rank']
        participant['seed'] = data['seed']
        return participant

    def query_tournament_events(self, tournaments_list, events_list=[]):
        events_dict = {}
        print(tournaments_list)
        print(events_list)
        for tournament in tournaments_list:
            try:
                response = challonge.tournaments.show(tournament)
                try:
                    event_dict = {}
                    event_dict['id'] = response['url']
                    event_dict['platform'] = self.platform
                    events_dict[response['name']] = event_dict
                except TypeError:
                    print("Tournament doesn't exist: {t}".format(t=tournament))
            except req_error as e:
                print(f'You do not have access to {tournament}')
                print(f'Check your API credentials or that the tournament is finished')
        if events_dict:
            return events_dict
        else:
            print('Issues, idk.')

    def query_event_standings(self, event):
        participants_standings_list = []
        try:
            response = challonge.participants.index(event)
            for competitor in response:
                participant = self._extract_participant_data(competitor)
                participants_standings_list.append(participant)
                if participant['placement'] == None:
                    print('Tournament has no standings, check that it was finished.')
        except req_error as e:
            print(e)
            print('API issues')
        return participants_standings_list, 0

    def query_event_sets(self, tournament, event_id=''):
        sets = []

        try:
            response = challonge.matches.index(event_id, state='complete')
            players_dict = {} # {<id>: <name>}
            for player in challonge.participants.index(event_id):
                players_dict[player['id']] = {"name": player['name'], 
                                            "seed": player['seed']
                                            }
            try:
                for match in response:
                    try:
                        set_data = self._extract_set_data(match, 
                                                        tournament, 
                                                        players_dict)
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
        except req_error as e:
            print('API issues')
            print(e)
        return sets