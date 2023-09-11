from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from marshmallow import ValidationError
import dotenv
import os

from schemas import FileGetSchema, FilePostSchema
from services import S3Service
from services import DatabaseService
from auth.authorization import token_exists_in_database


class FileResource(Resource):
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

        # Verifique se o token não existe no banco de dados
        if not token_exists_in_database(token):
            return False

        # Se a autorização for bem-sucedida, continue a solicitação
        return True

    def get(self):
        token_is_valid = self.custom_authorization(request)
        if not token_is_valid:
            return {"message": "Invalid token.", "Content": []}, 400

        # Validar e deserializar os dados de solicitação usando o esquema
        try:
            validated_data = FileGetSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages}, 400

        foldername = validated_data['foldername']
        filename = validated_data['filename']

        # Encontrar o arquivo no s3
        file_path = f'{foldername}/{filename}'
        success, file_content = self.s3_client.download_file(file_key=file_path)

        if success:
            return {"message": "File founded.", "Content": file_content}, 200
        else:
            return {"message": "File not found.", "Content": file_content}, 400

    def post(self):
        token_is_valid = self.custom_authorization(request)
        if not token_is_valid:
            return {"message": "Invalid token.", "Content": []}, 400

        # Validar e deserializar os dados de solicitação usando o esquema
        try:
            validated_data = FilePostSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages}, 400

        foldername = validated_data['foldername']
        filename = validated_data['filename']
        content = validated_data['content']

        # Verificar se o arquivo já existe na pasta
        file_exists = self.s3_client.find_file_in_folder(folder_prefix=foldername, filename=filename)

        if file_exists:
            # O arquivo ja existe na pasta especificada
            text = 'The file already exists on this folder'
            return {"message": text}, 201

        # Criar o arquivo na pasta especificada
        success, message = self.s3_client.upload_file(filename=filename, foldername=foldername,
                                                      base64_file=content)

        if success:
            return {"message": message}, 200
        else:
            return {"message": message}, 400

        # Buscar o arquivo  usando a pasta no s3
        # Se existir retornar que esse arquivo ja existe
