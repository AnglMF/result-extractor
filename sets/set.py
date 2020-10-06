class Set:
    def __init__(self, set_dict, tournament):
        try:
            self.player1 = set_dict["slots"][0]["entrant"]["participants"][0]["gamerTag"]
            self.player2 = set_dict["slots"][1]["entrant"]["participants"][0]["gamerTag"]
            self.player1_id = set_dict["slots"][0]["entrant"]["participants"][0]["player"]["id"]
            self.player2_id = set_dict["slots"][1]["entrant"]["participants"][0]["player"]["id"]
            self.score1 = set_dict["slots"][0]["standing"]["stats"]["score"]["value"]
            self.score2 = set_dict["slots"][1]["standing"]["stats"]["score"]["value"]
            seed1 = set_dict["slots"][0]["entrant"]["seeds"][0]["seedNum"]
            seed2 = set_dict["slots"][1]["entrant"]["seeds"][0]["seedNum"]
            self.result = ""
            self.check_winner(set_dict["slots"][0]["standing"]["placement"], seed1, seed2)
            self.set_id = set_dict["id"]
            self.tournament = tournament
            self.round = abs(set_dict["round"])
        except TypeError:
            print("There's an error with the Set data entry")

    def get_players(self):
        return [self.player1, self.player2]

    def check_winner(self, winner, seed1, seed2):
        if winner != 1:
            temp_player = self.player1
            temp_player_id = self.player1_id
            temp_score = self.score1
            self.player1 = self.player2
            self.player1_id = self.player2_id
            self.score1 = self.score2
            self.player2 = temp_player
            self.player2_id = temp_player_id
            self.score2 = temp_score
            self.result = ""
            if seed2 > seed1:
                self.result = "upset"
            else:
                self.result = "expected"
        else:
            if seed1 > seed2:
                self.result = "upset"
            else:
                self.result = "expected"

    def as_dict(self):
        set_as_dict = {}
        set_as_dict["score1"] = self.score1
        set_as_dict["winner"] = self.player1
        set_as_dict["score2"] = self.score2
        set_as_dict["loser"] = self.player2
        set_as_dict['tournament'] = self.tournament
        set_as_dict["round"] = self.round
        set_as_dict["result"] = self.result
        return set_as_dict
