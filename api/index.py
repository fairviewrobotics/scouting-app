from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Annotated
import json
import os

from .database import Database
from .score import Score

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/json/match_scouting")
async def get_match_scouting_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'match_scouting_data.json')
    with open(file_path, 'r') as file:
        return json.load(file)

@app.put("/api/py/update_data/statbotics/{competition_key}")
async def update_statbotics_data(competition_key: str):
    await Database.update_sb_data(competition_key)

@app.put("/api/py/update_data/blue_alliance/{competition_key}")
async def update_blue_alliance_data(competition_key: str):
    await Database.update_tba_data(competition_key)

# @app.post("/api/py/add_pit_scouting_data/{competition_key}")
# async def add_pit_scouting_data(data: dict, competition_key: str):
#     Database.add_pit_data(data, competition_key)

@app.get("/api/py/data/all_teams/{competition_key}")
async def get_all_teams(competition_key: str):
    return await Database.get_all_data(competition_key)

@app.get("/api/py/data/single_team/{team_number}/{competition_key}")
async def get_single_team(team_number: int, competition_key: str):
    return await Database.get_single_row(competition_key, "team_number", team_number)

@app.get("/api/py/data/weighted_all_teams/{competition_key}/{weights}")
async def get_weighted_all_teams(competition_key: str, weights: str):
    return await Score.get_sorted_teams_and_data(competition_key, json.loads(weights))

@app.put("/api/py/update_data/set_up_competition/{competition_key}")
async def set_up_competition(competition_key: str):
    await Database.set_up_competition(competition_key)









