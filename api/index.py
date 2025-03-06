from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel, create_model
from typing import List, Annotated, Dict, Optional
import json
import os
from . import score
from . import database
from . import tba_statbotics
from . import match_scouting
from . import pit_scouting
from . import utils

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

class WeightsRequest(BaseModel):
    weights: Dict[str, float]

@app.get("/api/py/json/match_scouting")
async def get_match_scouting_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'match_scouting_data.json')
    with open(file_path, 'r') as file:
        return json.load(file)
    
@app.get("/api/py/json/pit_scouting")
async def get_pit_scouting_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'pit_scouting_data.json')
    with open(file_path, 'r') as file:
        return json.load(file)
    
@app.get("/api/py/json/schema")
async def get_schema_json():
    return utils.get_combined_schema("2025code")

@app.put("/api/py/update_data/statbotics/{competition_key}")
async def update_statbotics_data(competition_key: str):
    result = await tba_statbotics.update_sb_data(competition_key)
    return {
        "status": result
    }

@app.put("/api/py/update_data/blue_alliance/{competition_key}")
async def update_blue_alliance_data(competition_key: str):
    result = await tba_statbotics.update_tba_data(competition_key)
    return {
        "status": result
    }

# @app.post("/api/py/add_pit_scouting_data/{competition_key}")
# async def add_pit_scouting_data(data: dict, competition_key: str):
#     database.add_pit_data(data, competition_key)

@app.get("/api/py/data/all_teams/{competition_key}")
async def get_all_teams(competition_key: str):
    return await database.query_data(competition_key)

@app.get("/api/py/data/single_team/{team_number}/{competition_key}")
async def get_single_team(team_number: int, competition_key: str):
    return await database.query_single_column(competition_key, "team_number", team_number)

@app.post("/api/py/data/weighted_all_teams/{competition_key}")
async def get_weighted_all_teams(competition_key: str, request: WeightsRequest):
    try:
        weights = request.weights
        result = await score.get_sorted_teams_and_data(competition_key, weights)
        print(result)
        return result
    except Exception as e:
        print(f"Error in get_weighted_all_teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/py/update_data/set_up_competition/{competition_key}")
async def set_up_competition(competition_key: str):
    result1 = await database.create_main_table(competition_key)
    result2 = await database.set_up_scouting_db(competition_key)
    result3 = await tba_statbotics.set_up_competition(competition_key)
    result4 = await database.set_up_pit_scouting_db(competition_key)
    return {
        "status": result1 and result2 and result3 and result4,
        "creating_main_table": result1,
        "setting_up_scouting_db": result2,
        "setting_up_competition": result3,
        "setting_up_pit_scouting_db": result4
    }

@app.post("/api/py/update_data/add_match_scouting/{competition_key}")
async def add_match_scouting(competition_key: str, data: dict):
    return await match_scouting.add_match_scouting_data(data, competition_key)

@app.put("/api/py/update_data/remove_match_scouting/{name}/{match_number}/{competition_key}")
async def remove_match_scouting(name: str, match_number: int, competition_key: str):
    return await match_scouting.remove_match_scouting_data(match_scouting.get_entry_id(name, match_number), competition_key)

@app.get("/api/py/data/single_match_scouting/{name}/{match_number}/{competition_key}")
async def get_single_match_scouting(name: str, match_number: int, competition_key: str):
    return await match_scouting.get_single_match_scouting_data(match_scouting.get_entry_id(name, match_number), competition_key)

@app.put("/api/py/update_data/main_db_from_match_scouting/{competition_key}")
async def update_main_db_from_match_scouting(competition_key: str):
    return await match_scouting.update_main_db_from_match_scouting_db(competition_key)



@app.post("/api/py/update_data/add_pit_scouting/{competition_key}")
async def add_pit_scouting(competition_key: str, data: dict):
    print(f"Received data: {data}")  # Debugging log
    return await pit_scouting.add_pit_scouting_data(data, competition_key)


@app.put("/api/py/update_data/remove_pit_scouting/{team_number}/{competition_key}")
async def remove_pit_scouting(team_number: int, competition_key: str):
    return await pit_scouting.remove_pit_scouting_data(team_number, competition_key)

@app.get("/api/py/data/single_pit_scouting/{team_number}/{competition_key}")
async def get_single_match_scouting(team_number: int, competition_key: str):
    return await pit_scouting.get_single_pit_scouting_data(team_number, competition_key)



