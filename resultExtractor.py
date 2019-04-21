from graphqlclient import GraphQLClient
from yaml import load
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment

from competitor.competitor import Competitor
from sets.set_history import SetHistory
from sets.set import Set
import queries

import pandas
import json


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
    auth_token = '026d66d8eeb4f1e73aa2ebe750388536'
    events = []  # {event_id, tournament}
    ranking = Ranking()
    participants_dict = {}
    sets = ranking.total_sets
    cache_responses = {}

    def __init__(self):
        self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
        self.client.inject_token('Bearer ' + self.auth_token)

    def _log(self, _message, _object):
        print('{msg}:\n{obj}'.format(msg=_message, obj=_object))

    def _post(self, query_name,  query, query_variables):
        self._log("Query: {name}\nQuery Variables: {variables}".format(name=query_name, variables=query_variables),
                  "--------------------------------")
        result = self.client.execute(query, query_variables)
        result_object = json.loads(result)
        self.cache_responses[query_name] = result_object
        if "errors" in result_object.keys():
            self._log("Query Response", result_object)
            raise ValueError
        return result_object

    def _update_participants_dict(self):
        udpated_dict = {}
        for registered_participant in self.ranking.competitors:
            udpated_dict[registered_participant.id] = registered_participant.gamertag
        self.participants_dict = udpated_dict

    def get_tournament_sets(self, tournaments, event):
        self.events = self._get_tournament_events(tournaments, event)
        for event in self.events:
            self._get_event_participants(event)
            self._log("Participant list", self.ranking.competitors)
            self._get_event_sets(event)
            self._set_participant_placement_per_event(event)
            self._log("Participants with placings", self.ranking.competitors)
        # self.ranking.set_assistance_requirement(tournament_number=3)
        self.ranking.sort_by_avg_placing()
        self.ranking.assign_set_history_for_top_15_players()
        self._log("cache", self.cache_responses)

    def _create_set_entry(self, raw_data, tournament):
        set_entry = Set(raw_data, tournament)
        # set_entry["Winner"] = participants_dict[raw_data["winnerId"]]
        if set_entry.score1 >= 0 and set_entry.score2 >= 0:
            # DQs are marked on smash.gg as game count -1, so don't include DQs
            self.sets.register_set(set_entry)
            del set_entry

    def _get_event_sets(self, event):
        page_number = 1
        per_page = 49
        sets_registered = 0
        event_sets_query = queries.event_sets_query()
        event_sets = self._post("event sets", event_sets_query, {"eventID": event["event_id"],
                                                                 "page_number": page_number,
                                                                 "per_page": per_page})
        for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
            self._create_set_entry(value, event["tournament"])
        sets_registered += per_page
        while not sets_registered > event_sets["data"]["event"]["sets"]["pageInfo"]["total"]:
            page_number += 1
            event_sets = self._post("event sets", event_sets_query, {"eventID": event["event_id"],
                                                                     "page_number": page_number,
                                                                     "per_page": per_page})
            try:
                for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                    self._create_set_entry(value, event["tournament"])
                sets_registered += per_page
            except TypeError:
                pass

    def set_participant_placement(self, participant_id, event, placement):
        for nemo_participant in self.ranking.competitors:
            if nemo_participant.id == participant_id:
                nemo_participant.register_placing(event["tournament"], placement)

    def _set_participant_placement_per_event(self, event):
        response = self._get_event_standings(event)
        for key, value in enumerate(response["data"]["event"]["standings"]["nodes"]):
            self.set_participant_placement(value["entrant"]["participants"][0]["playerId"], event,
                                           value["placement"])

    def _get_event_standings(self, event):
        event_standings_query = queries.event_standings_query()
        participants_response = self._post("event standings", event_standings_query,
                                           {"eventID": event["event_id"]})
        return participants_response

    def _get_event_participants(self, event):
        event_participants_query = queries.event_participants_query()
        participants_data = self._post("event participants", event_participants_query,
                                           {"eventID": event["event_id"]})
        for key, value in enumerate(participants_data["data"]["event"]["entrants"]["nodes"]):
            new_participant = Competitor(value["participants"][0]["playerId"],
                                         value["participants"][0]["gamerTag"], listaTorneos["tournaments"])
            if new_participant.id not in self.participants_dict.keys():
                self.ranking.competitors.append(new_participant)
            del new_participant

        self._update_participants_dict()

    def _get_tournament_events(self, tournaments, events):
        event_id_list = []
        tournament_query = queries.tournament_events_query()
        tournament_query_response = ''
        for tournament in tournaments:
            try:
                tournament_query_response = self._post("tournament events", tournament_query,
                                                       {"tournamentName": tournament})
                event_found = False
                self._log('Looking for events:\n{events}'.format(events=events), '')
                for key, value in enumerate(tournament_query_response["data"]["tournament"]["events"]):
                    self._log("'{ev}' event on {t}".format(ev=value["name"], t=tournament), '')
                    if value["name"] in events:
                        event_id_list.append({"event_id": value["id"], "tournament": tournament})
                        event_found = True
                        break
                if not event_found:
                    self._log('Not all events found on {tournament}'.format(tournament=tournament), '-----------------')
            except ValueError:
                self._log("There's an error with the query", tournament_query_response)
            except TypeError:
                self._log("Query response empty, tournament not found", tournament)

        return event_id_list


if __name__ == "__main__":
    listaTorneos = load(open("tournamentList.yml", "r"))
    prueba = TournamentSetsRequest()
    prueba.get_tournament_sets(listaTorneos["tournaments"], listaTorneos["events"])
    file = ResultsWorkBook()
    file.register_sets(prueba.sets.get_sets())
    data = []
    for participant in prueba.ranking.competitors:
        data.append(participant.as_dict())
    file.register_placings(data)
    file.save_workbook("haber.xlsx")
