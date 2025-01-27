import os
import statbotics
import requests
from dotenv import load_dotenv


dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../api', '.env'))
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

        print(response.json())

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
                winrate = team[1]["qual"]["ranking"]["record"]["wins"] / (team[1]["qual"]["ranking"]["record"]["wins"] + team[1]["qual"]["ranking"]["record"]["losses"])

                list_of_teams.append(winrate)
            return list_of_teams
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def get_new_tba_data(event_key: str) -> list[dict]:
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

def get_team_epa(team_number: int, event_key: str) -> dict:
    sb_dict = sb.get_team_event(team_number, event_key, ["epa_end", "auto_epa_end", "teleop_epa_end", "endgame_epa_end"])

    sb_dict["overall_epa"] = sb_dict.pop("epa_end")
    sb_dict["auto_epa"] = sb_dict.pop("auto_epa_end")
    sb_dict["teleop_epa"] = sb_dict.pop("teleop_epa_end")
    sb_dict["endgame_epa"] = sb_dict.pop("endgame_epa_end")

    return sb_dict

def get_new_sb_data(event_key) -> list[dict]:
    list_of_teams = get_list_of_team_numbers(event_key)
    epas = []
    for team in list_of_teams:
        epas.append({
            **{"team_number": team},
            **get_team_epa(team, event_key)
        })
    return epas


if __name__ == '__main__':
    # print(get_list_of_team_numbers("2024code"))
    # print(get_list_of_team_names("2024code"))
    # print(get_list_of_team_ranks("2024code"))
    # print(get_list_of_team_winrates("2024code"))
    
    print(0 + None)