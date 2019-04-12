from sets.set import Set


class SetHistory:
    def __init__(self, player):
        self.__sets = []
        self.player = player
        self.__sets_list = []

    def get_sets_won(self):
        sets_won = [set for set in self.__sets if self.player == set.winner]
        return sets_won

    def get_sets_lost(self):
        sets_lost = [set for set in self.__sets if not self.player == set.winner]
        return sets_lost

    def register_set(self, set_data):
        if isinstance(set_data, Set):
            self.__sets.append(set_data)
        else:
            raise ValueError('Invalid set value')

    def get_sets_vs(self, opponent):
        sets_h2h = [set for set in self.__sets if opponent in set.get_players()]
        if not sets_h2h:
            raise ValueError('No sets vs specified player: {op}'.format(op=opponent))
        else:
            return sets_h2h

    def sort_sets(self):
        self.__sets = sorted(self.__sets, key=lambda each_set: each_set.round, reverse=True)

    def get_sets(self):
        return self.__sets

    def get_sets_dict(self):
        self.__sets_list = []
        for set in self.__sets:
            self.__sets_list.append(set.as_dict())
        return self.__sets_list
