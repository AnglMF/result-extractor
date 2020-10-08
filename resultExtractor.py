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
        self.competitors = []
        self.__qualified_competitors = []
        self.__unqualified_competitors = []
        self.__unordered = True

    def sort_by_avg_placing(self):
        if self.__unordered:
            self.__unordered = False
            sorted_list = sorted(self.competitors, key=lambda competitors: competitors.average)
            self.competitors = sorted_list

    def set_assistance_requirement(self, **kwargs):
        if kwargs.get("tournament_number"):
            for competitor in self.competitors:
                if competitor.tournaments_assisted >= kwargs.get("tournament_number"):
                    self.__qualified_competitors.append(competitor)
                else:
                    self.__unqualified_competitors.append(competitor)
        elif kwargs.get("assistance_percentage"):
            for competitor in self.competitors:
                if competitor.assistance_percentage >= kwargs.get("assistance_percentage"):
                    self.__qualified_competitors.append(competitor)
                else:
                    self.__unqualified_competitors.append(competitor)
        self.competitors = self.__qualified_competitors

    def get_single_tournament_results(self, tournament):
        competitor_list = []
        for competitor in self.competitors:
            competitor_dict = competitor.get_tournament_result(tournament)
            if not competitor_dict["placing"] == '-':
                competitor_list.append(competitor_dict)
        sorted_list = sorted(competitor_list, key=lambda competitors: competitors["placing"])
        return sorted_list

    def assign_set_history(self):
        for _set in self.total_sets.sets:
            set_assigned = 0
            for player in self.competitors:
                if player.gamertag in _set.get_players():
                    player.register_set(_set)
                    set_assigned += 1
                    if set_assigned == 2:
                        break

    def get_h2h_record(self):
        player_records = []
        for competitor1 in self.competitors:
            player_record_dictionary = {'player': competitor1.gamertag}
            for competitor2 in self.competitors:
                if competitor1 != competitor2:
                    player_record_dictionary[competitor2.gamertag] = competitor1.record_vs(competitor2.gamertag)
            player_records.append(player_record_dictionary)
        return player_records


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
                self.ranking.competitors.append(new_competitor)
                self.participants_dict[participant['id']] = new_competitor
            else:
                self.participants_dict[participant['id']].register_placing(tournament,
                                                                           {"placing": participant['placement'],
                                                                            "seed": participant['seed']})


if __name__ == "__main__":
    tournamentList = load(open("tournamentList.yml", "r"))
    prueba = TournamentSetsRequest()
    prueba.get_all_sets(tournamentList["tournaments"], tournamentList["event"])
    prueba.ranking.sort_by_avg_placing()
    prueba.ranking.assign_set_history()
    participants_placings = []
    for participant in prueba.ranking.competitors:
        participants_placings.append(participant.get_all_placings())
    file = ResultsWorkBook()
    file.create_spreadsheet(prueba, participants_placings, tournamentList["tournaments"])
