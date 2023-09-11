from marshmallow import Schema, fields


class FilesSchema(Schema):
    foldername = fields.Str(required=True)
    limit = fields.Int()
    page = fields.Int()
