from ranking import ResultExtractor
from ResultsWorkbook import ResultsWorkBook
from yaml import load
import json

if __name__ == "__main__":
    
    credentials = None
    with open ("credentials.json", "r") as file:
        credentials = json.load(file)
    data = ResultExtractor()

    # Uncomment this if you are going to use challonge data
    #-------------------------------------------------------
    #challonge_data = load(open("challonge.yml", "r"))
    #data.add_client(challonge_data["tournaments"], 
    #                client="challonge",
    #                user=credentials['challonge_user'],
    #                api_key=credentials['challonge'])
    #-------------------------------------------------------


    # Uncomment this if you are going to use startgg data
    #-------------------------------------------------------
    #start_gg_data = load(open("start_gg.yml", "r"))
    #data.add_client(start_gg_data["tournaments"], 
    #                events_list=start_gg_data["event"], 
    #                client="start_gg",
    #                api_key = credentials["start_gg"])
    #-------------------------------------------------------
    
    
    data.get_all_sets()
    data.ranking.assign_set_history()
    data.ranking.check_tag_mismatch()
    data.ranking.remove_duplicates()

    # Run the script until here the first time to get the list of players
    # so you can identify duplicates/variations and merge them as described below
    # You can uncomment below this after you have added as many merges as necessary


    # Merge tags sample
    # After the first execution, put all your merge instructions here.
    # All player tags within the list will be merged into the second argument
    # Example, "Barto", "rickbb", and "elbarto" data will be put into -> "Elbarto"
    #-------------------------------------------------------
    #data.ranking.merge_players(["Barto", "rickbb", "elbarto"],"Elbarto")
    #data.ranking.merge_players(["dodo"], "Dodo")
    #-------------------------------------------------------
    
    data.ranking.sort_by_avg_placing()

    # Uncomment this to put all the data into an xslx file
    #-------------------------------------------------------
    #participants_placings = []
    #for participant in data.ranking.competitors_sorted:
    #    participants_placings.append(participant.get_all_placings())
    #file = ResultsWorkBook()
    #file.create_spreadsheet(data, participants_placings, list(data.events.keys()), name="season stats")
    #-------------------------------------------------------
