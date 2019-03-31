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
    self.save_workbook("test.xlsx")

  def save_workbook(self, name):
    self.workbook.save(name)


class TournamentSetsRequest:
  eventIDs = []
  participants = {}
  sets = []
  #SetId, Tournament, Player1, Score1, Player2, Score2, Winner

  def __init__(self):
    self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
    self.client.inject_token('Bearer ' + '026d66d8eeb4f1e73aa2ebe750388536')
    
  def post(self, query, queryVariables):
    result = self.client.execute(query, queryVariables)
    resultObject = json.loads(result)
    print(resultObject)
    return resultObject

  def create_set_entry(self, rawData, tournament):
    setEntry = {}
    setEntry["SetID"] = rawData["id"]
    setEntry["Tournament"] = tournament
    setEntry["Player1"] = self.participants[rawData["slots"][0]["entrant"]["id"]]
    setEntry["ScorePlayer1"] = rawData["slots"][0]["standing"]["stats"]["score"]["value"]
    setEntry["Player2"] = self.participants[rawData["slots"][1]["entrant"]["id"]]
    setEntry["ScorePlayer2"] = rawData["slots"][1]["standing"]["stats"]["score"]["value"]
    setEntry["Winner"] = self.participants[rawData["winnerId"]]
    if not(setEntry["ScorePlayer1"]<0) and not(setEntry["ScorePlayer2"]<0):
      #DQs are marked on smash.gg as game count -1, so skip don't include DQs
      self.sets.append(setEntry)

  def get_event_sets(self, eventID, tournament):
    pageNumber = 1
    perPage = 60
    setsRegistered = 0
    eventSetsQuery= '''
      query tournamentSets($eventID: Int, $pageNumber: Int, $perPage: Int){
        event(id:$eventID){
          sets(
            page: $pageNumber
            perPage: $perPage
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
    eventSets = self.post(eventSetsQuery, {"eventID": eventID, "pageNumber": pageNumber, "perPage": perPage})
    for key, value in enumerate(eventSets["data"]["event"]["sets"]["nodes"]):
      self.create_set_entry(value, tournament)
    setsRegistered += perPage
    while not setsRegistered>eventSets["data"]["event"]["sets"]["pageInfo"]["total"]:
      pageNumber += 1
      eventSets = self.post(eventSetsQuery, {"eventID": eventID, "pageNumber": pageNumber, "perPage": perPage})
      for key, value in enumerate(eventSets["data"]["event"]["sets"]["nodes"]):
        self.create_set_entry(value, tournament)
      setsRegistered += perPage
    print(self.sets)

  def get_event_participants(self, eventID):
    eventParticipantsQuery= '''
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
        }
      }
    '''
    participantsResponse = self.post(eventParticipantsQuery, {"eventID": eventID})
    participantsData = (participantsResponse)
    for key, value in enumerate(participantsData["data"]["event"]["entrants"]["nodes"]):
      if self.participants.get(value["id"]) == None:
        self.participants[value["id"]] = value["participants"][0]["gamerTag"]

  def get_tournament_events(self, tournaments, events):
    tournamentQuery = '''
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
      tournamentQueryResults = self.post(tournamentQuery, {"tournamentName": tournament})
      tournamentsResponse = (tournamentQueryResults)
      for key, value in enumerate(tournamentsResponse["data"]["tournament"]["events"]):
        if (value["name"] in events):
          self.eventIDs.append(value["id"])
          self.get_event_participants(value["id"])
          print(self.participants)
          self.get_event_sets(value["id"], tournament)


if __name__ == "__main__":
  listaTorneos = load(open("tournamentList.yml", "r"))
  prueba = TournamentSetsRequest()
  prueba.get_tournament_events(listaTorneos["tournaments"], listaTorneos["events"])
  file = ResultsWorkBook()
  file.register_sets(prueba.sets)
