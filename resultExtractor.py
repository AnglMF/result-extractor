from graphqlclient import GraphQLClient
import json
from yaml import load

class tournamentResultRequest:

  def __init__(self):
    self.client = GraphQLClient('https://api.smash.gg/gql/alpha')
    self.client.inject_token('Bearer ' + '026d66d8eeb4f1e73aa2ebe750388536')
    variables = ''
    query = ''
    
  def post(self, query, queryVariables):
    result = self.client.execute(query, queryVariables)
    return result

  def getTournamentEvents(self, tournaments):
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
    print(json.loads(tournamentQueryResults))


if __name__ == "__main__":
  listaTorneos = load(open("tournamentList.yml", "r"))
  prueba = tournamentResultRequest()
  prueba.getTournamentEvents(listaTorneos["tournaments"])
