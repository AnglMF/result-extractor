from graphqlclient import GraphQLClient
from yaml import load
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

import pandas
import json


class ResultsWorkBook:

  def __init__(self):
    self.workbook = Workbook()
    self.worksheet = self.workbook.active

  def register_sets(self, setsDict):
    df = pandas.DataFrame.from_dict(prueba.sets)
    for r in dataframe_to_rows(df, index=True, header=True):
      self.worksheet.append(r)
    for cell in self.worksheet['A'] + self.worksheet[1]:
      cell.style = 'Pandas'
    print(df)
    self.save_workbook("output/test.xlsx")

  def save_workbook(self, name):
    self.workbook.save(name)


class TournamentSetsRequest:
    events = []
    participants = {}  # Id, gamerTag, {tournament, placing}
    sets = []  # {SetId, Tournament, Player1, Score1, Player2, Score2, Winner}
    cache_responses = {}

    def __init__(self):
        self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
        self.client.inject_token('Bearer ' + '026d66d8eeb4f1e73aa2ebe750388536')

    def _log(self, _message, _object):
        print('{msg}:\n{obj}'.format(msg=_message, obj=_object))

    def _post(self, query, query_variables):
        result = self.client.execute(query, query_variables)
        result_object = json.loads(result)
        self._log("Query Response", result_object)
        return result_object

    def get_participants_placings(self):
        2

    def get_tournament_sets(self, tournaments, event):
        self.events = self._get_tournament_events(tournaments, event)
        # LOGGING
        for event in self.events:
            self._get_event_participants(event)
            self._log("Participant list", self.participants)
            self._get_event_sets(event)

    def _create_set_entry(self, raw_data, tournament):
        set_entry = {}
        set_entry["SetID"] = raw_data["id"]
        set_entry["Tournament"] = tournament
        set_entry["Player1"] = self.participants[raw_data["slots"][0]["entrant"]["id"]]
        set_entry["ScorePlayer1"] = raw_data["slots"][0]["standing"]["stats"]["score"]["value"]
        set_entry["Player2"] = self.participants[raw_data["slots"][1]["entrant"]["id"]]
        set_entry["ScorePlayer2"] = raw_data["slots"][1]["standing"]["stats"]["score"]["value"]
        set_entry["Winner"] = self.participants[raw_data["winnerId"]]
        if not(set_entry["ScorePlayer1"] < 0) and not(set_entry["ScorePlayer2"] < 0):
            # DQs are marked on smash.gg as game count -1, so skip don't include DQs
            self.sets.append(set_entry)

    def _get_event_sets(self, event):
        page_number = 1
        per_page = 60
        sets_registered = 0
        event_sets_query = '''
          query tournamentSets($eventID: Int, $page_number: Int, $per_page: Int){
            event(id:$eventID){
              sets(
                page: $page_number
                perPage: $per_page
              ){
                pageInfo{
                  total
                }
                nodes{
                  winnerId
                  id
                  slots{
                    id
                    standing{
                      placement
                      stats{
                        score{
                          value
                        }
                      }
                    }
                    entrant{
                      id
                    }
                  }
                }
              }
            }
          }
        '''
        event_sets = self._post(event_sets_query, {"eventID": event["event_id"], "page_number": page_number,
                                                   "per_page": per_page})
        for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
            self._create_set_entry(value, event["tournament"])
        sets_registered += per_page
        while not sets_registered > event_sets["data"]["event"]["sets"]["pageInfo"]["total"]:
            page_number += 1
            event_sets = self._post(event_sets_query, {"eventID": event["event_id"], "page_number": page_number,
                                                       "per_page": per_page})
            for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                self._create_set_entry(value, event["tournament"])
            sets_registered += per_page

    def _set_participant_placement_per_event(self, raw_data, event):
        for key, value in raw_data:
            1

    def _get_event_participants(self, event):
        event_participants_query = '''
            query EventParticipants($eventID: Int){
            event(id:$eventID){
              entrants(query: {
                page: 1
                perPage: 150
              }){
               nodes{
                  id
                  participants{
                    gamerTag
                  }
                }
              }
              standings(query: {
                page:1
                perPage: 150
              }){
                nodes{
                  id
                  placement
                }
              }
            }
          }
        '''
        participants_response = self._post(event_participants_query, {"eventID": event["event_id"]})
        participants_data = participants_response
        for key, value in enumerate(participants_data["data"]["event"]["entrants"]["nodes"]):
            if self.participants.get(value["id"]) is None:
                self.participants[value["id"]] = value["participants"][0]["gamerTag"]
        # self._set_participant_placement_per_event(enumerate(participants_data["data"]["event"]["standings"]["nodes"]),
        #                                           event["tournament"])

    def _get_tournament_events(self, tournaments, events):
        event_id_list = []
        tournament_query = '''
          query TournamentQuery($tournamentName: String) {
            tournament(slug: $tournamentName){
              id
              name
            events {
                id
                name
              }
            }
          }
        '''
        for tournament in tournaments:
            tournament_query_results = self._post(tournament_query, {"tournamentName": tournament})
            tournaments_response = tournament_query_results
            for key, value in enumerate(tournaments_response["data"]["tournament"]["events"]):
                if value["name"] in events:
                    event_id_list.append({"event_id": value["id"], "tournament": tournament})

        return event_id_list


if __name__ == "__main__":
    listaTorneos = load(open("tournamentList.yml", "r"))
    prueba = TournamentSetsRequest()
    prueba.get_tournament_sets(listaTorneos["tournaments"], listaTorneos["events"])
    prueba.get_participants_placings()
    file = ResultsWorkBook()
    file.register_sets(prueba.sets)
