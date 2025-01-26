from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Annotated
import json

from database import Database
from score import Score

app = FastAPI()

@app.get("/json/match_scouting")
async def get_match_scouting_json():
    with open("../api/match_scouting.json", 'r') as file:
        return json.load(file)

@app.put("/update_data/statbotics/{competition_key}")
async def update_statbotics_data(competition_key: str):
    Database.update_sb_data(competition_key)

@app.put("/update_data/blue_alliance/{competition_key}")
async def update_blue_alliance_data(competition_key: str):
    Database.update_tba_data(competition_key)

# @app.post("/add_pit_scouting_data/{competition_key}")
# async def add_pit_scouting_data(data: dict, competition_key: str):
#     Database.add_pit_data(data, competition_key)

@app.get("/data/all_teams/{competition_key}")
async def get_all_teams(competition_key: str):
    return Database.get_all_data(competition_key)

@app.get("/data/single_team/{team_number}/{competition_key}")
async def get_single_team(team_number: int, competition_key: str):
    return Database.get_single_row(competition_key, "team_number", team_number)

@app.get("/data/weighted_all_teams/{competition_key}/{weights}")
async def get_weighted_all_teams(competition_key: str, weights: str):
    return Score.get_sorted_teams_and_data(competition_key, json.loads(weights))







