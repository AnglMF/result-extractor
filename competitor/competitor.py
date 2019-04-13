from sets.set_history import SetHistory


class Competitor:
    def __init__(self, id, gamertag, tournaments):
        self.placings = {}
        self.id = id
        self.gamertag = gamertag
        self.average = 0
        self.tournaments_assisted = 0
        self.assistance_percentage = 0
        self.__sets_won = 0
        self.win_percentage = 0
        for tournament in tournaments:
            self.placings[tournament] = '-'
        self.__sets = SetHistory(self.gamertag)

    def __calculate_attendance(self):
        self.assistance_percentage = self.tournaments_assisted/len(self.placings.keys()) * 100

    def register_placing(self, tournament, placing):
        self.placings[tournament] = placing
        self.tournaments_assisted += 1
        self.__calculate_attendance()

    def get_avg_placing(self):
        total_value = 0
        for placing in self.placings.values():
            if not placing == '-':
                total_value += placing
        self.average = total_value/self.tournaments_assisted
        return self.average

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
            else:
                raise ValueError
            if not set_history:
                print('No sets Found')
            return set_history
        except ValueError:
            print('Invalid Option')

    def as_dict(self):
        competitor_dict = {}
        competitor_dict['id'] = self.id
        competitor_dict['name'] = self.gamertag
        competitor_dict['avg_placing'] = self.average
        for tournament in self.placings.keys():
            competitor_dict[tournament] = self.placings[tournament]

    def win_percentage(self):
        return self.__sets.get_win_percentage()
