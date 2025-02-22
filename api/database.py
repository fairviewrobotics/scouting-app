import os
import asyncio
import json
from sqlalchemy import text
from dotenv import load_dotenv
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Float, Boolean, text
from sqlalchemy.types import TypeEngine

from . import utils
# import utils


dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '.env.local'))
print("Loading .env file from:", dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

base_dir = os.path.dirname(os.path.abspath(__file__))
match_scouting_json_path = os.path.join(base_dir, 'match_scouting_data.json')


# DATABASE SETUP

tmpPostgres = urlparse(os.getenv("DATABASE_URL"))
if tmpPostgres == None: 
    tmpPostgres = urlparse(os.environ.get('DATABASE_URL'))
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



async def create_main_table(competition_key) -> bool:
    """
    Creates the main Postgres table for all data storage.

    Args:
        competition_key (str): The competition key to create the table for.

    Returns:
        bool: Database operation completion.
    """
    try:
        # Load schema from JSON
        schema = utils.get_combined_schema(competition_key)
        
        # Create the 'teams' table
        table_columns = []
        for column_name, column_type in schema.items():
            sql_type: TypeEngine = SQLALCHEMY_TYPE_MAP.get(column_type)
            if not sql_type:
                raise ValueError(f"Unsupported column type: {column_type}")
            # Add columns, make "Team Number" a primary key if it fits
            table_columns.append(
                Column(column_name.replace(" ", "_").lower(), sql_type, primary_key=(column_name == "team_number"))
            )

        Table(competition_key, metadata, *table_columns)
        print(f"Prepared to create table 'teams' with columns: {', '.join([col.name for col in table_columns])}")

        # Create the table in the database
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        print(f"Table {competition_key} created.")
        return True
    except Exception as e:
        print(f"Failed to create table: {e}")
        return False
    finally:
        await engine.dispose()


async def set_up_scouting_db(competition_key: str):
    with open(match_scouting_json_path, 'r') as file:
        questions = json.load(file)
    
    set_up_dict = {"entry_id": "String"}
    for question in questions:
        set_up_dict[question["name"]] = question["type"]

    try:
        # Load schema from JSON
        schema = set_up_dict
        
        # Create the 'teams' table
        table_columns = []
        for column_name, column_type in schema.items():
            sql_type: TypeEngine = SQLALCHEMY_TYPE_MAP.get(column_type)
            if not sql_type:
                raise ValueError(f"Unsupported column type: {column_type}")
            # Add columns, make "Team Number" a primary key if it fits
            table_columns.append(
                Column(column_name.replace(" ", "_").lower(), sql_type, primary_key=(column_name == "entry_id"))
            )

        Table(competition_key + "_match_scouting", metadata, *table_columns)
        print(f"Prepared to create table 'teams' with columns: {', '.join([col.name for col in table_columns])}")

        # Create the table in the database
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        print(f"Table {competition_key} created.")
        return True
    except Exception as e:
        print(f"Failed to create table: {e}")
        return False
    finally:
        await engine.dispose()




# DATABASE FUNCTIONS


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
    print("DATABASE_URL:", os.getenv("DATABASE_URL"))
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

# FUNCTIONS TO BE USED BY API ENDPOINTS

base_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(base_dir, 'schema.json')
scouting_schema_path = os.path.join(base_dir, 'scouting_schema.json')
                

    

if __name__ == "__main__":
    # Database.update_main_db_from_match_scouting_db("2024code")

    # Database.set_up_main_database("2024code")
    # Database.set_up_competition("2024code")
    # Database.update_sb_data("2024code")
    # Database.update_tba_data("2024code")
    asyncio.run(create_main_table("2025code"))
    
                


            