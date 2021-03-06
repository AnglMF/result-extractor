def event_sets_query():
    return '''
          query eventSets($eventID: ID, $page_number: Int, $per_page: Int){
            event(id:$eventID){
              sets(
                page: $page_number
                perPage: $per_page
              ){
                pageInfo{
                    total
                }
                nodes{
                  id
                  round
                  slots{
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
                        gamerTag
                      }
                        seeds{
                            seedNum
                        }
                    }
                  }
                }
              }
            }
          }
        '''


def event_standings_query():
    return '''
            query EventParticipants($eventID: ID){
                event(id:$eventID){
                  standings(query: {
                    page:1
                    perPage: 150
                  }){
                    pageInfo{
                      total
                    }
                    nodes{
                      entrant{
                        participants{
                          player{
                            id
                          }
                          gamerTag
                        }
                        seeds{
                          seedNum
                        }
                      }
                      placement
                    }
                  }
                }
              }
        '''


def event_participants_query():
    return '''
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


def tournament_events_query():
    return '''
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
