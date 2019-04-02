from graphqlclient import GraphQLClient
from yaml import load
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment

import pandas
import json


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
        df = df.sort_values("Avg Placing")
        for r in dataframe_to_rows(df, index=True, header=True):
            self.worksheet.append(r)
        for cell in self.worksheet['A'] + self.worksheet[1]:
            cell.style = 'Pandas'
        print(df)

    def register_sets(self, info):
        self.worksheet.title = "Sets Head 2 Head"
        df = pandas.DataFrame.from_dict(info)
        orden = ["ScorePlayer1", "Player1", "Player2", "ScorePlayer2", "Tournament", "SetID"]
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


class Participant:
    placings = []
    id = None
    name = ''

    def __init__(self, name, player_id):
        self.name = name
        self.id = player_id
        self.placings = {}

    def average_placing(self):
        tournament_number = 0
        total_placings = 0
        for key, value in self.placings.items():
            if not value == '-':
                total_placings += value
                tournament_number += 1
        return total_placings/tournament_number

    def set_tournaments_list(self, tournaments):
        for tournament in tournaments:
            self.placings[tournament] = "-"

    def set_tournament_placing(self, tournament, result):
            self.placings[tournament] = result

    def get_info(self):
        print('ID: {id}\nName: {name}\n Placings:\n{placings}'.format(id=self.id, name=self.name,
                                                                      placings=self.placings))

    def as_dict(self):
        object_dict = {}
        object_dict["Id"] = self.id
        object_dict["GamerTag"] = self.name
        for key, value in self.placings.items():
            object_dict[key] = value
        object_dict["Avg Placing"] = self.average_placing()
        return object_dict

    def equals(self, doppleganger):
        if self.id == doppleganger.id:
            return True
        else:
            return False


class TournamentSetsRequest:
    auth_token = 'YOUR TOKEN HERE'
    events = []             # {event_id, tournament}
    participants = []       # Id, gamerTag, {tournament, placing}
    participants_dict = {}
    sets = []               # {SetId, Tournament, Player1, Score1, Player2, Score2, Winner}
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
        for registered_participant in self.participants:
            udpated_dict[registered_participant.id] = registered_participant.name
        self.participants_dict = udpated_dict

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
        set_entry = {}
        set_entry["SetID"] = raw_data["id"]
        set_entry["Tournament"] = tournament
        set_entry["Player1"] = \
            self.participants_dict[raw_data["slots"][0]["entrant"]["participants"][0]["player"]["id"]]
        set_entry["ScorePlayer1"] = raw_data["slots"][0]["standing"]["stats"]["score"]["value"]
        set_entry["Player2"] = \
            self.participants_dict[raw_data["slots"][1]["entrant"]["participants"][0]["player"]["id"]]
        set_entry["ScorePlayer2"] = raw_data["slots"][1]["standing"]["stats"]["score"]["value"]
        # set_entry["Winner"] = participants_dict[raw_data["winnerId"]]
        if not(set_entry["ScorePlayer1"] < 0) and not(set_entry["ScorePlayer2"] < 0):
            # DQs are marked on smash.gg as game count -1, so skip don't include DQs
            self.sets.append(set_entry)

    def _get_event_sets(self, event):
        page_number = 1
        per_page = 49
        sets_registered = 0
        event_sets_query = '''
          query tournamentSets($eventID: ID, $page_number: Int, $per_page: Int){
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
                      participants{
                        player{
                          id
                        }
                      }
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
        for nemo_participant in self.participants:
            if nemo_participant.id == participant_id:
                nemo_participant.set_tournament_placing(event["tournament"], placement)

    def _set_participant_placement_per_event(self, event):
        response = self._get_event_standings(event)
        for key, value in enumerate(response["data"]["event"]["standings"]["nodes"]):
            self.set_participant_placement(value["entrant"]["participants"][0]["player"]["id"], event,
                                           value["placement"])

    def _get_event_standings(self, event):
        event_standings_query = '''
            query EventParticipants($eventID: ID){
            event(id:$eventID){
              standings(query: {
                page:1
                perPage: 150
              }){
                nodes{
                  entrant{
                    participants{
                      player{
                        id
                      }
                    }
                  }
                  placement
                }
              }
            }
          }
        '''
        participants_response = self._post("event standings", event_standings_query,
                                           {"eventID": event["event_id"]})
        return participants_response

    def _get_event_participants(self, event):
        event_participants_query = '''
            query EventParticipants($eventID: ID){
            event(id:$eventID){
              entrants(query: {
                page: 1
                perPage: 150
              }){
               nodes{
                  id
                  participants{
                    gamerTag
                    player{
                      id
                    }
                  }
                }
              }
            }
          }
        '''
        participants_response = self._post("event participants", event_participants_query,
                                           {"eventID": event["event_id"]})
        participants_data = participants_response
        new_participant = None
        for key, value in enumerate(participants_data["data"]["event"]["entrants"]["nodes"]):
            del new_participant
            new_participant = Participant(
                value["participants"][0]["gamerTag"], value["participants"][0]["player"]["id"])
            if new_participant.id not in self.participants_dict.keys():
                new_participant.set_tournaments_list(listaTorneos["tournaments"])
                self.participants.append(new_participant)

        self._update_participants_dict()

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
        tournament_query_response = ''
        for tournament in tournaments:
            try:
                tournament_query_response = self._post("tournament events", tournament_query,
                                                       {"tournamentName": tournament})
                event_found = 0
                self._log('Looking for events:\n{events}'.format(events=events), '')
                for key, value in enumerate(tournament_query_response["data"]["tournament"]["events"]):
                    self._log("'{ev}' event on {t}".format(ev=value["name"], t=tournament), '')
                    if value["name"] in events:
                        event_id_list.append({"event_id": value["id"], "tournament": tournament})
                        event_found = 1
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
    file.register_sets(prueba.sets)
    data = []
    for participant in prueba.participants:
        data.append(participant.as_dict())
    file.register_placings(data)
    file.save_workbook("haber.xlsx")
