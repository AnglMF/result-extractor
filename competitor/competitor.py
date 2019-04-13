from sets.set_history import SetHistory

class Competitor:
    def __init__(self, id, gamertag, tournaments):
        self.placings = {}
        self.id = id
        self.gamertag = gamertag
        for tournament in tournaments:
            self.placings[tournament] = '-'
        self.__sets = SetHistory(self.gamertag)

    def get_attendance(self):
        total = len(self.placings.keys())
        tournaments_assisted = 0
        for key, value in self.placings.items():
            if not value == '-':
                tournaments_assisted += 1
        return tournaments_assisted/total

    def register_placing(self, tournament, placing):
        self.placings[tournament] = placing

    def get_placings(self):
        return self.placings

    def register_set(self, set_object):
        self.__sets.register_set(set_object)

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
