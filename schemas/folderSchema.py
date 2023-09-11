from marshmallow import Schema, fields


class FolderSchema(Schema):
    foldername = fields.Str(required=True)
