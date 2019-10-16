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

    def get_single_tournament_results(self, tournament):
        competitor_list = []
        for competitor in self.competitors:
            competitor_dict = competitor.get_single_tournament_result(tournament)
            if not competitor_dict[tournament + " placing"] == '-':
                competitor_list.append(competitor_dict)
        sorted_list = sorted(competitor_list, key=lambda competitors: competitors[tournament + " placing"])
        return sorted_list

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
        orden = ["id", "avg_placing", "name"] + listaTorneos['tournaments']
        df = df.reindex(columns=orden)
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)
        for cell in self.worksheet['A'] + self.worksheet[1]:
            cell.style = 'Pandas'

    def register_tournament_results(self, tournament, participants):
        df = pandas.DataFrame.from_dict(participants)
        self.worksheet = self.new_worksheet(tournament)
        orden = ["name", tournament + " placing", tournament + " seed", tournament + " difference"]
        df = df.reindex(columns=orden)
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)

    def register_sets(self, info):
        self.worksheet.title = "Sets Head 2 Head"
        df = pandas.DataFrame.from_dict(info)
        orden = ["score1", "p1", "p2", "score2", "tournament", "round", "winner"]
        df = df.reindex(columns=orden)
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)
        for cell in self.worksheet['A'] + self.worksheet[1]:
            cell.style = 'Pandas'

    def save_workbook(self, name):
        self.workbook.save(name)
        self.workbook.close()
        column = self.worksheet.column_dimensions['B']
        column.alignment = Alignment(horizontal='center')


class TournamentSetsRequest:
    auth_token = 'YOUR TOKEN'
    events = {}  # tournament: event_id
    ranking = Ranking()
    participants_dict = {}  # participant, competitor_object
    sets = ranking.total_sets
    client = Query(auth_token)

    def _log(self, _message, _object):
        print('{msg}:\n{obj}'.format(msg=_message, obj=_object))

    def __get_events_sets(self, events):
        for tournament, event in events:
            self._get_event_participants(tournament, event)
            self._log("Participant list", self.ranking.competitors)
            self._get_event_sets(tournament, event)
            self._log("Participants with placings", self.ranking.competitors)

    def __get_tournament_events(self, tournaments, event):
        self.events = self.client.query_tournament_events(tournaments, event)

    def get_all_sets(self, tournaments, event):
        self.__get_tournament_events(tournaments, event)
        self.__get_events_sets(self.events.items())

    def _get_event_sets(self, tournament, event):
        event_sets = self.client.query_event_sets(tournament, event)
        for set in event_sets:
            self.sets.register_set(set)
        self._log('Event sets: ', event_sets)

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
    listaTorneos = load(open("tournamentList.yml", "r"))
    prueba = TournamentSetsRequest()
    prueba.get_all_sets(listaTorneos["tournaments"], listaTorneos["event"])
    file = ResultsWorkBook()
    file.register_sets(prueba.sets.get_sets())
    data = []
    for participant in prueba.ranking.competitors:
        data.append(participant.as_dict())
    file.register_placings(data)
    data = []
    for tournament in listaTorneos["tournaments"]:
        data = prueba.ranking.get_single_tournament_results(tournament)
        file.register_tournament_results(tournament, data)
    file.save_workbook("haber.xlsx")
