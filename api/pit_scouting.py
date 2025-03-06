import json
import hashlib
import random
import string
import os
import sys
from . import database
from fastapi import UploadFile
from . import tba_statbotics
# import database
# import tba_statbotics

base_dir = os.path.dirname(os.path.abspath(__file__))
pit_scouting_json_path = os.path.join(base_dir, 'pit_scouting_data.json')

    
def get_pit_scouting_schema():
    with open(pit_scouting_json_path, 'r') as file:
        questions = json.load(file)

    schema = {}
    for question in questions:
        schema[question["name"]] = question["type"]
    
    return schema

async def add_pit_scouting_data(data: dict, competition_key: str) -> bool:

    return await database.insert_data(competition_key + "_pit_scouting", [data])

async def remove_pit_scouting_data(team_number: int, competition_key: str) -> bool:
    return await database.delete_data(competition_key + "_pit_scouting", {"team_number": team_number})
    
async def get_single_pit_scouting_data(team_number: int, competition_key: str):
    return await database.query_single_row(f"{competition_key}_pit_scouting", "team_number", team_number)



    



