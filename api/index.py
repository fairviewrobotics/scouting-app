from fastapi import FastAPI
import json

### Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}

@app.get("/api/py/json/match_scouting")
async def get_match_scouting_json():
    with open("../api/match_scouting.json", 'r') as file:
        return json.load(file)