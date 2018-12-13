from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from .models import Sample, Result


class ResultRelatedFieldSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ('timeout', 'elapsed_time', 'exit_status', 'status', 'output', 'zip_result', 'decompiler',
                  'processed_on', 'version')


class SampleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    result = ResultRelatedFieldSerializer()

    class Meta:
        model = Sample
        fields = ('md5', 'sha1', 'sha2', 'name', 'data', 'size', 'uploaded_on', 'file_type')


class SampleWithoutDataSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    result = ResultRelatedFieldSerializer()

    class Meta:
        model = Sample
        fields = ('md5', 'sha1', 'sha2', 'name', 'size', 'uploaded_on', 'file_type')


class ResultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ('timeout', 'elapsed_time', 'exit_status', 'status', 'output', 'zip_result', 'decompiler',
                  'processed_on', 'version', 'sample__md5', 'sample__sha1', 'sample__sha2')
