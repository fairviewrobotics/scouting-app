# Pit scouting data
# Gets taken in from FastAPI, processed into score, fed into database

# The Blue Alliance Data
# Gets taken in from TBA API, processed into score, fed into database

# Statbotics Data
# Gets taken in from Statbotics API, processed into score, fed into database

# Each team has its own score that gets updated every time new data comes in

# Pit scouting comes in based on sources determined by the json file

# Blue alliance/Stabotics data keys are different, so we just take the ones that stay the same only: EPA, etc. 

# main.py contains all API endpoints
# - update statbotics data : PUT
# - update blue alliance data : PUT
# - add pit scouting data : POST
# - retrieve data for one team : GET
# - retrieve list of all teams with stats: GET
# - retrieve list of teams with stats based on weights : GET
# - update weights : PUT

# Statbotics and TBA data is stored in the Vercel Postgres database as the raw data, as well as a z-score based standardization calculated for
# all the data. This is done to ensure that the data is standardized to the same scale. When the data is updated, the z-score is recalculated. 
# When pit scouting data is added, the z-score is also recalculated.

# The score for each team is calculated by taking the z-score of each data point, multiplying it by the weight of that data point, and summing
# all the data points together. Weights are store in a json file that can be updated by the user through the API.


# Todo:
# - Implement match scouting data DONE
#  - Update main database from scouting database DONE
# - Scoring algorithm 
# - API endpoints
# - Edit file paths
# - Frontend
#  - Set up page
#  - Team list
#  - Pit scouting page
# - Clean up backend code
# - Robot photos
# - Other team info input (capabilities, autos, etc.) - pit scouting
# - Data can be kept between remaps of the database

# Todo SETUP FOR USER
# - Input competition key
# - Input match scouting questions
