from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import dotenv
import os

from resources import FileResource
from resources import FilesResource
from resources import FolderResource

app = Flask(__name__)
api = Api(app)

dotenv.load_dotenv(dotenv.find_dotenv())
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
jwt = JWTManager(app)

api.add_resource(FileResource, "/file")
api.add_resource(FilesResource, "/files")
api.add_resource(FolderResource, "/folder")


if __name__ == "__main__":
    app.run(debug=True)
