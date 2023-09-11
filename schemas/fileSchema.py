from marshmallow import Schema, fields


class FileGetSchema(Schema):
    foldername = fields.Str(required=True)
    filename = fields.Str(required=True)


class FilePostSchema(Schema):
    foldername = fields.Str(required=True)
    filename = fields.Str(required=True)
    content = fields.Str(required=True)
