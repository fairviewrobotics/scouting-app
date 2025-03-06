import os
import statbotics
import requests
from dotenv import load_dotenv
import json
from . import database
# import database


dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '.env.local'))
print("Loading .env file from:", dotenv_path)
load_dotenv(dotenv_path=dotenv_path)
apiKey = os.getenv("TBA_API_KEY")
if apiKey == None: 
    apiKey = os.environ.get('TBA_API_KEY')

sb = statbotics.Statbotics()

def get_list_of_team_numbers(event_key: str) -> list[int]:
    url = f'https://www.thebluealliance.com/api/v3/event/{event_key}/teams/simple'
    headers = {
        "accept": "application/json",
        "X-TBA-Auth-Key": apiKey
    }

    list_of_teams = []

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                list_of_teams.append(int(post['key'][3::]))
            return list_of_teams
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def get_list_of_team_names(event_key: str) -> list[str]:
    url = f'https://www.thebluealliance.com/api/v3/event/{event_key}/teams/simple'
    headers = {
        "accept": "application/json",
        "X-TBA-Auth-Key": apiKey
    }

    list_of_teams = []

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                list_of_teams.append(post['nickname'])
            return list_of_teams
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
    
def get_list_of_team_ranks(event_key: str) -> list[int]:
    url = f'https://www.thebluealliance.com/api/v3/event/{event_key}/teams/statuses'
    headers = {
        "accept": "application/json",
        "X-TBA-Auth-Key": apiKey
    }

    list_of_teams = []

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            posts = response.json()
            for team in posts.items():
                if team[1] == None or team[1]["qual"] == None:
                    list_of_teams.append(1)
                else:
                    list_of_teams.append(team[1]["qual"]["ranking"]["rank"])
            return list_of_teams
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
    

def get_list_of_team_winrates(event_key: str) -> list[int]:
    url = f'https://www.thebluealliance.com/api/v3/event/{event_key}/teams/statuses'
    headers = {
        "accept": "application/json",
        "X-TBA-Auth-Key": apiKey
    }

    list_of_teams = []

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            posts = response.json()
            for team in posts.items():
                if team[1] == None or team[1]["qual"] == None:
                    list_of_teams.append(0)
                else:
                    winrate = team[1]["qual"]["ranking"]["record"]["wins"] / (team[1]["qual"]["ranking"]["record"]["wins"] + team[1]["qual"]["ranking"]["record"]["losses"])

                    list_of_teams.append(winrate)
            return list_of_teams
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def get_tba_data(event_key: str) -> list[dict]:
    team_numbers = get_list_of_team_numbers(event_key)
    team_names = get_list_of_team_names(event_key)
    team_ranks = get_list_of_team_ranks(event_key)
    team_winrates = get_list_of_team_winrates(event_key)

    k = []
    for i in range(len(team_numbers)):
        k.append({
            "team_number": team_numbers[i],
            "team_name": team_names[i],
            "rank": team_ranks[i],
            "winrate": team_winrates[i]
        })

    return k

def get_team_sb_data(team_number: int, event_key: str) -> dict:
    sb_dict = sb.get_team_event(team_number, event_key, ["epa"])["epa"]["breakdown"]
    return sb_dict

def get_sb_data(event_key) -> list[dict]:
    list_of_teams = get_list_of_team_numbers(event_key)
    epas = []
    for team in list_of_teams:
        epas.append({
            **{"team_number": team},
            **get_team_sb_data(team, event_key)
        })
    return epas

def get_sb_keys(event_key) -> dict:
    list_of_teams = get_list_of_team_numbers(event_key)
    return {key: "Float" for key in get_team_sb_data(list_of_teams[0], event_key).keys()}

def get_tba_keys() -> dict:
    return {
        "team_number": "Integer",
        "team_name": "String",
        "rank": "Integer",
        "winrate": "Float"
    }




# * DATABASE STUFF TO FIX

async def set_up_competition(competition_key: str) -> bool:
    """
    Sets up the competition by tables for all teams using TBA data.

    Args:
        competition_key (str): The competition key to set up.
    """

    team_numbers = get_list_of_team_numbers(competition_key)
    k = []
    for i in range(len(team_numbers)):
        k.append({
            "team_number": team_numbers[i],
        })
    return await database.insert_data(competition_key, k)

async def update_sb_data(competition_key: str):
    """
    Updates the Statbotics data in the database.

    Args:
        competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
    """
    newData = get_sb_data(competition_key)
    return await database.update_data(competition_key, newData)

async def update_tba_data(competition_key: str) -> bool: 
    """
    Updates the TBA data in the database.

    Args:
        competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
    """

    newData = get_tba_data(competition_key)
    return await database.update_data(competition_key, newData)





if __name__ == '__main__':
    # print(get_list_of_team_numbers("2024code"))
    # print(get_list_of_team_names("2024code"))
    # print(get_list_of_team_ranks("2024code"))
    # print(get_list_of_team_winrates("2024code"))
    # print(get_sb_keys("2024code"))
    print(get_tba_keys())