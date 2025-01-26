import os
import asyncio
import json
from sqlalchemy import text
from dotenv import load_dotenv
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Float, Boolean, text
from sqlalchemy.types import TypeEngine
import tba_statbotics

load_dotenv()



# DATABASE SETUP

tmpPostgres = urlparse(os.getenv("DATABASE_URL"))
engine = create_async_engine(f"postgresql+asyncpg://{tmpPostgres.username}:{tmpPostgres.password}@{tmpPostgres.hostname}{tmpPostgres.path}?ssl=require", echo=True)

metadata = MetaData()

# Mapping between JSON types and SQLAlchemy types
SQLALCHEMY_TYPE_MAP = {
    "Integer": Integer,
    "String": String,
    "DateTime": DateTime,
    "Float": Float,
    "Boolean": Boolean
}


# DATABASE FUNCTIONS

async def create_table_from_json(json_file: str, table_name: str, primary_db_key) -> bool:
    """
    Creates a MongoDB table from a JSON file.

    Args:
        json_file (str): JSON file to create table from.
        table_name (str): Name of the table to create.

    Returns:
        bool: Database operation completion.
    """
    try:
        # Load schema from JSON
        with open(json_file, "r") as f:
            schema = json.load(f)
        
        # Create the 'teams' table
        table_columns = []
        for column_name, column_type in schema.items():
            sql_type: TypeEngine = SQLALCHEMY_TYPE_MAP.get(column_type)
            if not sql_type:
                raise ValueError(f"Unsupported column type: {column_type}")
            # Add columns, make "Team Number" a primary key if it fits
            table_columns.append(
                Column(column_name.replace(" ", "_").lower(), sql_type, primary_key=(column_name == primary_db_key))
            )

        Table(table_name, metadata, *table_columns)
        print(f"Prepared to create table 'teams' with columns: {', '.join([col.name for col in table_columns])}")

        # Create the table in the database
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        print(f"Table {table_name} created.")
        return True
    except Exception as e:
        print(f"Failed to create table: {e}")
        return False
    finally:
        await engine.dispose()

### Insert Operation
async def insert_data(table_name: str, data: list[dict]) -> bool:
    """Inserts data into a table.

    Args:
        table_name (str): The name of the table to insert data into.
        data (list[dict]): The data to insert into the table.

    Returns:
        bool: Database operation completion.
    """
    try:
        async with engine.begin() as conn:
            for row in data:
                columns = ', '.join(row.keys())
                values = ', '.join([f":{key}" for key in row.keys()])
                query = text(f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})')
                await conn.execute(query, row)
        print("Data inserted.")
        return True
    except Exception as e:
        print(f"Failed to insert data: {e}")
        return False
    finally:
        await engine.dispose()

### Query Operation
async def query_data(table_name: str) -> list[dict]:
    """Queries data from a table.

    Args:
        table_name (str): The name of the table to query data from.

    Returns:
        list[dict]: The queried data.
    """
    try:
        async with engine.connect() as conn:
            query = text(f'SELECT * FROM "{table_name}"')
            result = await conn.execute(query)
            rows = result.fetchall()
            print(f"Queried data: {rows}")
            return [dict(row._mapping) for row in rows]
    except Exception as e:
        print(f"Failed to query data: {e}")
        return []
    finally:
        await engine.dispose()

### Query Single Row Operation
async def query_single_row(table_name: str, primary_key: str, primary_key_value) -> dict:
    """Queries a single row of data from a table using the primary key.

    Args:
        table_name (str): The name of the table to query data from.
        primary_key (str): The name of the primary key column.
        primary_key_value: The value of the primary key to query.

    Returns:
        dict: The queried row as a dictionary.
    """
    try:
        async with engine.connect() as conn:
            query = text(f'SELECT * FROM "{table_name}" WHERE "{primary_key}" = :primary_key_value')
            result = await conn.execute(query, {"primary_key_value": primary_key_value})
            row = result.fetchone()
            if row:
                print(f"Queried row: {row}")
                return dict(row._mapping)
            else:
                print(f"No row found with {primary_key} = {primary_key_value}")
                return {}
    except Exception as e:
        print(f"Failed to query data: {e}")
        return {}
    finally:
        await engine.dispose()

async def query_single_column(table_name: str, column_name: str) -> list:
    """Gets all values of a single column from a table.

    Args:
        table_name (str): The name of the table to query data from.
        column_name (str): The name of the column to get values from.

    Returns:
        list: The values of the specified column.
    """
    try:
        async with engine.connect() as conn:
            query = text(f'SELECT "{column_name}" FROM "{table_name}"')
            result = await conn.execute(query)
            rows = result.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        print(f"Failed to get column values: {e}")
        return []
    finally:
        await engine.dispose()

### Update Operation
async def update_data(table_name: str, condition: dict, update_values: dict) -> bool:
    """Updates data in a table that matches the specified condition.

    Args:
        table_name (str): The name of the table to update data in.
        condition (dict): The condition to update data based on.
        update_values (dict): The values to update.

    Returns:
        bool: Database operation completion.
    """
    try:
        table = metadata.tables[table_name]
        async with engine.begin() as conn:
            condition_clause = " AND ".join(f"{k} = :{k}" for k in condition.keys())
            set_clause = ", ".join(f"{k} = :{k}" for k in update_values.keys())
            query = text(f'UPDATE "{table_name}" SET {set_clause} WHERE {condition_clause}')
            await conn.execute(query, {**condition, **update_values})
        print("Data updated.")
        return True
    except Exception as e:
        print(f"Failed to update data: {e}")
        return False
    finally:
        await engine.dispose()

async def update_data(table_name: str, data: list[dict]) -> bool:
    """
    Updates the Statbotics data in the database.

    Args:
        table_name (str): The name of the table to update data in.
        data (list[dict]): A list of dictionaries, each containing a team_number and other values to update.

    Returns:
        bool: Database operation completion.
    """
    try:
        async with engine.begin() as conn:
            for row in data:
                team_number = row.pop("team_number")
                condition = {"team_number": team_number}
                condition_clause = " AND ".join(f"{k} = :{k}" for k in condition.keys())
                set_clause = ", ".join(f"{k} = :{k}" for k in row.keys())
                query = text(f'UPDATE "{table_name}" SET {set_clause} WHERE {condition_clause}')
                await conn.execute(query, {**condition, **row})
        print("Data updated.")
        return True
    except Exception as e:
        print(f"Failed to update data: {e}")
        return False
    finally:
        await engine.dispose()

### Delete Operation
async def delete_data(table_name: str, condition: dict) -> bool:
    """Deletes data from a table that matches the specified condition.

    Args:
        table_name (str): The name of the table to delete data from.
        condition (dict): The condition to delete data based on.

    Returns:
        bool: Database operation completion.
    """
    try:
        async with engine.begin() as conn:
            condition_clause = " AND ".join(f"{k} = :{k}" for k in condition.keys())
            query = text(f'DELETE FROM "{table_name}" WHERE {condition_clause}')
            await conn.execute(query, condition)
        print("Data deleted.")
        return True
    except Exception as e:
        print(f"Failed to delete data: {e}")
        return False
    finally:
        await engine.dispose()

### Delete Table Operation
async def delete_table(table_name: str) -> bool:
    """Deletes a table from the database.

    Args:
        table_name (str): The name of the table to delete.

    Returns:
        bool: Database operation completion.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        print("Table deleted.")
        return True
    except Exception as e:
        print(f"Failed to delete table: {e}")
        return False
    finally:
        await engine.dispose()

### Drop and Create Table Operation
async def drop_and_create_table_from_json(json_file: str, table_name: str, primary_db_key="team_number") -> bool:
    """Drops and recreates a table from a JSON file.

    Args:
        json_file (str): JSON file to create table from.
        table_name (str): Name of the table to create.

    Returns:
        bool: Database operation completion.
    """
    try:
        # Drop the table
        await delete_table(table_name)

        # Create the table
        await create_table_from_json(json_file, table_name, primary_db_key)
        return True
    except Exception as e:
        print(f"Failed to drop and create table: {e}")
        return False

# FUNCTIONS TO BE USED BY API ENDPOINTS

schema_path = "/Users/aadit/Documents/GitHub/scouting-app-backend/api/schema.json"
scouting_schema_path = "/Users/aadit/Documents/GitHub/scouting-app-backend/api/scouting_schema.json"


class Database:

    
    
    @staticmethod
    def set_up_main_database(table_name: str):
        """
        Sets up the main database by creating tables from JSON files.
        """

        # Check if the schema.json file exists
        if not os.path.exists(schema_path):
            print(f"File not found: {schema_path}")
            return

        asyncio.run(drop_and_create_table_from_json(schema_path, table_name))

    @staticmethod
    def set_up_other_database(table_name: str, json_path: str, primary_db_key):
        """
        Sets up the database by creating tables from JSON files.
        """
       
        

        # Check if the schema.json file exists
        if not os.path.exists(json_path):
            print(f"File not found: {json_path}")
            return

        asyncio.run(drop_and_create_table_from_json(json_path, table_name, primary_db_key))

    @staticmethod
    def clear_schema():
        
        initdict = {
            "team_number": "Integer",
            "team_name": "String",
            "rank": "Integer",
            "winrate": "Float",
            "overall_epa": "Float",
            "auto_epa": "Float",
            "teleop_epa": "Float",
            "endgame_epa": "Float"
        }

        with open(schema_path, 'w') as file:
            json.dump(initdict, file, indent=4)

    @staticmethod
    def update_schema(dict : dict, clear_schema=False):
        """Updates the schema of the database with a dictionary of items to be added.

        Args:
            dict (dict): List of items to be added to the schema.
            clear_schema (bool, optional): Whether to clear the schema before updating. Defaults to False.
        """

        if clear_schema:
            Database.clear_schema()

        # Load the existing JSON data
        with open(schema_path, 'r') as file:
            schema = json.load(file)

        schema.update(dict)

        # Save the updated data back to the JSON file
        with open(schema_path, 'w') as file:
            json.dump(schema, file, indent=4)


    @staticmethod
    def set_up_competition(competition_key: str):
        """
        Sets up the competition by tables for all teams using TBA data.

        Args:
            competition_key (str): The competition key to set up.
        """

        team_numbers = tba_statbotics.get_list_of_team_numbers(competition_key)
        k = []
        for i in range(len(team_numbers)):
            k.append({
                "team_number": team_numbers[i],
            })
        asyncio.run(insert_data(competition_key, k))


    @staticmethod
    def update_sb_data(competition_key: str):
        """
        Updates the Statbotics data in the database.

        Args:
            competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
        """
        newData = tba_statbotics.get_new_sb_data(competition_key)
        asyncio.run(update_data(competition_key, newData))

    @staticmethod
    def update_tba_data(competition_key: str):
        """
        Updates the TBA data in the database.

        Args:
            competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
        """

        newData = tba_statbotics.get_new_tba_data(competition_key)
        asyncio.run(update_data(competition_key, newData))

    @staticmethod
    def insert_sb_data(competition_key: str):
        """
        Updates the Statbotics data in the database.

        Args:
            competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
        """
        newData = tba_statbotics.get_new_sb_data(competition_key)
        asyncio.run(insert_data(competition_key, newData))

    @staticmethod
    def insert_tba_data(competition_key: str):
        """
        Updates the TBA data in the database.

        Args:
            competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
        """

        newData = tba_statbotics.get_new_tba_data(competition_key)
        asyncio.run(insert_data(competition_key, newData))

    @staticmethod
    def add_match_scouting_data(data: dict, competition_key: str):
        """
        Adds match scouting data to the database.

        Args:
            data (dict): The data to add.
            competition_key (str): The competition key to add data for. Format: "yyyyCOMP_CODE"
        """
        asyncio.run(insert_data(competition_key + "_match_scouting", [data]))

    @staticmethod
    def remove_match_scouting_data(condition: dict, competition_key: str):
        """
        Removes match scouting data from the database.

        Args:
            data (dict): The data to remove.
            competition_key (str): The competition key to remove data for. Format: "yyyyCOMP_CODE"
        """
        asyncio.run(delete_data(competition_key + "_match_scouting", condition))

    @staticmethod
    def update_main_db_from_match_scouting_db(competition_key: str):
        """
        Updates the main database from the match scouting database.

        Args:
            competition_key (str): The competition key to update data for. Format: "yyyyCOMP_CODE"
        """
        match_scouting_data = asyncio.run(query_data(competition_key + "_match_scouting"))
        team_numbers = tba_statbotics.get_list_of_team_numbers(competition_key)

        with open(scouting_schema_path, 'r') as file:
            scouting_schema = json.load(file)
        
        scouting_schema.pop("entry_id")
        scouting_schema.pop("scout_name")
        scouting_schema.pop("match_number")
        scouting_schema.pop("team_number")

        for key in scouting_schema:
            scouting_schema[key] = 0.0

        to_add = []
        
        for team in team_numbers:
            team_dict_sum = scouting_schema.copy()
            team_dict_count = {key: 0 for key in scouting_schema}
            for entry in match_scouting_data:
                if entry["team_number"] == team:
                    for key in team_dict_sum:
                        if isinstance(entry[key], bool):
                            team_dict_sum[key] += int(entry[key])
                        else:
                            team_dict_sum[key] += entry[key]
                        team_dict_count[key] += 1

            to_add.append({
                "team_number": team,
                **{key: (team_dict_sum[key] / team_dict_count[key]) if team_dict_count[key] != 0 else 0 for key in team_dict_sum}
            })

        asyncio.run(update_data(competition_key, to_add))

    @staticmethod
    def get_single_column(table_name: str, column_name: str):
        """
        Gets all values of a single column from a table.

        Args:
            table_name (str): The name of the table to query data from.
            column_name (str): The name of the column to get values from.

        Returns:
            list: The values of the specified column.
        """
        return asyncio.run(query_single_column(table_name, column_name))
    
    @staticmethod
    def get_single_row(table_name: str, primary_key: str, primary_key_value):
        """
        Queries a single row of data from a table using the primary key.

        Args:
            table_name (str): The name of the table to query data from.
            primary_key (str): The name of the primary key column.
            primary_key_value: The value of the primary key to query.

        Returns:
            dict: The queried row as a dictionary.
        """
        return asyncio.run(query_single_row(table_name, primary_key, primary_key_value))
    
    @staticmethod
    def get_all_data(table_name: str):
        """
        Queries data from a table.

        Args:
            table_name (str): The name of the table to query data from.

        Returns:
            list[dict]: The queried data.
        """
        return asyncio.run(query_data(table_name))
            

    

if __name__ == "__main__":
    Database.update_main_db_from_match_scouting_db("2024code")

    # Database.set_up_main_database("2024code")
    # Database.set_up_competition("2024code")
    # Database.update_sb_data("2024code")
    # Database.update_tba_data("2024code")
    
                


            