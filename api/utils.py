from . import tba_statbotics
from . import match_scouting
# import tba_statbotics
# import match_scouting

def combine_dicts(dict_list) -> dict:
    """
    Combine a list of dictionaries into a single dictionary without repeating keys.

    Args:
        dict_list (list[dict]): List of dictionaries to combine.

    Returns:
        dict: Combined dictionary.
    """
    combined_dict = {}
    for d in dict_list:
        combined_dict.update(d)
    return combined_dict


def get_combined_schema(competition_key):
    """
    Get the schema of the combined data from TBA and match scouting.

    Returns:
        dict: The schema of the combined data.
    """
    schema = combine_dicts([
            tba_statbotics.get_tba_keys(), 
            tba_statbotics.get_sb_keys(competition_key),
            match_scouting.get_match_scouting_schema()
            ])
    return schema