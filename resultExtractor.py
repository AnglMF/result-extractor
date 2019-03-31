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


class Participant:
    placings = []
    id = None
    name = ''

    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.placings = []

    def set_tournaments_list(self, tournaments):
        for tournament in tournaments:
            self.placings.append({tournament: "-"})

    def set_tournament_placing(self, tournament, result):
        for placing in self.placings:
            placing[tournament] = result

    def get_info(self):
        print('ID: {id}\nName: {name}\n Placings:\n{placings}'.format(id=self.id,name=self.name,
                                                                      placings=self.placings))


class TournamentSetsRequest:
    events = []  # {event_id, tournament}
    participants = []  # Id, gamerTag, {tournament, placing}
    sets = []  # {SetId, Tournament, Player1, Score1, Player2, Score2, Winner}
    cache_responses = {}

    def __init__(self):
        self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
        self.client.inject_token('Bearer ' + '026d66d8eeb4f1e73aa2ebe750388536')

    def _log(self, _message, _object):
        print('{msg}:\n{obj}'.format(msg=_message, obj=_object))

    def _post(self, query_name,  query, query_variables):
        result = self.client.execute(query, query_variables)
        result_object = json.loads(result)
        self.cache_responses[query_name] = result_object
        self._log("Query Response", result_object)
        return result_object

    def _get_participants_dict(self):
        participants_dict = {}
        for participant in self.participants:
            participants_dict[participant.id] = participant.name
        return participants_dict

    def get_tournament_sets(self, tournaments, event):
        self.events = self._get_tournament_events(tournaments, event)
        for event in self.events:
            self._get_event_participants(event)
            self._log("Participant list", self.participants)
            self._get_event_sets(event)
            self._set_participant_placement_per_event(event)
            self._log("Participants with placings", self.participants)

        self._log("cache", self.cache_responses)

    def _create_set_entry(self, raw_data, tournament):
        participants_dict = self._get_participants_dict()
        set_entry = {}
        set_entry["SetID"] = raw_data["id"]
        set_entry["Tournament"] = tournament
        set_entry["Player1"] = participants_dict[raw_data["slots"][0]["entrant"]["id"]]
        set_entry["ScorePlayer1"] = raw_data["slots"][0]["standing"]["stats"]["score"]["value"]
        set_entry["Player2"] = participants_dict[raw_data["slots"][1]["entrant"]["id"]]
        set_entry["ScorePlayer2"] = raw_data["slots"][1]["standing"]["stats"]["score"]["value"]
        set_entry["Winner"] = participants_dict[raw_data["winnerId"]]
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
            for key, value in enumerate(event_sets["data"]["event"]["sets"]["nodes"]):
                self._create_set_entry(value, event["tournament"])
            sets_registered += per_page

    def set_participant_placement(self, participant_id, event, placement):
        for participant in self.participants:
            if participant.id == participant_id:
                participant.set_tournament_placing(event["tournament"], placement)


    def _set_participant_placement_per_event(self, event):
        for key, value in enumerate(self.cache_responses["event participants"]["data"]["event"]["standings"]["nodes"]):
            self.set_participant_placement(value["entrant"]["id"], event, value["placement"])

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
                  entrant{
                    id
                  }
                  placement
                }
              }
            }
          }
        '''
        participants_response = self._post("event participants", event_participants_query,
                                           {"eventID": event["event_id"]})
        participants_data = participants_response
        for key, value in enumerate(participants_data["data"]["event"]["entrants"]["nodes"]):
            participant = Participant(value["participants"][0]["gamerTag"], value["id"])
            if participant not in self.participants:
                participant.set_tournaments_list(listaTorneos["tournaments"])
                self.participants.append(participant)
            del participant

        self._log("participantes", self.participants)
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
            tournament_query_results = self._post("tournament events", tournament_query, {"tournamentName": tournament})
            tournaments_response = tournament_query_results
            for key, value in enumerate(tournaments_response["data"]["tournament"]["events"]):
                if value["name"] in events:
                    event_id_list.append({"event_id": value["id"], "tournament": tournament})

        return event_id_list


if __name__ == "__main__":
    listaTorneos = load(open("tournamentList.yml", "r"))
    prueba = TournamentSetsRequest()
    prueba.get_tournament_sets(listaTorneos["tournaments"], listaTorneos["events"])
    file = ResultsWorkBook()
    file.register_sets(prueba.sets)
