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
        mongo_uri = getattr(settings, 'MONGO_URI', os.environ.get('MONGO_URI', ''))
        mongo_user = getattr(settings, 'MONGO_USER', os.environ.get('MONGO_USER', ''))
        mongo_password = getattr(settings, 'MONGO_PASSWORD', os.environ.get('MONGO_PASSWORD', ''))
        mongo_auth_source = getattr(settings, 'MONGO_AUTH_SOURCE', os.environ.get('MONGO_AUTH_SOURCE', 'admin'))

        if mongo_uri:
            client = MongoClient(mongo_uri)
        else:
            client_kwargs = {'host': host, 'port': port}
            if mongo_user and mongo_password:
                client_kwargs.update({
                    'username': mongo_user,
                    'password': mongo_password,
                    'authSource': mongo_auth_source,
                })
            client = MongoClient(**client_kwargs)
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
