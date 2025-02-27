import json
from . import database
import os
from . import utils

base_dir = os.path.dirname(os.path.abspath(__file__))
match_scouting_json_path = os.path.join(base_dir, 'match_scouting_data.json')



def z_score(list: list) -> list:
    """
    Calculate the z-score of a list of data points
    """
    if len(list) == 0:
        print("List is empty!!!!!! aaah!!")
        return []
    mean = sum(list) / len(list)
    std_dev = (sum([(value - mean) ** 2 for value in list]) / len(list)) ** 0.5

    if std_dev == 0:
        return [0 for _ in list]

    return [(value - mean) / std_dev for value in list]

def get_column_from_dict(data: list[dict], column_name: str) -> list:
    """Gets all values of a single column from a list of dictionaries.

    Args:
        data (list[dict]): The list of dictionaries to extract the column from.
        column_name (str): The name of the column to get values from.

    Returns:
        list: The values of the specified column.
    """
    try:
        return [row[column_name] for row in data if column_name in row]
    except Exception as e:
        print(f"Failed to get column values: {e}")
        return []
    
def combine_lists_to_dicts(list1: list, list2: list, column_name1: str, column_name2: str) -> list[dict]:
    """Combines two lists into a list of dictionaries based on two column names.

    Args:
        list1 (list): The first list of values.
        list2 (list): The second list of values.
        column_name1 (str): The column name for the first list.
        column_name2 (str): The column name for the second list.

    Returns:
        list[dict]: A list of dictionaries combining the two lists.
    """
    try:
        combined_list = [{column_name1: value1, column_name2: value2} for value1, value2 in zip(list1, list2)]
        return combined_list
    except Exception as e:
        print(f"Failed to combine lists: {e}")
        return []

    
def score(data: list[dict], weights: dict, competition_key: str) -> list[dict]:
    """
    Calculate the score of a team based on the data and weights

    Args:
        data (list[dict]): The data of all teams
        weights (dict): The weights to score by

    Returns:
        float: The score of the team
    """
    schema = utils.get_combined_schema(competition_key)

    with open(match_scouting_json_path, 'r') as file:
        match_scouting_questions = json.load(file)

    schema.pop("team_number")
    schema.pop("team_name")

    z_scores = []

    prefs = dict()
    for key in schema.keys():
        for question in match_scouting_questions:
            if question["name"] == key:
                prefs[key] = 1 if (question["score_pref"] == "high" or question["score_pref"] == "true") else -1
                break
    prefs["rank"] = -1

    for key in schema.keys():
        print(f"Key: {key}")
        column = get_column_from_dict(data, key)
        for i in range(len(column)):
            if column[i] == None:
                column[i] = 0
        pref_column = [value * prefs.get(key, 1) for value in column]
        z = z_score(pref_column)
        z_scores.append(z)

    for i in range(len(z_scores)):
        key = list(schema.keys())[i]
        z_scores[i] = [value * weights.get(key, 1) for value in z_scores[i]]


    print("Lengths of arrays in z_scores:")
    for i, z in enumerate(z_scores):
        print(f"z_scores[{i}] length: {len(z)}")

    # Debugging: Print contents of z_scores
    print("Contents of z_scores:")
    for i, z in enumerate(z_scores):
        print(f"z_scores[{i}]: {z}")    

    weighted_scores = [sum(values) for values in zip(*z_scores)]  





    team_numbers = get_column_from_dict(data, "team_number")

    scores_dict = combine_lists_to_dicts(team_numbers, weighted_scores, "team_number", "score")

    # print("---------------------Scores----------------------")
    # print(weighted_scores)

    # print("---------------------Weighted scores----------------------")
    # print(scores_dict)

    return scores_dict

def get_sorted_teams(data: list[dict], weights: dict, competition_key: str) -> list[dict]:
    """
    Get a list of teams sorted by score

    Args:
        data (list[dict]): The data of all teams
        weights (dict): The weights to score by

    Returns:
        list[dict]: The data of all teams sorted by score
    """

    # Calculate scores and combine with data
    scores_dict = score(data, weights, competition_key)

    # Sort teams based on score
    sorted_teams = sorted(scores_dict, key=lambda x: x["score"], reverse=True)

    # Combine sorted scores with original data
    combined_data = []
    for team in sorted_teams:
        team_data = next(item for item in data if item["team_number"] == team["team_number"])
        combined_data.append({**team_data, "score": team["score"]})

    return combined_data


async def get_sorted_teams_and_data(competition_key: str, weights: dict):
    """
    Get a list of teams sorted by score

    Args:
        comp_key (str): The competition key to get data from
        weights (dict): The weights to score by

    Returns:
        list[dict]: The data of all teams sorted by score
    """
    data = await database.query_data(competition_key)
    return get_sorted_teams(data, weights, competition_key)


