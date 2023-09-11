from services import DatabaseService


def token_exists_in_database(token):
    # Consultar o banco de dados para verificar a existência do token
    db = DatabaseService()
    result = db.check_token(token_id=token)
    if result is not None:
        return True
    return False
