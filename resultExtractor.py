from yaml import load
import json

from queries.queries import start_gg, challonge_client
from ResultsWorkbook import ResultsWorkBook
from ranking.competitor import Competitor
from ranking import Ranking
from datetime import datetime

import os


def log(_message, _object):
    print('{msg}:\n{obj}'.format(msg=_message, obj=_object))


class TournamentSetsRequest:
    events = {}  # tournament: event_id
    ranking = Ranking()
    participants_dict = {}  # participant, competitor_object
    sets = ranking.total_sets
    clients = []

    def add_client(self, tournament_list, events_list=[], client="st_gg", user="none", api_key=""):
        if client == "start_gg":
            api_client = start_gg(api_key)
        elif client =="challonge":
            api_client = challonge_client(user, api_key)
        
        self.get_all_sets(tournament_list, events_list, api_client)

    def __get_events_sets(self, events, client):
        for tournament, event in events:
            log("Getting information for ", tournament)
            self._get_event_participants(tournament, event, client)
            self._get_event_sets(tournament, event, client)
            log("Finished processing data for ", tournament)

    def __get_tournament_events(self, tournaments, event, client):
        self.events = client.query_tournament_events(tournaments, events_list=event)

    def get_all_sets(self, tournaments, event, client):
        self.__get_tournament_events(tournaments, event, client)
        self.__get_events_sets(self.events.items(), client)

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


if __name__ == "__main__":
    
    credentials = None
    with open ("credentials.json", "r") as file:
        credentials = json.load(file)
    start_gg_data = load(open("start_gg.yml", "r"))
    challonge_data = load(open("challonge.yml", "r"))
    data = TournamentSetsRequest()

    data.add_client(challonge_data["tournaments"], 
                    client="challonge",
                    user=credentials['challonge_user'],
                    api_key=credentials['challonge'])
      
    # data.add_client(start_gg_data["tournaments"], 
    #                 events_list=start_gg_data["event"], 
    #                 client="start_gg",
    #                 api_key = credentials["start_gg"])
    
    data.ranking.assign_set_history()
    data.ranking.check_tag_mismatch()
    data.ranking.remove_duplicates()

    # Remove duplicate players and merge tags

    # Challonge
    # data.ranking.remove_duplicate_player("Andy")
    # data.ranking.remove_duplicate_player("Frank")
    # data.ranking.remove_duplicate_player("Yoshi")
    # data.ranking.remove_duplicate_player("Fist")
    # data.ranking.remove_duplicate_player("Mike")
    # data.ranking.remove_duplicate_player("Papu")
    # data.ranking.remove_duplicate_player("Luigi")
    # data.ranking.remove_duplicate_player("Skips")
    # data.ranking.remove_duplicate_player("Barto")
    # data.ranking.remove_duplicate_player("Wero")
    data.ranking.merge_players(["Reypokemon", "Rey pokemon"], 'Rey pokemon')
    data.ranking.merge_players(["Andy"], 'Andygib')

    # Start gg
    # data.ranking.merge_players(["Aanndy mijas", "ANDY CRK", "andy gibbs", "Andy Gibs"], "Andygibb")
    # data.ranking.merge_players(["LFG | PanterA", "PanterA"], "PanterA")
    # data.ranking.merge_players(["guzyowo"], "Tunoeresbbsitaeresbbsota")
    # data.ranking.merge_players(["PX - Plusk"],"Plusk")
    # data.ranking.merge_players(["dodo"],"Dodo")
    # data.ranking.merge_players(["rickbb", "elbarto"],"Elbarto")
    # data.ranking.remove_duplicate_player("Fran")
    # data.ranking.remove_duplicate_player("TEC")
    # data.ranking.remove_duplicate_player("Mike")
    # data.ranking.remove_duplicate_player("Saru")
    # data.ranking.remove_duplicate_player("Bimbo")
    # data.ranking.remove_duplicate_player("Oliverga")
    data.ranking.sort_by_avg_placing()
    participants_placings = []
    for participant in data.ranking.competitors_sorted:
        participants_placings.append(participant.get_all_placings())
    file = ResultsWorkBook()
    file.create_spreadsheet(data, participants_placings, list(data.events.keys()))
