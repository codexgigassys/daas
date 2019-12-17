from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from .models import Sample, Result


class ResultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    # fixme: add URL to download compressed code

    class Meta:
        model = Result
        fields = ('timeout', 'elapsed_time', 'exit_status', 'status', 'decompiler',
                  'processed_on', 'version')


class SampleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    subfiles = serializers.ListField(write_only=True)

    class Meta:
        model = Sample
        fields = ('md5', 'sha1', 'sha2', 'file_name', 'size', 'uploaded_on', 'file_type',
                  'seaweedfs_file_id', 'subfiles')

    def create(self, validated_data: dict) -> Sample:
        if validated_data['file_type'] == 'zip':
            instance = super().create(validated_data)
        else:
            for file in validated_data['subfiles']:
                pass
        return instance

class ZipSampleSerializer(serializers.Serializer):
    subfiles = # VER COMO CUERNO SERIALIZAR ESTO BIEN. NO SE SI ES MEJOR USAR UN SERIALIZER O DOS. CON UNO ES MAS FACIL
    # Y SI ES ZIP EL CREATE TIENE Q RETORNAR UN OBJETO PERO QUE ESE OBJETO NO SE PERSISTA. HAY QUE HACER UN MODELO NO
    # PERSISTENTE (PROXY ES?).