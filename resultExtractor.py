from yaml import load

from competitor.competitor import Competitor
from sets.set_history import SetHistory
from queries.queries import Query
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
        self.__unordered = True

    def sort_by_avg_placing(self):
        if self.__unordered:
            self.__unordered = False
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
                        self.total_sets.update_player_tag(
                            mismatch[id], self.competitors[id].gamertag
                        )
        return

    def assign_set_history(self):
        self.check_tag_mismatch()
        for _set in self.total_sets.sets:
            set_assigned = 0
            for player in list(self.competitors.values()):
                if player.id in _set.as_dict().values():
                    player.register_set(_set)
                    set_assigned += 1
                    if set_assigned == 2:
                        break

    def get_h2h_record(self):
        player_records = []
        for competitor1 in list(self.competitors.values()):
            player_record_dictionary = {'player': competitor1.gamertag}
            for competitor2 in self.competitors.values():
                if competitor1 != competitor2:
                    player_record_dictionary[competitor2.gamertag] = competitor1.record_vs(competitor2.gamertag)
            player_records.append(player_record_dictionary)
        return player_records
    
    def merge_players(self, old_tags, new_tag):
        for old_tag in old_tags:

            # If the tag is the same, no need to update the tag
            if not old_tag == new_tag: 
                print("Updating set history...")
                self.total_sets.update_player_tag(old_tag, new_tag)

            #Begin search of player where data will be merged (new_tag)
            for player in list(self.competitors.values()):
                if player.gamertag == new_tag:
                    # Player who will have data merged has been found

                    # Iterate through all players to correct the data to new_tag
                    for old_player in list(self.competitors.values()):

                        # Check if current player is to be removed
                        if old_player.gamertag == old_tag:

                            # Duplicate/copy has been found
                            if not old_player == player:
                                # If it's not actually the same player, merge them
                                player.combine_data(old_player)
                                self.competitors.pop(old_player.id)
                                print(f'Merged player {old_tag} into {new_tag}')

                        # If not to be removed, check if player has sets vs
                        # player to be removed, and update to new_tag
                        elif old_player.record_vs(old_tag):
                            old_player.update_player_tag(old_tag, new_tag)
                            print(f'Updated set data for {old_player.gamertag}')

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
    client = Query(os.environ['TOKEN'])

    def __get_events_sets(self, events):
        for tournament, event in events:
            log("Getting information for " + tournament, None)
            self._get_event_participants(tournament, event)
            self._get_event_sets(tournament, event)
            log(tournament + " done", None)

    def __get_tournament_events(self, tournaments, event):
        self.events = self.client.query_tournament_events(tournaments, event)

    def get_all_sets(self, tournaments, event):
        self.__get_tournament_events(tournaments, event)
        self.__get_events_sets(self.events.items())

    def _get_event_sets(self, tournament, event):
        event_sets = self.client.query_event_sets(tournament, event)
        for set in event_sets:
            self.sets.register_set(set)

    def _get_event_participants(self, tournament, event):
        event_participants, total_participants = self.client.query_event_standings(event)
        for participant in event_participants:
            if participant['id'] not in self.participants_dict.keys():
                new_competitor = Competitor(participant['id'], participant['name'], self.events.keys())
                new_competitor.register_placing(tournament, {"placing": participant['placement'],
                                                             "seed": participant['seed']})
                self.ranking.competitors[new_competitor.id] =new_competitor
                self.ranking.competitors_tags.append(new_competitor.gamertag)
                print(f'Added new player tag: {new_competitor.gamertag}')
                self.participants_dict[participant['id']] = new_competitor
            else:
                self.participants_dict[participant['id']].register_placing(tournament,
                                                                           {"placing": participant['placement'],
                                                                            "seed": participant['seed']})


if __name__ == "__main__":
    tournamentList = load(open("tournamentList.yml", "r"))
    data = TournamentSetsRequest()
    data.get_all_sets(tournamentList["tournaments"], tournamentList["event"])
    data.ranking.merge_players(["Aanndy mijas"], "Andygibb")
    data.ranking.merge_players(["LFG | PanterA", "PanterA"], "PanterA")
    data.ranking.merge_players(["Saru"], "Saru")
    data.ranking.merge_players(["guzyowo"], "Guzy")
    data.ranking.merge_players(["TEC"],"Tec")
    data.ranking.remove_duplicate_player("Fran")
    data.ranking.remove_duplicate_player("Mike")
    data.ranking.remove_duplicate_player("Bimbo")
    data.ranking.sort_by_avg_placing()
    data.ranking.assign_set_history()
    participants_placings = []
    for participant in data.ranking.competitors_sorted:
        participants_placings.append(participant.get_all_placings())
    file = ResultsWorkBook()
    file.create_spreadsheet(data, participants_placings, tournamentList["tournaments"])
