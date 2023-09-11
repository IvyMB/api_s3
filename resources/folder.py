from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
import dotenv
import os

from services import S3Service
from services import DatabaseService
from schemas import FolderSchema
from auth.authorization import token_exists_in_database


class FolderResource(Resource):
    def __init__(self):
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.db = DatabaseService()
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

    def post(self):
        token_is_valid = self.custom_authorization(request)
        if not token_is_valid:
            return {"message": "Invalid token.", "Content": []}, 400

        # Validar e deserializar os dados de solicitação usando o esquema
        try:
            validated_data = FolderSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages}, 400

        foldername = validated_data.get('foldername')

        # Encontrar o arquivo no s3
        success, file_content = self.s3_client.create_folder(foldername=foldername)

        if success:
            return {"message": "Folder successfully created.", "Content": file_content}, 200
        else:
            return {"message": "Folder not found.", "Content": file_content}, 400
