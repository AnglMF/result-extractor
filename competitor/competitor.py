from sets.set_history import SetHistory

POSSIBLE_PLACINGS = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (7, 6), (9, 7), (13, 8), (17, 9), (25, 10), (33, 11),
                     (49, 12), (65, 13), (97, 14), (129, 15)]


class Competitor:
    def __init__(self, id, gamertag, tournaments):
        self.placings = {}  # {tournament: {placing: n, seed: n}}
        self.id = id
        self.gamertag = gamertag
        self.average = 0
        self.tournaments_assisted = 0
        self.assistance_percentage = 0
        self.__sets_won = 0
        self.win_percentage = 0
        for tournament in tournaments:
            self.placings[tournament] = {'placing': '-'}
            self.placings[tournament]["seed"] = '-'
        self.__sets = SetHistory(self.gamertag)

    def __calculate_attendance(self):
        self.assistance_percentage = self.tournaments_assisted/len(self.placings.keys()) * 100

    def register_placing(self, tournament, placing):
        self.placings[tournament]['placing'] = placing["Placing"]
        self.placings[tournament]['seed'] = placing["Seed"]
        self.tournaments_assisted += 1
        self.__calculate_attendance()
        self.__get_avg_placing()

    def __get_avg_placing(self):
        total_value = 0
        for result in self.placings.values():
            if not result["placing"] == '-':
                total_value += result["placing"]
        self.average = total_value/self.tournaments_assisted

    def register_set(self, set_object):
        self.__sets.register_set(set_object)
        if set_object.winner == self.gamertag:
            self.__sets_won += 1

    def sets(self, type, **kwargs):
        try:
            if type == 'won':
                set_history = self.__sets.get_sets_won()
            elif type == 'lost':
                set_history = self.__sets.get_sets_lost()
            elif type == 'vs':
                opponent = kwargs.get('opponent')
                set_history = self.__sets.get_sets_vs(opponent)
            elif type == 'all':
                set_history = self.__sets.get_sets()
            else:
                raise ValueError
            if not set_history:
                print('No sets Found')
            return set_history
        except ValueError:
            print('Invalid Option')

    def get_single_tournament_result(self, tournament):
        competitor_dict = self.__get_main_data()
        competitor_dict[tournament + ' placing'] = self.placings[tournament]["placing"]
        competitor_dict[tournament + ' seed'] = self.placings[tournament]["seed"]
        competitor_dict[tournament + ' difference'] = self.calculate_difference(self.placings[tournament]["seed"],
                                                                                self.placings[tournament]["placing"])
        return competitor_dict



    def __get_main_data(self):
        competitor_dict = {}
        print(self.gamertag)
        competitor_dict['id'] = self.id
        competitor_dict['name'] = self.gamertag
        competitor_dict['avg_placing'] = self.average
        return competitor_dict


    def as_dict(self):
        competitor_dict = self.__get_main_data()
        for tournament in self.placings.keys():
            competitor_dict[tournament] = self.placings[tournament]["placing"]
        return competitor_dict

    def win_percentage(self):
        return self.__sets.get_win_percentage()

    def calculate_difference(self, seed, placement):
        expected = 0
        previous = 0
        actual = 0
        value = 0
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
        value = expected-actual
        if value > 0:
            value = '+' + str(value)
        return value

    def __str__(self):
        return self.gamertag + self.id
