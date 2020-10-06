from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment

import pandas


class ResultsWorkBook:
    def __init__(self):
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.index = 1

    def new_worksheet(self, name):
        self.index += 1
        return self.workbook.create_sheet(title=name, index=self.index)

    def register_placings(self, info, tournaments):
        self.worksheet = self.new_worksheet("Placings")
        df = pandas.DataFrame.from_dict(info)
        df = df.sort_values("avg_placing")
        orden = ["id", "avg_placing", "win_perc", "name"] + tournaments
        df = df.reindex(columns=orden)
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)
        for cell in self.worksheet['A'] + self.worksheet[1]:
            cell.style = 'Pandas'

    def register_h2h(self, info):
        self.worksheet = self.new_worksheet("H2H")
        df = pandas.DataFrame.from_dict(info)
        player_list = []
        for competitor in info:
            player_list.append(competitor["player"])
        orden = ["player"] + player_list
        df = df.reindex(columns=orden)
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)

    def register_tournament_results(self, tournament, participants):
        df = pandas.DataFrame.from_dict(participants)
        self.worksheet = self.new_worksheet(tournament)
        orden = ["name", "placing", "seed", "performance"]
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

    def create_spreadsheet(self, ranking_object, placings, tournaments):
        self.register_sets(ranking_object.sets.get_sets())
        self.register_h2h(ranking_object.ranking.get_h2h_record())
        self.register_placings(placings, tournaments)
        for tournament in tournaments:
            data = ranking_object.ranking.get_single_tournament_results(tournament)
            self.register_tournament_results(tournament, data)
        self.save_workbook("haber.xlsx")