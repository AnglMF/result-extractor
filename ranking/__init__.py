from ranking.set_history import SetHistory


class Ranking:
    def __init__(self):
        self.total_sets = SetHistory('Global')
        self.competitors = {}
        self.competitors_sorted = []
        self.competitors_tags = []
        self.__qualified_competitors = {}
        self.__unqualified_competitors = {}
        self.unordered = True

    def remove_duplicates(self):
        unique_tags = {*()}
        duplicates_removed = []
        print(f'Removing duplicates...')
        for tag in self.competitors_tags:
            if (tag in unique_tags) and (tag not in duplicates_removed):
                print(f'Found duplicate: {tag}')
                self.remove_duplicate_player(tag)
                duplicates_removed.append(tag)
            else:
                unique_tags.add(tag)
        print('Players after removing duplicates...')
        print(unique_tags)

    def sort_by_avg_placing(self):
        if self.unordered:
            self.unordered = False
            sorted_list = sorted(list(self.competitors.values()), key=lambda competitors: competitors.average)
            self.competitors_sorted = sorted_list

    def set_assistance_requirement(self, **kwargs):
        if kwargs.get("tournament_number"):
            for competitor in list(self.competitors.values()):
                if competitor.tournaments_assisted >= kwargs.get("tournament_number"):
                    self.__qualified_competitors[competitor.id] = competitor
                else:
                    self.__unqualified_competitors[competitor.id] = competitor
        elif kwargs.get("assistance_percentage"):
            for competitor in list(self.competitors.values()):
                if competitor.assistance_percentage >= kwargs.get("assistance_percentage"):
                    self.__qualified_competitors[competitor.id] = competitor
                else:
                    self.__unqualified_competitors[competitor.id] = competitor
        self.competitors = self.__qualified_competitors

    def get_single_tournament_results(self, tournament):
        competitor_list = []
        for competitor in list(self.competitors.values()):
            competitor_dict = competitor.get_tournament_result(tournament)
            if not competitor_dict["placing"] == '-':
                competitor_list.append(competitor_dict)
        sorted_list = sorted(competitor_list, key=lambda competitors: competitors["placing"])
        return sorted_list
    
    def check_tag_mismatch(self):
        needs_correction = []
        for _set in self.total_sets.sets:
            for player in _set.get_players():
                for gamertag in player.values():
                    if gamertag not in self.competitors_tags:
                        if player not in needs_correction:
                            needs_correction.append(player)

        # See who the tags actually belong to
        for mismatch in needs_correction:
                for id in mismatch.keys():
                    print(f'Updating {mismatch[id]} into {self.competitors[id].gamertag}')
                    self.total_sets.update_player_tag(
                        mismatch[id], self.competitors[id].gamertag
                    )
        return

    def assign_set_history(self):
        try:
            for _set in self.total_sets.sets:
                set_dict = _set.as_dict()
                # Assign set to winner of set
                self.competitors[set_dict["winner_id"]].register_set(_set)
                
                # Assign set to loser of set
                self.competitors[set_dict["loser_id"]].register_set(_set)
        except KeyError as e:
            print(f'Error registering the following set:')
            print(_set.as_dict())
            print(e)

    def get_h2h_record(self, competitor_list):
        player_records = []
        for competitor1 in competitor_list:
            player_record_dictionary = {'player': competitor1.gamertag}
            for competitor2 in competitor_list:
                if competitor1 != competitor2:
                    player_record_dictionary[competitor2.gamertag] = competitor1.record_vs(competitor2)
            player_records.append(player_record_dictionary)
        return player_records
    
    def get_games_h2h_record(self, competitor_list):
        player_records = []
        for competitor1 in competitor_list:
            player_record_dictionary = {'player': competitor1.gamertag}
            for competitor2 in competitor_list:
                if competitor1 != competitor2:
                    player_record_dictionary[competitor2.gamertag] = competitor1.record_vs_games(competitor2)
            player_records.append(player_record_dictionary)
        return player_records
    
    def check_inconsistencies(self, competitor1, competitor2):
            set_data1 = competitor1.sets.get_sets_vs(competitor2)
            set_data2 = competitor2.sets.get_sets_vs(competitor1)
            if set_data1 and set_data2:

                if  len(set_data1) != len(set_data2):
                    #print(f'Inconsistency found with {competitor1.gamertag} and {competitor2.gamertag} set data')
                    #print(f'{competitor1} data:')
                    #print(set_data1)
                    #print(f'{competitor2} data:')
                    #print(set_data2)
                    pass
    
    def merge_players(self, old_tags, new_tag):

        for player in list(self.competitors.values()):
            if player.gamertag == new_tag:
                # Found original
                #print(f'Found {player.gamertag}')

                # Search for the copies
                for old_tag in old_tags:
                    #print(old_tag)
                    if old_tag != new_tag:
                        #print(f'Updating set history from {old_tag} into {new_tag}')
                        self.total_sets.update_player_tag(old_tag, new_tag)

                    # Look for every player to see if there is data to update
                    for updating_player in list(self.competitors.values()):
                        
                        if updating_player.gamertag == old_tag:
                            # Found copy
                            #print(f'Found {old_tag}, merging into {new_tag}')
                            if not updating_player == player:
                                # If it's not actually the same player, merge them
                                #print(f'Combining data into {new_tag}')
                                player.combine_data(updating_player)
                                #print(f'Removing {updating_player.gamertag}')
                                self.competitors.pop(updating_player.id)
                                #print(f'Merged player {old_tag} into {new_tag}')
                        elif updating_player.sets.get_sets_vs(old_tag) !="":
                            # Check if there is data to update
                            #print(f'{updating_player.gamertag} has sets with {old_tag}, updating...')
                            updating_player.sets.update_player_tag(old_tag, new_tag)
                            #print(f'Updated set data for {updating_player.gamertag}')
                        else: 
                            pass
                            #print(f'{updating_player.gamertag} has no sets vs {old_tag}')

                        if old_tag != new_tag:
                            self.check_inconsistencies(player, updating_player)    
                break
        return
    
    def remove_duplicate_player(self, tag):
        self.merge_players([tag],tag)
        return