from yaml import load
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment

from competitor.competitor import Competitor
from sets.set_history import SetHistory
from queries.queries import Query

import pandas


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

    def get(self):
        self.sort_by_avg_placing()
        competitor_list = []
        for competitor in self.competitors:
            competitor_list.append(competitor.as_dict())
        return competitor_list

    def assign_set_history_for_top_15_players(self):
        try:
            for i in range(0, 14):
                sets_to_register = []
                for set in self.total_sets.sets:
                    if self.competitors[i].gamertag in set.get_players():
                        sets_to_register.append(set)
                        self.competitors[i].register_set(set)
        except IndexError:
            print('Not Enough qualified competitors')

class ResultsWorkBook:

    def __init__(self):
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.index = 1

    def new_worksheet(self, name):
        self.index += 1
        return self.workbook.create_sheet(title=name, index=self.index)

    def register_placings(self, info):
        self.worksheet = self.new_worksheet("Placings")
        df = pandas.DataFrame.from_dict(info)
        df = df.sort_values("avg_placing")
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)
        for cell in self.worksheet['A'] + self.worksheet[1]:
            cell.style = 'Pandas'
        print(df)

    def register_sets(self, info):
        self.worksheet.title = "Sets Head 2 Head"
        df = pandas.DataFrame.from_dict(info)
        orden = ["score1", "p1", "p2", "score2", "tournament", "round", "winner"]
        df = df.reindex(columns=orden)
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)
        for cell in self.worksheet['A'] + self.worksheet[1]:
            cell.style = 'Pandas'
        print(df)

    def save_workbook(self, name):
        self.workbook.save(name)
        self.workbook.close()
        column = self.worksheet.column_dimensions['B']
        column.alignment = Alignment(horizontal='center')


class TournamentSetsRequest:
    auth_token = 'YOUR TOKEN'
    events = {}  # tournament: event_id
    ranking = Ranking()
    participants_dict = {}
    sets = ranking.total_sets
    client = Query(auth_token)

    def _log(self, _message, _object):
        print('{msg}:\n{obj}'.format(msg=_message, obj=_object))

    def _update_participants_dict(self):
        udpated_dict = {}
        for registered_participant in self.ranking.competitors:
            udpated_dict[registered_participant.id] = registered_participant.gamertag
        self.participants_dict = udpated_dict

    def get_tournament_sets(self, tournaments, event):
        self.events = self.client.query_tournament_events(tournaments, event)
        for tournament, event in self.events.items():
            self._get_event_participants(tournament, event)
            self._log("Participant list", self.ranking.competitors)
            self._get_event_sets(tournament, event)
            self._log("Participants with placings", self.ranking.competitors)
        # self.ranking.set_assistance_requirement(tournament_number=3)
        self.ranking.sort_by_avg_placing()
        self.ranking.assign_set_history_for_top_15_players()

    def _get_event_sets(self, tournament, event):
        event_sets = self.client.query_event_sets(tournament, event)
        for set in event_sets:
            self.sets.register_set(set)
        self._log('Event sets: ', event_sets)

    def set_participant_placement(self, participant_id, tournament, placement):
        for nemo_participant in self.ranking.competitors:
            if nemo_participant.id == participant_id:
                nemo_participant.register_placing(tournament, placement)

    def _get_event_participants(self, tournament, event):
        event_participants, total_participants = self.client.query_event_standings(event)
        for participant in event_participants:
            new_participant = Competitor(participant['id'], participant['name'], self.events.keys())
            if new_participant.id not in self.participants_dict.keys():
                self.ranking.competitors.append(new_participant)
            self.set_participant_placement(participant['id'], tournament, participant['placement'])
            del new_participant
        self._update_participants_dict()


if __name__ == "__main__":
    listaTorneos = load(open("tournamentList.yml", "r"))
    prueba = TournamentSetsRequest()
    prueba.get_tournament_sets(listaTorneos["tournaments"], listaTorneos["event"])
    file = ResultsWorkBook()
    file.register_sets(prueba.sets.get_sets())
    data = []
    for participant in prueba.ranking.competitors:
        data.append(participant.as_dict())
    file.register_placings(data)
    file.save_workbook("haber.xlsx")
