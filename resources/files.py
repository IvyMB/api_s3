from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from marshmallow import ValidationError
import dotenv
import os

from services import S3Service
from schemas import FilesSchema
from services import DatabaseService
from auth.authorization import token_exists_in_database


class FilesResource(Resource):
    def __init__(self):
        self.db = DatabaseService()
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.s3_client = S3Service(
            aws_access_key_id=os.environ.get('ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('SECRET_KEY'),
            bucket_name=os.environ.get('BUCKET_NAME')
        )

    def custom_authorization(self, request):
        # Verifique se o cabeçalho de autorização contém um token
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return {"message": "Token de autorização não fornecido."}, 401

        # Extraia o token do cabeçalho de autorização
        token = authorization_header.split()[-1]

        # Verifique se o token existe no banco de dados
        if not token_exists_in_database(token):
            return {"message": "Token inválido."}, 401

        # Se a autorização for bem-sucedida, continue a solicitação
        return None

    def get(self):
        token_is_valid = self.custom_authorization(request)
        if not token_is_valid:
            return {"message": "Invalid token.", "Content": []}, 400

        # Validar e deserializar os dados de solicitação usando o esquema
        try:
            validated_data = FilesSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages}, 400

        limit = validated_data.get('limit')
        page = validated_data.get('page')
        foldername = validated_data.get('foldername')

        if page is not None and limit is not None:
            # Se ambos `page` e `limit` forem fornecidos, listar com paginação

            page = int(page)
            limit = int(limit)
            success, folder_content = self.s3_client.get_list_files_from_folder(folder_prefix=foldername, page=page,
                                                                                limit=limit)

            # Encontrar a pasta no s3
            if success:
                return {"message": "Folder founded.", "Content": folder_content}, 200
            else:
                return {"message": "Folder not found.", "Content": folder_content}, 400

        else:
            # Se nenhum ou apenas um dos parâmetros for fornecido, listar todos os arquivos
            success, file_content = self.s3_client.get_list_files_from_folder(folder_prefix=foldername)
            if success:
                return {"message": "File founded.", "Content": file_content}, 200
            else:
                return {"message": "File not found.", "Content": file_content}, 400
