class Competitor:
    def __init__(self, id, gamertag, tournaments):
        self.placings = {}
        self.id = id
        self.gamertag = gamertag
        for tournament in tournaments:
            self.placings[tournament] = '-'

    def get_attendance(self):
        total = len(self.placings.keys())
        tournaments_assisted = 0
        for key, value in self.placings.items():
            if not value == '-':
                tournaments_assisted += 1
        print(tournaments_assisted/total)
        return tournaments_assisted/total

    def register_placing(self, tournament, placing):
        self.placings[tournament] = placing

    def get_placings(self):
        print(self.placings)
        return self.placings
