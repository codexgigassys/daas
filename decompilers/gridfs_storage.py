import os
from typing import Any, Union

import gridfs
from bson import ObjectId
from pymongo import MongoClient


class GridFSStorage:
    def __init__(self) -> None:
        mongo_uri = os.environ.get('MONGO_URI', '')
        if mongo_uri:
            client = MongoClient(mongo_uri)
        else:
            client_kwargs = {
                'host': os.environ.get('MONGO_HOST', 'mongo'),
                'port': int(os.environ.get('MONGO_PORT', 27017)),
            }
            mongo_user = os.environ.get('MONGO_USER', '')
            mongo_password = os.environ.get('MONGO_PASSWORD', '')
            if mongo_user and mongo_password:
                client_kwargs.update({
                    'username': mongo_user,
                    'password': mongo_password,
                    'authSource': os.environ.get('MONGO_AUTH_SOURCE', 'admin'),
                })
            client = MongoClient(**client_kwargs)
        database = client[os.environ.get('MONGO_DB', 'daas_files')]
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


storage = GridFSStorage()
