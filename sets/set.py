class Set:
    def __init__(self, set_dict, tournament):
        self.player1 = set_dict["slots"][0]["entrant"]["participants"][0]["gamerTag"]
        self.player2 = set_dict["slots"][1]["entrant"]["participants"][0]["gamerTag"]
        self.player1_id = set_dict["slots"][0]["entrant"]["participants"][0]["playerId"]
        self.player2_id = set_dict["slots"][1]["entrant"]["participants"][0]["playerId"]
        self.score1 = set_dict["slots"][0]["standing"]["stats"]["score"]["value"]
        self.score2 = set_dict["slots"][1]["standing"]["stats"]["score"]["value"]
        self.set_id = set_dict["id"]
        self.tournament = tournament
        self.winner = self.__get_winner(set_dict["slots"][0]["standing"]["placement"])
        self.round = abs(set_dict["round"])

    def get_players(self):
        return [self.player1, self.player2]

    def __get_winner(self, p1_placement):
        if p1_placement == 1:
            winner = self.player1
        else:
            winner = self.player2
        return winner

    def as_dict(self):
        set_as_dict = {}
        set_as_dict["score1"] = self.score1
        set_as_dict["p1"] = self.player1
        set_as_dict["score2"] = self.score2
        set_as_dict["p2"] = self.player2
        set_as_dict["winner"] = self.winner
        set_as_dict['tournament'] = self.tournament
        set_as_dict["round"] = self.round
        return set_as_dict

    def get_round(self):
        return abs(self.round)
