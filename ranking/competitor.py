from ranking.set_history import SetHistory

POSSIBLE_PLACINGS = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (7, 6), (9, 7), (13, 8), (17, 9), (25, 10), (33, 11),
                     (49, 12), (65, 13), (97, 14), (129, 15)]


def calculate_performance(seed, placement):
    expected = 0
    previous = 0
    actual = 0
    try:
        for placing in POSSIBLE_PLACINGS:
            if seed >= placing[0]:
                previous = placing
            else:
                expected = previous[1]
                break
        for placing in POSSIBLE_PLACINGS:
            if placement >= placing[0]:
                previous = placing
            else:
                actual = previous[1]
                break
    except TypeError:
        return '-'

    value = expected - actual
    if value > 0:
        value = '+' + str(value)
    return value


class Competitor:
    def __init__(self, id, gamertag, tournaments):
        self.placings = {}  # {tournament: {placing: n, seed: n}}
        self.id = id
        self.gamertag = gamertag
        self.average = 0
        self.tournaments_assisted = 0
        self.assistance_percentage = 0
        self.sets_won = 0
        for tournament in tournaments:
            self.placings[tournament] = {'placing': '-'}
            self.placings[tournament]["seed"] = '-'
        self.sets = SetHistory(self.gamertag)

    def __calculate_attendance(self):
        self.assistance_percentage = self.tournaments_assisted/len(self.placings.keys()) * 100

    def register_placing(self, tournament, placing):
        self.placings[tournament]['placing'] = placing["placing"]
        self.placings[tournament]['seed'] = placing["seed"]
        self.tournaments_assisted += 1
        self.__calculate_attendance()
        if placing["placing"] != '-':
            self.__get_avg_placing()

    def __get_avg_placing(self):
        total_value = 0
        for result in self.placings.values():
            if not result["placing"] == '-':
                total_value += result["placing"]
        if total_value > 0:
            self.average = total_value/self.tournaments_assisted
        else:
            self.average = 1000

    def register_set(self, set_object):
        self.sets.register_set(set_object)

    def get_sets(self, category, **kwargs):
        try:
            if category == 'won':
                set_history = self.sets.get_sets_won()
            elif category == 'lost':
                set_history = self.sets.get_sets_lost()
            elif category == 'vs':
                opponent = kwargs.get('opponent')
                set_history = self.sets.get_sets_vs(opponent)
            elif category == 'all':
                set_history = self.sets.get_sets()
            else:
                raise ValueError
            if not set_history:
                print('No sets Found')
            return set_history
        except ValueError:
            print('Invalid Option')

    def get_tournament_result(self, tournament):
        competitor_dict = self.__get_main_data()
        try:
            competitor_dict['placing'] = self.placings[tournament]["placing"]
            competitor_dict['seed'] = self.placings[tournament]["seed"]
            competitor_dict['performance'] = calculate_performance(self.placings[tournament]["seed"],
                                                                   self.placings[tournament]["placing"])
        except KeyError as e:
            print("error with performance/results data for " + competitor_dict["name"])
            print(e)
            competitor_dict['placing'] = '-'
            competitor_dict['seed'] = '-'
            competitor_dict['performance'] = '-'
        return competitor_dict

    def __get_main_data(self):
        competitor_dict = {}
        competitor_dict['id'] = self.id
        competitor_dict['name'] = self.gamertag
        competitor_dict['avg_placing'] = self.average
        return competitor_dict

    def get_all_placings(self):
        competitor_dict = self.__get_main_data()
        self.sets.update_win_percentage()
        competitor_dict['win_perc'] = self.sets.win_percentage
        for tournament in self.placings.keys():
            competitor_dict[tournament] = self.placings[tournament]["placing"]
        return competitor_dict

    def record_vs(self, opponent):
        if isinstance(opponent, Competitor):
            return self.sets.get_set_record_vs_id(opponent)
        else:
            return self.sets.get_set_record_vs_gamertag(opponent)
        
    def record_vs_games(self, opponent):
        if isinstance(opponent, Competitor):
            return self.sets.get_games_record_vs_id(opponent)
        else:
            return self.sets.get_games_record_vs_gamertag(opponent)
    
    
    def combine_data(self, competitor_clone):
        # Add the placings of the "clone" to the competitor object
        for tournament in competitor_clone.placings.keys():
            if not competitor_clone.placings[tournament]["placing"]=="-":
                self.register_placing(tournament, 
                                      competitor_clone.placings[tournament])
        
        # Register all sets from the clone to the competitor object
        for _set in competitor_clone.sets.sets:
            self.register_set(_set)
            
        # Update the playertag on all sets newly registered
        self.sets.update_player_tag(competitor_clone.gamertag,
                                                self.gamertag)
        return

    def __str__(self):
        return self.gamertag
