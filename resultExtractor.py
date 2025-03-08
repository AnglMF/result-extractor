from yaml import load
import json

from competitor.competitor import Competitor
from sets.set_history import SetHistory
from queries.queries import start_gg, challonge_client
from ResultsWorkbook import ResultsWorkBook
from datetime import datetime

import os


def log(_message, _object):
    print('{msg}:\n{obj}'.format(msg=_message, obj=_object))


class Ranking:
    def __init__(self):
        self.total_sets = SetHistory('Global')
        self.competitors = {}
        self.competitors_sorted = []
        self.competitors_tags = []
        self.__qualified_competitors = {}
        self.__unqualified_competitors = {}
        self.unordered = True

    def sort_by_avg_placing(self):
        if self.unordered:
            self.unordered = False
            sorted_list = sorted(list(self.competitors.values()), key=lambda competitors: competitors.average)
            self.competitors_sorted = sorted_list

    def set_assistance_requirement(self, **kwargs):
        if kwargs.get("tournament_number"):
            for competitor in list(self.competitors.values()):
                if competitor.tournaments_assisted >= kwargs.get("tournament_number"):
                    self.__qualified_competitors[competitor.id] = competitor
                else:
                    self.__unqualified_competitors[competitor.id] = competitor
        elif kwargs.get("assistance_percentage"):
            for competitor in list(self.competitors.values()):
                if competitor.assistance_percentage >= kwargs.get("assistance_percentage"):
                    self.__qualified_competitors[competitor.id] = competitor
                else:
                    self.__unqualified_competitors[competitor.id] = competitor
        self.competitors = self.__qualified_competitors

    def get_single_tournament_results(self, tournament):
        competitor_list = []
        for competitor in list(self.competitors.values()):
            competitor_dict = competitor.get_tournament_result(tournament)
            if not competitor_dict["placing"] == '-':
                competitor_list.append(competitor_dict)
        sorted_list = sorted(competitor_list, key=lambda competitors: competitors["placing"])
        return sorted_list
    
    def check_tag_mismatch(self):
        needs_correction = []
        for _set in self.total_sets.sets:
            for player in _set.get_players():
                for gamertag in player.values():
                    if gamertag not in self.competitors_tags:
                        if player not in needs_correction:
                            needs_correction.append(player)

        # See who the tags actually belong to
        for mismatch in needs_correction:
                for id in mismatch.keys():
                    print(f'Updating {mismatch[id]} into {self.competitors[id].gamertag}')
                    self.total_sets.update_player_tag(
                        mismatch[id], self.competitors[id].gamertag
                    )
        return

#     def assign_set_history(self):
#         self.check_tag_mismatch()
#         for _set in self.total_sets.sets:
#             set_assigned = 0
#             set_dict = _set.as_dict()
#             for player in list(self.competitors.values()):
#                 if player.id in [set_dict["winner_id"], set_dict["loser_id"]]:
#                     player.register_set(_set)
#                     set_assigned += 1
#                     if set_assigned == 2:
#                         break
#                 if set_assigned == 0:
#                     print(f'Error registering the following set:')
#                     print(_set.as_dict())

    def assign_set_history(self):
        self.check_tag_mismatch()
        try:
            for _set in self.total_sets.sets:
                set_dict = _set.as_dict()
                # Assign set to winner of set
                self.competitors[set_dict["winner_id"]].register_set(_set)
                
                # Assign set to loser of set
                self.competitors[set_dict["loser_id"]].register_set(_set)
        except KeyError:
            print(f'Error registering the following set:')
            print(_set.as_dict())

    def get_h2h_record(self, competitor_list):
        player_records = []
        for competitor1 in competitor_list:
            player_record_dictionary = {'player': competitor1.gamertag}
            for competitor2 in competitor_list:
                if competitor1 != competitor2:
                    player_record_dictionary[competitor2.gamertag] = competitor1.record_vs(competitor2)
            player_records.append(player_record_dictionary)
        return player_records
    
    def get_games_h2h_record(self, competitor_list):
        player_records = []
        for competitor1 in competitor_list:
            player_record_dictionary = {'player': competitor1.gamertag}
            for competitor2 in competitor_list:
                if competitor1 != competitor2:
                    player_record_dictionary[competitor2.gamertag] = competitor1.record_vs_games(competitor2)
            player_records.append(player_record_dictionary)
        return player_records
    
    def check_inconsistencies(self, competitor1, competitor2):
            #set_data1 = competitor1.get_sets('vs', opponent=competitor2)
            #set_data2 = competitor2.get_sets('vs', opponent=competitor1)
            set_data1 = competitor1.sets.get_sets_vs(competitor2)
            set_data2 = competitor2.sets.get_sets_vs(competitor1)
            if set_data1 and set_data2:

                if  len(set_data1) != len(set_data2):
                    #print(f'Inconsistency found with {competitor1.gamertag} and {competitor2.gamertag} set data')
                    #print(f'{competitor1} data:')
                    #print(set_data1)
                    #print(f'{competitor2} data:')
                    #print(set_data2)
                    pass
    
    def merge_players(self, old_tags, new_tag):

        for player in list(self.competitors.values()):
            if player.gamertag == new_tag:
                # Found original
                #print(f'Found {player.gamertag}')

                # Search for the copies
                for old_tag in old_tags:
                    #print(old_tag)
                    if old_tag != new_tag:
                        #print(f'Updating set history from {old_tag} into {new_tag}')
                        self.total_sets.update_player_tag(old_tag, new_tag)

                    # Look for every player to see if there is data to update
                    for updating_player in list(self.competitors.values()):
                        
                        if updating_player.gamertag == old_tag:
                            # Found copy
                            #print(f'Found {old_tag}, merging into {new_tag}')
                            if not updating_player == player:
                                # If it's not actually the same player, merge them
                                #print(f'Combining data into {new_tag}')
                                player.combine_data(updating_player)
                                #print(f'Removing {updating_player.gamertag}')
                                self.competitors.pop(updating_player.id)
                                #print(f'Merged player {old_tag} into {new_tag}')
                        elif updating_player.sets.get_sets_vs(old_tag) !="":
                            # Check if there is data to update
                            #print(f'{updating_player.gamertag} has sets with {old_tag}, updating...')
                            updating_player.sets.update_player_tag(old_tag, new_tag)
                            #print(f'Updated set data for {updating_player.gamertag}')
                        else: 
                            pass
                            #print(f'{updating_player.gamertag} has no sets vs {old_tag}')

                        if old_tag != new_tag:
                            self.check_inconsistencies(player, updating_player)    
                break
        return
    
    def remove_duplicate_player(self, tag):
        self.merge_players([tag],tag)
        return


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

    #data.add_client(challonge_data["tournaments"], 
    #                client="challonge",
    #                user=credentials['challonge_user']
    #                api_key=credentials['challonge'])
      
    data.add_client(start_gg_data["tournaments"], 
                    events_list=start_gg_data["event"], 
                    client="start_gg",
                    api_key = credentials["start_gg"])
    
    data.ranking.assign_set_history()

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
    # data.ranking.merge_players(["Reypokemon", "Rey pokemon"], 'Rey pokemon')
    # data.ranking.merge_players(["Andy"], 'Andygib')

    # Start gg
    data.ranking.merge_players(["Aanndy mijas", "ANDY CRK", "andy gibbs", "Andy Gibs"], "Andygibb")
    data.ranking.merge_players(["LFG | PanterA", "PanterA"], "PanterA")
    data.ranking.merge_players(["guzyowo"], "Tunoeresbbsitaeresbbsota")
    data.ranking.merge_players(["PX - Plusk"],"Plusk")
    data.ranking.merge_players(["dodo"],"Dodo")
    data.ranking.merge_players(["rickbb", "elbarto"],"Elbarto")
    data.ranking.remove_duplicate_player("Fran")
    data.ranking.remove_duplicate_player("TEC")
    data.ranking.remove_duplicate_player("Mike")
    data.ranking.remove_duplicate_player("Saru")
    data.ranking.remove_duplicate_player("Bimbo")
    data.ranking.remove_duplicate_player("Oliverga")
    data.ranking.sort_by_avg_placing()
    participants_placings = []
    for participant in data.ranking.competitors_sorted:
        participants_placings.append(participant.get_all_placings())
    file = ResultsWorkBook()
    file.create_spreadsheet(data, participants_placings, list(data.events.keys()))
