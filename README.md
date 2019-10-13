# Extractor de resultados de torneos de smash.gg
Este pequeño programa acepta como entrada una lista de torneos de smash.gg
y te regresa en conjunto información relevante sobre los torneos listados.

## Información
Acutalmente regresa:
* Listado de todos los sets jugados
* Listado de todos los participantes y su placing

# Usage

You should add the smash.gg tournament URLs in the "tournamentList.yml" file.
Currently only smash.gg URLs are supported.

Running ```python resultExtractory.py``` shoud generate an xsls file with the relevant information
from the tournaments listed in the tournamentList.yml file.

## Modules


## Classes

### TournamentSetsRequest
#### Properties
- auth_token
- client
- events
- ranking
- participants_dict
- sets
#### Methods
- ##### ```get_tournament_sets(tournaments, events)```
  - _tournaments_: List. smash.gg URLs of tournaments
  - _events_: Events of the tournament that will be crawled.

  Will extract all of the played sets for the specified event of the provided tournaments.
  The results of this procedure will be stored in the ```sets``` property


### Ranking
#### Properties
- _total_sets_:
- _competitors_: List[]. Contains a list of all competitors extracted from each tournemant's events.
- ___qualified_competitors_: List[]
- ___unqualified_competitors_: List[]

#### Methods
- ##### ```sort_by_avg_placing()```
  Will sort the ```competitors``` list by their ```average``` property.

- ##### ```set_assistance_requirement(**kwargs)```
  Supported keyword arguments are:
  - tournament_number: Int.
  - assistance_percentage: Int.

  Will filter competitors into qualified and unqualified, based on the argument provided.
  Qualified competitors will end in the ```competitors``` list, while competitors that do not meet the specified
  criteria will end up in the ```__unqualified_competitors``` property.
  
  Assistance percentage ranges from 0 to 100.

- ##### ```assign_set_history_to_top_15_players```

  Populates the ```__sets``` property of the top 15 competitors with the highest ```average``` property value.



