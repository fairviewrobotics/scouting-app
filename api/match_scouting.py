import json
import database
from database import Database
import hashlib
import random
import tba_statbotics
import string

match_scouting_json_path = "/Users/aadit/Documents/GitHub/scouting-app-backend/api/match_scouting.json"
scouting_schema_path = "/Users/aadit/Documents/GitHub/scouting-app-backend/api/scouting_schema.json"

def get_entry_id(name: str, match_number: int) -> str:

    name = name + str(match_number)
    # Use SHA-256 to generate a hash of the name
    hash_object = hashlib.sha256(name.encode())
    # Convert the hash to a hexadecimal string
    hex_dig = hash_object.hexdigest()
    
    return hex_dig

def clear_questions():
        
    initdict = [
        {
            "question": "Scout Name",
            "name": "scout_name",
            "type": "String"
        },
        {
            "question": "Match Number",
            "name": "match_number",
            "type": "Integer"
        },
        {
            "question": "Team Number",
            "name": "team_number",
            "type": "Integer"
        },
        {
            "question": "Breakdown?",
            "name": "breakdown",
            "type": "Boolean",
            "score_pref": "false"
        }
    ]

    with open(match_scouting_json_path, 'w') as file:
        json.dump(initdict, file, indent=4)


def update_questions(list : list[dict], clear=False):
    """Updates the schema of the database with a dictionary of items to be added.

    Args:
        list (list[dict]): List of items to be added to the schema.
        clear (bool, optional): Whether to clear the questions before updating. Defaults to False.
    """

    if clear:
        clear_questions()

    # Load the existing JSON data
    with open(match_scouting_json_path, 'r') as file:
        questions = json.load(file)

    # Add the new items to the existing data
    questions[-1:-1] = list

    # Save the updated data back to the JSON file
    with open(match_scouting_json_path, 'w') as file:
        json.dump(questions, file, indent=4)
    
def update_schema_from_questions(clear=False):
    with open(match_scouting_json_path, 'r') as file:
        questions = json.load(file)
    
    filtered_questions = [question for question in questions if "score_pref" in question]

    add = {}
    for question in filtered_questions:
        add[question["name"]] = "Float"
    
    Database.update_schema(add, clear)

def set_up_scouting_db(competition_key: str):
    with open(match_scouting_json_path, 'r') as file:
        questions = json.load(file)
    
    set_up_dict = {"entry_id": "String"}
    for question in questions:
        set_up_dict[question["name"]] = question["type"]
    
    with open(scouting_schema_path, 'w') as scouting_schema:
        json.dump(set_up_dict, scouting_schema, indent=4)

    Database.set_up_other_database(competition_key + "_match_scouting", scouting_schema_path, "entry_id")

def add_match_scouting_data(data: dict, competition_key: str):

    new = {
        **{"entry_id": get_entry_id(data["scout_name"], data["match_number"])},
        **data
    }

    Database.add_match_scouting_data(new, competition_key)

def remove_match_scouting_data(entry_id: str, competition_key: str):
    Database.remove_match_scouting_data({"entry_id": entry_id}, competition_key)

def get_single_match_scouting_data(entry_id: str, competition_key: str):
    return database.query_single_row(f"{competition_key}_match_scouting", "entry_id", entry_id)

def get_all_match_scouting_data(competition_key: str):
    return database.query_database(f"{competition_key}_match_scouting")


    
    
if __name__ == '__main__':

    for i in range(1, 50):
        k = {
            "scout_name": ''.join(random.choices(string.ascii_letters,
                             k=5)),
            "match_number": random.randint(1, 49),
            "team_number": random.choice(tba_statbotics.get_list_of_team_numbers("2024code")),
            "auto_notes": random.randint(0, 8),
            "teleop_notes": random.randint(0, 8),
            "notes_passed": random.randint(0, 8),
            "climbed": bool(random.getrandbits(1)),
            "breakdown": bool(random.getrandbits(1))
        }
        add_match_scouting_data(k, "2024code")
