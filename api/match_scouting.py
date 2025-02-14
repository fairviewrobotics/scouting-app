import json
import hashlib
import random
import string
import os
import sys
from . import database
from . import tba_statbotics
# import database
# import tba_statbotics

base_dir = os.path.dirname(os.path.abspath(__file__))
match_scouting_json_path = os.path.join(base_dir, 'match_scouting_data.json')

def get_entry_id(name: str, match_number: int) -> str:

    name = name + str(match_number)
    # Use SHA-256 to generate a hash of the name
    hash_object = hashlib.sha256(name.encode())
    # Convert the hash to a hexadecimal string
    hex_dig = hash_object.hexdigest()
    
    return hex_dig
    
def get_match_scouting_schema():
    with open(match_scouting_json_path, 'r') as file:
        questions = json.load(file)
    
    filtered_questions = [question for question in questions if "score_pref" in question]

    schema = {}
    for question in filtered_questions:
        schema[question["name"]] = "Float"
    
    return schema

async def add_match_scouting_data(data: dict, competition_key: str) -> bool:
    new = {
        **{"entry_id": get_entry_id(data["scout_name"], data["match_number"])},
        **data
    }
    return await database.insert_data(competition_key + "_match_scouting", [data])

async def remove_match_scouting_data(entry_id: str, competition_key: str) -> bool:
    return await database.delete_data(competition_key + "_match_scouting", {"entry_id": entry_id})
    
async def get_single_match_scouting_data(entry_id: str, competition_key: str):
    return await database.query_single_row(f"{competition_key}_match_scouting", "entry_id", entry_id)

async def get_all_match_scouting_data(competition_key: str):
    return await database.query_data(f"{competition_key}_match_scouting")

async def update_main_db_from_match_scouting_db(competition_key: str) -> bool:
    """
    Updates the main database from the match scouting database.

    Args:
        competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
    """
    match_scouting_data = await database.query_data(competition_key + "_match_scouting")
    team_numbers = tba_statbotics.get_list_of_team_numbers(competition_key)

    scouting_schema = get_match_scouting_schema()
    
    scouting_schema.pop("entry_id")
    scouting_schema.pop("scout_name")
    scouting_schema.pop("match_number")
    scouting_schema.pop("team_number")

    for key in scouting_schema:
        scouting_schema[key] = 0.0

    to_add = []
    
    for team in team_numbers:
        team_dict_sum = scouting_schema.copy()
        team_dict_count = {key: 0 for key in scouting_schema}
        for entry in match_scouting_data:
            if entry["team_number"] == team:
                for key in team_dict_sum:
                    if isinstance(entry[key], bool):
                        team_dict_sum[key] += int(entry[key])
                    else:
                        team_dict_sum[key] += entry[key]
                    team_dict_count[key] += 1

        to_add.append({
            "team_number": team,
            **{key: (team_dict_sum[key] / team_dict_count[key]) if team_dict_count[key] != 0 else 0 for key in team_dict_sum}
        })

    return await database.update_data(competition_key, to_add)



    
    
if __name__ == '__main__':

    # for i in range(1, 50):
    #     k = {
    #         "scout_name": ''.join(random.choices(string.ascii_letters,
    #                          k=5)),
    #         "match_number": random.randint(1, 49),
    #         "team_number": random.choice(tba_statbotics.get_list_of_team_numbers("2024code")),
    #         "auto_notes": random.randint(0, 8),
    #         "teleop_notes": random.randint(0, 8),
    #         "notes_passed": random.randint(0, 8),
    #         "climbed": bool(random.getrandbits(1)),
    #         "breakdown": bool(random.getrandbits(1))
    #     }
    #     add_match_scouting_data(k, "2024code")

    print(get_match_scouting_schema())
