from queries.queries import start_gg, challonge_client
from ranking.competitor import Competitor
from ranking.ranking import Ranking



def log(_message, _object):
    print('{msg}:\n{obj}'.format(msg=_message, obj=_object))


class ResultExtractor:
    events = {}  # tournament: {'id': event_id, 'platform': platform}
    ranking = Ranking()
    participants_dict = {}  # participant, competitor_object
    sets = ranking.total_sets
    challonge_client = None
    start_gg_client = None

    def add_client(self, tournament_list, events_list=[], client="st_gg", user="none", api_key=""):
        if client == "start_gg":
            self.start_gg_client = start_gg(api_key)
            self.__get_tournament_events(tournament_list, 
                                         events_list, 
                                         self.start_gg_client)
        elif client =="challonge":
            self.challonge_client = challonge_client(user, api_key)
            self.__get_tournament_events(tournament_list, 
                                         events_list, 
                                         self.challonge_client)

    def __get_events_sets(self, events, client):
        for tournament, event in events:
            log("Getting information for ", tournament)
            self._get_event_participants(tournament, event['id'], client)
            self._get_event_sets(tournament, event['id'], client)
            log("Finished processing data for ", tournament)

    def __get_tournament_events(self, tournaments, event, client):
        self.events.update(client.query_tournament_events(tournaments,
                                                          events_list=event))

    def get_all_sets(self):
        for client in [self.start_gg_client, self.challonge_client]:
            events_to_check = {}
            for key, value in self.events.items():
                try:
                    if value['platform'] == client.platform:
                        events_to_check[key] = value
                except AttributeError:
                    pass
            self.__get_events_sets(events_to_check.items(), client)
            print('All players found:')
            print(self.ranking.competitors_tags)

    def _get_event_sets(self, tournament, event, client):
        event_sets = client.query_event_sets(tournament, event_id = event)
        for set in event_sets:
            self.sets.register_set(set)

    def _get_event_participants(self, tournament, event, client):
        event_participants, total_participants = client.query_event_standings(event)
        for participant in event_participants:
            if participant['id'] not in self.participants_dict.keys():
                print(f'adding competitor {participant["name"]}')
                new_competitor = Competitor(participant['id'], participant['name'], self.events.keys())
                new_competitor.register_placing(tournament, {"placing": participant['placement'],
                                                             "seed": participant['seed']})
                self.ranking.competitors[new_competitor.id] =new_competitor
                self.ranking.competitors_tags.append(new_competitor.gamertag)
                self.participants_dict[participant['id']] = new_competitor
            else:
                self.participants_dict[participant['id']].register_placing(tournament,
                                                                           {"placing": participant['placement'],
                                                                            "seed": participant['seed']})