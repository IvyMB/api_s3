import mysql.connector
import dotenv
import os


class DatabaseUtils:
    def __init__(self):
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.db_host = str(os.environ.get('HOST_DB'))
        self.db_database = str(os.environ.get('DATABASE_DB'))
        self.db_user = str(os.environ.get('USER_DB'))
        self.db_password = str(os.environ.get('PASSWORD_DB'))

    def connect(self):
        con = mysql.connector.connect(
            host=self.db_host, user=self.db_user, password=self.db_password,
            database=self.db_database)
        return con

    def execute_unique_search_query(self, query, params=None):
        connection = self.connect()  # Conexão no banco de dados
        cursor = connection.cursor()

        # Se os parametros não estiverem vazios enviar os parametros
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result

        except Exception as e:
            print('Erro ao atualizar os dados:', e)
            return None

        finally:
            if connection:
                connection.close()
