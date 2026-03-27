import os
from typing import Any, Union

import gridfs
from bson import ObjectId
from django.conf import settings
from pymongo import MongoClient


class GridFSStorage:
    def __init__(self) -> None:
        host = getattr(settings, 'MONGO_HOST', os.environ.get('MONGO_HOST', 'mongo'))
        port = int(getattr(settings, 'MONGO_PORT', os.environ.get('MONGO_PORT', 27017)))
        db_name = getattr(settings, 'MONGO_DB', os.environ.get('MONGO_DB', 'daas_files'))

        client = MongoClient(host=host, port=port)
        database = client[db_name]
        self.fs = gridfs.GridFS(database)

    def upload_file(self, stream: Any, name: str) -> str:
        if hasattr(stream, 'read'):
            content = stream.read()
        else:
            content = stream
        if isinstance(content, str):
            content = content.encode('utf-8')
        return str(self.fs.put(content, filename=name))

    def get_file(self, file_id: str) -> bytes:
        return self.fs.get(ObjectId(file_id)).read()

    def delete_file(self, file_id: str) -> None:
        self.fs.delete(ObjectId(file_id))

    def file_exists(self, file_id: Union[str, None]) -> bool:
        if not file_id:
            return False
        try:
            return bool(self.fs.exists({'_id': ObjectId(file_id)}))
        except Exception:
            return False
