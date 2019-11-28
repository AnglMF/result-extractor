from sets.set import Set


class SetHistory:
    def __init__(self, player):
        self.sets = []
        self.player = player
        self.__unsorted = False
        self.total_set_count = 0

    def get_win_percentage(self):
        return len(self.get_sets_won())/self.total_set_count

    def get_sets_won(self):
        self.__sort_sets()
        sets_won = [set for set in self.sets if self.player == set.winner]
        return self.get_sets_dict_list(sets_won)

    def get_sets_lost(self):
        self.__sort_sets()
        sets_lost = [set for set in self.sets if not self.player == set.winner]
        return self.get_sets_dict_list(sets_lost)

    def register_set(self, set_object):
        try:
            if isinstance(set_object, Set):
                self.__unsorted = True
                self.sets.append(set_object)
                self.total_set_count += 1
            else:
                raise ValueError
        except ValueError:
            print('Invalid set Value')

    def get_sets_vs(self, opponent):
        self.__sort_sets()
        sets_h2h = [set for set in self.sets if opponent in set.get_players()]
        if not sets_h2h:
            raise ValueError('No sets vs specified player: {op}'.format(op=opponent))
        else:
            return self.get_sets_dict_list(sets_h2h)

    def get_set_record_vs(self, opponent):
        ret = ""
        try:
            sets = [set for set in self.sets if opponent in set.get_players()]
            won = 0
            lost = 0
            for set in sets:
                if set.winner == opponent:
                    lost += 1
                else:
                    won += 1
            if not(won == 0 and lost == 0):
                ret = str(won) + "-" + str(lost)
        except ValueError:
            pass
        finally:
            return ret

    def __sort_sets(self):
        if self.__unsorted:
            self.__unsorted = False
            self.sets = sorted(self.sets, key=lambda each_set: each_set.round, reverse=True)

    def get_sets(self):
        self.__sort_sets()
        return self.get_sets_won() + self.get_sets_lost()

    def get_sets_dict_list(self, set_list):
        self.__sort_sets()
        requested_sets_as_dict_list = []
        for set in set_list:
            requested_sets_as_dict_list.append(set.as_dict())
        return requested_sets_as_dict_list
