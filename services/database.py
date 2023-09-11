import mysql.connector
import dotenv
import os

from dependencies.databaseUtils import DatabaseUtils


class DatabaseService:
    def __init__(self):
        self.db = DatabaseUtils()
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.token_table = os.environ.get('TOKEN_TABLE')

    def check_token(self, token_id=''):
        query = f"SELECT token FROM {self.token_table} WHERE token = %s"
        params = (token_id,)
        data = self.db.execute_unique_search_query(query, params=params)
        return data
