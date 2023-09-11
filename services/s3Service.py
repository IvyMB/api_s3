import boto3
import botocore.exceptions
import base64
import io


class S3Service:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name):

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket_name = bucket_name

    def find_file_in_folder(self, folder_prefix='', filename=''):
        # Use list_objects_v2 para listar objetos na pasta especificada
        list_params = {'Bucket': self.bucket_name, 'Prefix': folder_prefix}
        response = self.s3_client.list_objects_v2(**list_params)

        # Verifique se o arquivo desejado está na lista de objetos
        if 'Contents' in response:
            objects = response['Contents']
            for obj in objects:
                if obj['Key'] == folder_prefix + filename:
                    return True
        return False

    def get_list_files_from_folder(self, folder_prefix='', page=None, limit=None):
        list_params = {'Bucket': self.bucket_name, 'Prefix': folder_prefix}
        start_index = None
        end_index = None

        if page is not None and limit is not None:
            # Calcula o índice de início com base na página e no limite
            start_index = (page - 1) * limit

            # Calcular o índice de fim
            end_index = start_index + limit
            # Adicionar os parâmetros para limitar os resultados
            list_params['MaxKeys'] = end_index
            list_params['MaxKeys'] = limit * page
            list_files = []

            try:
                response = self.s3_client.list_objects_v2(**list_params)
                result = []

                if 'Contents' in response:
                    objects = response['Contents']

                    # Iterando sobre os objetos e imprimindo seus nomes
                    for obj in objects[start_index:end_index]:
                        key = obj['Key']
                        data = {"filename": key}

                        result.append(data)
                    return True, result

                else:
                    content = "Nenhum objeto encontrado na pasta."
                    result.append(content)

                return False, result

            except botocore.exceptions.ClientError as e:
                return False, str(e)

    def download_file(self, file_key=''):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            content = response['Body'].read()
            return True, base64.b64encode(content).decode('utf-8')
        except Exception as e:
            return False, str(e)

    def upload_file(self, filename='', foldername='', base64_file=''):
        try:
            # Decodifica o PDF base64 para bytes
            file_path = f'{foldername}/{filename}'
            pdf_bytes = base64_file.encode('utf-8')

            # Configure a conexão com o Amazon S3
            self.s3_client.upload_fileobj(
                Fileobj=io.BytesIO(pdf_bytes),
                Bucket=self.bucket_name,
                Key=file_path, )

            return True, 'PDF uploaded successfully'

        except Exception as e:
            return False, str(e)

    def create_folder(self, foldername=''):
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=foldername + '/')
            return True, 'File successfully created'

        except Exception as e:
            return False, str(e)

    def folder_exists(self, foldername=''):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=foldername)

            # Verifique se há objetos cujas chaves (keys) têm um prefixo correspondente à pasta
            for obj in response.get('Contents', []):
                if obj['Key'].startswith(foldername):
                    return True

            return False
        except Exception as e:
            return False
