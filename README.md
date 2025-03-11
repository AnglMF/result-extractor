# How to use
## Setup an environment for the project
```bash
$ cd <project directory>
$ python -m venv environment
$ . environment/bin/activate
$ pip install -r requirements.txt
```

## Running the tests
```bash
$ python -m unittest unit_tests/*.py
```
A few challonge tests are failing lmao, don't know why even though it works as expected. It's an issue with the tests, not with the module. Ups

## Obtain API keys for the desired platforms
Only challonge and start.gg are supported at this moment.
#### Start GG API token
https://developer.start.gg/docs/authentication

#### Challonge API token
https://challonge.com/settings/developer

Put these tokens into the `credentials.json` file, **also include your challonge username** if you are using challonge.

## Getting the list of events to get data from
### Challonge
Example tournament: `https://challonge.com/gdhqr624`

1. Go to your tournament and get the ID from the URL.
2. Put the ID (in this case example: "gdhqr624") into the `challonge.yml` file in a separate line, between single quotes and with the correct indentation under "Tournaments".

Repeat for every tournament

### Start gg
Example tournament: `https://www.start.gg/tournament/genesis-x2/`

1. Go to the tournament page and get the tournament blob (in this example: "genesis-x2").
2. Put the blob into the `start_gg.yml` file in a separate line, between single quotes and with the correct indentation under "Tournaments".
3. Put the name of the event that you want to get the data from (as an example: 'Melee Singles') under "event". Repeat for every variation you find in every tournament (the event name can vary, for example it could be named "Singles", "SSBM Singles", "Melee Singles", etc. If none of the event names are found in a tournament, no data will be extracted).

------
You can use both challonge and start gg together during an execution, simply add both clients as described in the sample script **before** capturing all data

## Using the data
A sample script is provided that takes all data and outputs an xlsx file. Uncomment the sections as needed to get an excel sheet with data from the tournaments.

